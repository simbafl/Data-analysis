负责执行requst的去重，实现的很有技巧性，使用redis的set数据结构。但是注意scheduler并不使用其中用于在这个模块中实现的dupefilter键做request的调度，而是使用queue.py模块中实现的queue。
当request不重复时，将其存入到queue中，调度时将其弹出。

import logging
import time
from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint
from . import defaults
from .connection import get_redis_from_settings


logger = logging.getLogger(__name__)


# TODO: Rename class to RedisDupeFilter.
class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplicates filter.

    This class can also be used with default Scrapy's scheduler.

    """

    logger = logger

    def __init__(self, server, key, debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = server
        self.key = key
        self.debug = debug
        self.logdupes = True

    @classmethod
    def from_settings(cls, settings):
        """Returns an instance from given settings.

        This uses by default the key ``dupefilter:<timestamp>``. When using the
        ``scrapy_redis.scheduler.Scheduler`` class, this method is not used as
        it needs to pass the spider name in the key.

        Parameters
        ----------
        settings : scrapy.settings.Settings

        Returns
        -------
        RFPDupeFilter
            A RFPDupeFilter instance.


        """
        server = get_redis_from_settings(settings)
        # XXX: This creates one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        # TODO: Use SCRAPY_JOB env as default and fallback to timestamp.
        key = defaults.DUPEFILTER_KEY % {'timestamp': int(time.time())}
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(server, key=key, debug=debug)

    @classmethod
    def from_crawler(cls, crawler):
        """Returns instance from crawler.

        Parameters
        ----------
        crawler : scrapy.crawler.Crawler

        Returns
        -------
        RFPDupeFilter
            Instance of RFPDupeFilter.

        """
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        fp = self.request_fingerprint(request)
        # This returns the number of values added, zero if already exists.
        added = self.server.sadd(self.key, fp)
        return added == 0

    def request_fingerprint(self, request):
        """Returns a fingerprint for a given request.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        str

        """
        return request_fingerprint(request)

    def close(self, reason=''):
        """Delete data on close. Called by Scrapy's scheduler.

        Parameters
        ----------
        reason : str, optional

        """
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

    def log(self, request, spider):
        """Logs given request.

        Parameters
        ----------
        request : scrapy.http.Request
        spider : scrapy.spiders.Spider

        """
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False
这个文件看起来比较复杂，重写了scrapy本身已经实现的request判重功能。因为本身scrapy单机跑的话，只需要读取内存中的request队列或者持久化的request队列（scrapy默认的持久化似乎是json格式的文件，不是数据库）就能判断这次要发出的request url是否已经请求过或者正在调度（本地读就行了）。而分布式跑的话，就需要各个主机上的scheduler都连接同一个数据库的同一个request池来判断这次的请求是否是重复的了。
在这个文件中，通过继承BaseDupeFilter重写他的方法，实现了基于redis的判重。根据源代码来看，scrapy-redis使用了scrapy本身的一个fingerprint接request_fingerprint，这个接口很有趣，根据scrapy文档所说，他通过hash来判断两个url是否相同（相同的url会生成相同的hash结果），但是当两个url的地址相同，get型参数相同但是顺序不同时，也会生成相同的hash结果（这个真的比较神奇。。。）所以scrapy-redis依旧使用url的fingerprint来判断request请求是否已经出现过。
这个类通过连接redis，使用一个key来向redis的一个set中插入fingerprint（这个key对于同一种spider是相同的，redis是一个key-value的数据库，如果key是相同的，访问到的值就是相同的，这里使用spider名字+DupeFilter的key就是为了在不同主机上的不同爬虫实例，只要属于同一种spider，就会访问到同一个set，而这个set就是他们的url判重池），如果返回值为0，说明该set中该fingerprint已经存在（因为集合是没有重复值的），则返回False，如果返回值为1，说明添加了一个fingerprint到set中，则说明这个request没有重复，于是返回True，还顺便把新fingerprint加入到数据库中了。 DupeFilter判重会在scheduler类中用到，每一个request在进入调度之前都要进行判重，如果重复就不需要参加调度，直接舍弃就好了，不然就是白白浪费资源。