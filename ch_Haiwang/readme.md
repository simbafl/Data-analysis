# 猫眼爬取《海王》的评论信息

### 准备工作

准备虚拟环境

下载Fiddler抓包工具，前提是手机和电脑在同一局域网内，具体教程自行百度吧。

从猫眼寻找api规律，获取json数据

基本开始的链接为：`url = 'http://m.maoyan.com/mmdb/comments/movie/249342.json?_v_=yes&offset=0&startTime=0'`


#### 步骤
```md
    source venv3.5/bin/activate
    scrapy startproject Spider
    cd Spider
    scrapy genspider Haiwang m.maoyan.com
```
#### 代码 中间建设置
##### User-Agent动态设置. 下载`fake_useragent`插件, 维护的比较完善
##### 维护ip代理池, ip具体操作查看tools目录. `github`上也有人写了比较完善的`scrapy-proxy`, 功能比较齐全, 自我感觉不好用
```py
    class RandomUserAgentMiddleware(object):
    # 随机切换user-agent
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault('User-Agent', get_ua())
        
    class RandomProxyMiddleware(object):
    # 动态ip设置
    def process_request(self, request, spider):
        get_ip = GetIp()
        request.meta['proxy'] = get_ip.get_random_ip()
```

至于爬取后要怎么处理就看自己爱好了，我是先保存为 csv 文件，然后再汇总插入到mongodb，毕竟文件存储有限。


#### 评分占比, 看得出来大部分给了5分好评

![1-view](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/1.png)

#### 评分人数占比

![2-view](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/2.png)

#### 平均发布时间占比, 绝大数还是12点左右发布得, 凌晨5点人数最少, 符合常情

![chart-line](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/chart_line.png)

#### 评论词云图

![ciyun](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/ciyun.png)

#### 观众分布

![geo](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/geo.png)

`为了这几个图煞费苦心, 还是不完美` :+1::+1::+1:


对数据感兴趣的话可以邮箱联系我，共同进步。
