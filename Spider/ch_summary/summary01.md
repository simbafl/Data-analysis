## scrapy 如何中断续爬

1. scrapy简单易用，效率极高，自带多线程机制。但也正是因为多线程机制导致在用scrapy写爬虫的时候处理断点续爬很恼火。当你用for循环遍历一个网站的所有页面的时候,例如：

如果这个网站有10000页，启动scrapy后程序第一个发送的请求可能就是第10000页,然后第二个请求可能就是第1页。当程序跑到一半断掉的时候天知道有哪些页是爬过的。不过针对这个问题也不是没有解决办法。
```python
totalpages = 10000
for i in range(totalpages):
    url = '****page' + str(i)
    yield Request(url=url, callback=self.next)
```
2. 总之我们要想保证爬取数据的完整就要牺牲程序的效率。

- 有的人把所有爬取过的url列表保存到一个文件当中，然后再次启动的时候每次爬取要和文件当中的url列表对比，如果相同则不再爬取。
- 有的人在scrapy再次启动爬取的时候和数据库里面的数据做对比，如果相同则不存取。
- 还有一种办法呢就是利用Request中的优先级（priority）

前两种方法就不详细说了，通俗易懂。主要说一下这个优先级。修改上面的代码
```python
totalpages = 10000
def first(self, response):
    for i in range(totalpages):
        url = '****page' + str(i)
        priority = totalpages-i
        yield Request(url=url, 
                      periority=priority, 
                      callback=self.next)
```

3. 当Request中加入了priority属性的时候，每次scrapy从请求队列中取请求的时候就会判断优先级，先取出优先级高的去访问。由于scrapy默认启动16个线程。这时优先级为100 的就会在优先级为90之前被取出请求队列，这样呢我们就能大体上保证爬取网页的顺序性。

保证了顺序性之后呢，我们就要记录已经爬取的页数。由于发送请求，下载页面，存取数据这几个动作是顺序执行的，也就是说程序发送了这个请求不代表此时已经爬取到这一页了，只有当收到response的时候我们才能确定我们已经获取到了数据，这时我们才能记录爬取位置。完整的代码应该是这样的：
```python
with open('filename', 'r+') as f:  # 程序开始我们要读取上次程序断掉时候的爬取位置
    page = int(f.read()) - 20  # 毕竟多线程，防止小范围乱序，保证数据的完整性 
totalpages = 10000

def first(self, response):
    for i in range(self.page, totalpages):
        url = '****page' + str(i)
        priority = totalpages - i  # 优先级从高到低
        yield Request(url=url, 
                      meta={'page': 1},  # 把page传到下一页 
                      priority=priority,  # 设置优先级
                      callback=self.next())  # 回调下一个函数

def next(self, response):
    with open('filename', 'wb') as f:  # 请求成功保存当前page
        f.write(response.meta['page'])

```