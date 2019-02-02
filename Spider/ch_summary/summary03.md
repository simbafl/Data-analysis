### 爬虫高效率
爬虫的本质就是一个socket客户端与服务端的通信过程，如果我们有多个url待爬取，只用一个线程且采用串行的方式执行，
那只能等待爬取一个结束后才能继续下一个，效率会非常低。需要强调的是：对于单线程下串行N个任务，并不完全等同于低效。

如果这N个任务都是纯计算的任务，那么该线程对cpu的利用率仍然会很高，之所以单线程下串行多个爬虫任务低效， 是因为爬虫任务是明显的IO密集型程序。

---
#### 一、同步、异步、回调机制

1、同步调用：即提交一个任务后就在原地等待任务结束，等到拿到任务的结果后再继续下一行代码，效率低下
```python
import requests

def parse_page(res):
    print('解析 %s' %(len(res)))

def get_page(url):
    print('下载 %s' % url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text

urls=['https://www.baidu.com/','http://www.sina.com.cn/','https://www.python.org']
for url in urls:
    res = get_page(url)  # 调用一个任务，就在原地等待任务结束拿到结果后才继续往后执行
    parse_page(res)
```
2、一个简单的解决方案：多线程或多进程

在服务器端使用多线程（或多进程）。  
多线程（或多进程）的目的是让每个连接都拥有独立的线程（或进程），这样任何一个连接的阻塞都不会影响其他的连接。
```python
#IO密集型程序应该用多线程
import requests
from threading import Thread, current_thread

def parse_page(res):
    print('%s 解析 %s' %(current_thread().getName(),len(res)))
 

def get_page(url, callback=parse_page):
    print('%s 下载 %s' %(current_thread().getName(),url))
    response = requests.get(url)
    if response.status_code == 200:
        callback(response.text)


if __name__ == '__main__':
    urls=['https://www.baidu.com/','http://www.sina.com.cn/','https://www.python.org']
    for url in urls:
        t=Thread(target=get_page,args=(url,))
        t.start()
```
该方案的问题是：  
开启多进程或都线程的方式，我们是无法无限制地开启多进程或多线程的：在遇到要同时响应成百上千路的连接请求，则无论多线程还是多进程都会严重占据系统资源，降低系统对外界响应效率，
而且线程与进程本身也更容易进入假死状态。

3、改进方案：

线程池或进程池+异步调用：提交一个任务后并不会等待任务结束，而是继续下一行代码。很多程序员可能会考虑使用`'线程池'`或`'连接池'`。  
`'线程池'`旨在减少创建和销毁线程的频率，其维持一定合理数量的线程，并让空闲的线程重新承担新的执行任务。`'连接池'`维持连接的缓存池，尽量重用已有的连接、减少创建和关闭连接的频率。这两种技术都可以很好的降低系统开销，都被广泛应用很多大型系统，如Nginx、tomcat和各种数据库等。
```python
# IO密集型程序应该用多线程，我们使用线程池

import requests
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def parse_page(res):
    res=res.result()
    print('%s 解析 %s' %(current_thread().getName(),len(res)))

def get_page(url):
    print('%s 下载 %s' %(current_thread().getName(),url))
    response=requests.get(url)
    if response.status_code == 200:
        return response.text


if __name__ == '__main__':
    urls=['https://www.baidu.com/', 'http://www.sina.com.cn/', 'https://www.python.org']
    pool = ThreadPoolExecutor(50)
    # pool = ProcessPoolExecutor(50)
    for url in urls:
        pool.submit(get_page,url).add_done_callback(parse_page)
    pool.shutdown(wait=True)
```
改进后方案其实也存在着问题：

`'线程池'`和`'连接池'`技术也只是在一定程度上缓解了频繁调用IO接口带来的资源占用。而且，所谓`'池'`始终有其上限，当请求大大超过上限时，`'池'`构成的系统对外界的响应并不比没有池的时候效果好多少。所以使用`'池'`必须考虑其面临的响应规模，并根据响应规模调整'池'的大小。

对应上例中的所面临的可能同时出现的上千甚至上万次的客户端请求，`'线程池'`或`'连接池'`或许可以缓解部分压力，但是不能解决所有问题。

总之，多线程模型可以方便高效的解决小规模的服务请求，但面对大规模的服务请求，多线程模型也会遇到瓶颈，可以用非阻塞接口来尝试解决这个问题。

#### 二、高性能

上述无论哪种解决方案其实没有解决一个性能相关的问题：IO阻塞。无论是多进程还是多线程，在遇到IO阻塞时都会被操作系统强行剥夺走CPU的执行权限，程序的执行效率因此就降低了下来。

解决这一问题的关键在于，我们自己从应用程序级别检测IO阻塞，然后切换到我们自己程序的其他任务执行，这样把我们程序的IO降到最低，我们的程序处于就绪态就会增多，以此来迷惑操作系统，操作系统便以为我们的程序是IO比较少的程序，从而会尽可能多的分配CPU给我们，这样也就达到了提升程序执行效率的目的。

1、在python3.3之后新增了asyncio模块，可以帮我们检测IO（只能是网络IO），实现应用程序级别的切换。
```python
import asyncio


@asyncio.coroutine
def task(task_id,senconds):
    print('%s is start' %task_id)
    yield from asyncio.sleep(senconds) #只能检测网络IO,检测到IO后切换到其他任务执行
    print('%s is end' %task_id)

tasks = [task(task_id='任务1', senconds=3), task('任务2',2), task(task_id='任务3', senconds=1)]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
```
2、但asyncio模块只能发tcp级别的请求，不能发http协议，因此，在我们需要发送http请求的时候，需要我们自定义http报头。
```python
import asyncio
import uuid

user_agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'


def parse_page(host,res):
    print('%s 解析结果 %s' %(host,len(res)))
    with open('%s.html' %(uuid.uuid1()),'wb') as f:
        f.write(res)

@asyncio.coroutine
def get_page(host, port=80, url='/', callback=parse_page, ssl=False):
    print('下载 http://%s:%s%s' %(host,port,url))
    #步骤一（IO阻塞）：发起tcp链接，是阻塞操作，因此需要yield from
    if ssl:
        port = 443
    recv, send = yield from asyncio.open_connection(host=host, port=port, ssl=ssl)

    # 步骤二：封装http协议的报头，因为asyncio模块只能封装并发送tcp包，因此这一步需要我们自己封装http协议的包
    request_headers = '''GET %s HTTP/1.0rnHost: %srnUser-agent: %srnrn''' %(url,host,user_agent)
    # requset_headers = '''POST %s HTTP/1.0rnHost: %srnrnname=egon&password=123''' % (url, host,)
    request_headers=request_headers.encode('utf-8')

    # 步骤三（IO阻塞）：发送http请求包
    send.write(request_headers)
    yield from send.drain()

    # 步骤四（IO阻塞）：接收响应头
    while True:
        line = yield from recv.readline()
        if line == b'rn':
            break

        print('%s Response headers：%s' %(host,line))
        
    # 步骤五（IO阻塞）：接收响应体
    text = yield from recv.read()

    # 步骤六：执行回调函数
    callback(host, text)

    # 步骤七：关闭套接字
    send.close()  # 没有recv.close()方法，因为是四次挥手断链接，双向链接的两端，一端发完数据后执行send.close()另外一端就被动地断开


if __name__ == '__main__':
    tasks = [
        get_page('www.baidu.com', url='/s?wd=美女', ssl=True),
        get_page('www.cnblogs.com', url='/', ssl=True),
    ]


    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
```
3、自定义http报头多少有点麻烦，于是有了aiohttp模块，专门帮我们封装http报头，然后我们还需要用asyncio检测IO实现切换。

```python
import aiohttp
import asyncio


@asyncio.coroutine
def get_page(url):
    print('GET:%s' %url)
    response = yield from aiohttp.request('GET',url)
    data = yield from response.read()
    print(url, data)
    response.close()
    return 1

tasks=[
    get_page('https://www.python.org/doc'),
    get_page('https://www.baidu.com'),
    get_page('https://www.openstack.org')
]

loop = asyncio.get_event_loop()
results = loop.run_until_complete(asyncio.gather(*tasks))
loop.close()

print('=====>',results)  # [1, 1, 1]
```
4、此外，还可以将requests.get函数传给asyncio，就能够被检测了。
```python
import requests
import asyncio


@asyncio.coroutine
def get_page(func, *args):
    print('GET:%s' % args[0])
    loop = asyncio.get_event_loop()
    furture = loop.run_in_executor(None, func, *args)
    response = yield from furture
    print(response.url, len(response.text))
    return 1


tasks=[
    get_page(requests.get, 'https://www.python.org/doc'),
    get_page(requests.get, 'https://www.baidu.com'),
    get_page(requests.get, 'https://www.openstack.org')
]

loop = asyncio.get_event_loop()
results = loop.run_until_complete(asyncio.gather(*tasks))
loop.close()

print('=====>',results)  # [1, 1, 1]
```
5、还有之前在协程时介绍的gevent模块
```python
from gevent import monkey; monkey.patch_all()
import gevent
import requests


def get_page(url):
    print('GET:%s' % url)
    response = requests.get(url)
    print(url, len(response.text))
    return 1


# g1=gevent.spawn(get_page,'https://www.python.org/doc')
# g2=gevent.spawn(get_page,'https://www.cnblogs.com/linhaifeng')
# g3=gevent.spawn(get_page,'https://www.openstack.org')
# gevent.joinall([g1,g2,g3,])
# print(g1.value,g2.value,g3.value)  # 拿到返回值


#协程池
from gevent.pool import Pool

pool = Pool(2)
g1 = pool.spawn(get_page, 'https://www.python.org/doc')
g2 = pool.spawn(get_page, 'https://www.cnblogs.com/linhaifeng')
g3 = pool.spawn(get_page, 'https://www.openstack.org')
gevent.joinall([g1, g2, g3,])
print(g1.value, g2.value, g3.value)  # 拿到返回值
```
6、封装了gevent+requests模块的grequests模块
```python
#pip3 install grequests
import grequests


request_list=[
    grequests.get('https://wwww.xxxx.org/doc1'),
    grequests.get('https://www.cnblogs.com/linhaifeng'),
    grequests.get('https://www.openstack.org')
]

##### 执行并获取响应列表 #####

# response_list = grequests.map(request_list)
# print(response_list)

##### 执行并获取响应列表（处理异常） #####

def exception_handler(request, exception):
    # print(request,exception)
    print('%s Request failed' % request.url)

response_list = grequests.map(request_list, exception_handler=exception_handler)
print(response_list)
```
7、twisted：是一个网络框架，其中一个功能是发送异步请求，检测IO并自动切换，但是本人用的并不多。
```
问题一：error: Microsoft Visual C++ 14.0 is required. Get it with 'Microsoft Visual C++ Build Tools': http://landinghub.visualstudio.com/visual-cpp-build-tools

https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted

pip3 install C:UsersAdministratorDownloadsTwisted-17.9.0-cp36-cp36m-win_amd64.whl
pip3 install twisted


问题二：ModuleNotFoundError: No module named 'win32api'
https://sourceforge.net/projects/pywin32/files/pywin32/


问题三：openssl
pip3 install pyopenssl

```

```python
# twisted基本用法

from twisted.web.client import getPage,defer
from twisted.internet import reactor

def all_done(arg):
    # print(arg)
    reactor.stop()

def callback(res):
    print(res)
    return 1

defer_list = []
urls = [
    'http://www.baidu.com',
    'http://www.bing.com',
    'https://www.python.org',
]

for url in urls:
    obj = getPage(url.encode('utf=-8'),)
    obj.addCallback(callback)
    defer_list.append(obj)
   
defer.DeferredList(defer_list).addBoth(all_done)
reactor.run()


# twisted的getPage的详细用法
from twisted.internet import reactor
from twisted.web.client import getPage
import urllib.parse

def one_done(arg):
    print(arg)
    reactor.stop()

post_data = urllib.parse.urlencode({'check_data': 'adf'})
post_data = bytes(post_data, encoding='utf8')
headers = {b'Content-Type': b'application/x-www-form-urlencoded'}
response = getPage(bytes('http://dig.chouti.com/login', encoding='utf8'),
                  method=bytes('POST', encoding='utf8'),
                  postdata=post_data,
                  cookies={},
                  headers=headers)
response.addBoth(one_done)
reactor.run()
```
8、tornado最常用的一个异步网络框架
```python
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import ioloop


def handle_response(response):
    '''
    处理返回值内容（需要维护计数器，来停止IO循环），调用 ioloop.IOLoop.current().stop()
    :param response:
    :return:
    '''
    if response.error:
        print('Error:', response.error)
    else:
        print(response.body)


def func():
    url_list = [
        'http://www.baidu.com',
        'http://www.bing.com',
    ]

    for url in url_list:
        print(url)
        http_client = AsyncHTTPClient()
        http_client.fetch(HTTPRequest(url), handle_response)

ioloop.IOLoop.current().add_callback(func)
ioloop.IOLoop.current().start()
```
发现上例在所有任务都完毕后也不能正常结束，为了解决该问题，让我们来加上计数器。
```python
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado import ioloop


count=0

def handle_response(response):
    """
    处理返回值内容（需要维护计数器，来停止IO循环），调用 ioloop.IOLoop.current().stop()
    :param response:
    :return:
    """
    if response.error:
        print('Error:', response.error)
    else:
        print(len(response.body))

    global count
    count-=1 #完成一次回调，计数减1

    if count == 0:
        ioloop.IOLoop.current().stop()

def func():
    url_list = [
       'http://www.baidu.com',
       'http://www.bing.com',
    ]

    global count
    for url in url_list:
        print(url)
        http_client = AsyncHTTPClient()
        http_client.fetch(HTTPRequest(url), handle_response)
        count+=1  # 计数加1

ioloop.IOLoop.current().add_callback(func)
ioloop.IOLoop.current().start()
```

9. celery同样是python的一个非常好用的异步框架，功能强大，内部封装了多线程。 本人之前使用selenium和phantomjs比较频繁，但是相对很慢，配合celery大大提高了效率，有兴趣可以看celery官网。