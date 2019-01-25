## 分布式爬虫

#### 分布式爬虫的优点

1. 充分利用多机器的带宽加速爬取
2. 充分利用多机的ip加速爬取速度

#### 分布式爬虫需要解决的问题

1. request队列集中管理
2. 去重集中管理

#### scrapy不支持分布式，结合redis的特性自然而然产生了scrapy-redis，下面是scrapy-redis核心代码的梳理。
- [<font size=+1>Spider</font>](./Spider.py)
- [<font size=+1>Scheduler</font>](./Scheduler.py)
- [<font size=+1>Queue</font>](./Queue.py)
- [<font size=+1>Pipelines</font>](./Pipelines.py)
- [<font size=+1>picklecompat</font>](./picklecompat.py)
- [<font size=+1>Duperfilter</font>](./Duperfilter.py)
- [<font size=+1>Connection</font>](./Connection.py)

对于分布式爬虫案例就不写了，随便搜搜就好多，比如说新浪，页面结构算是比较复杂的了，而且反爬挺烦人。时间间隔控制一下，另外需要获取cookie，当然只需静态获取还比较容易，对于动态方式具体操作可以看我的博客。
> [**动态获取cookie**](https://blog.csdn.net/fenglei0415/article/details/81865379)

```md
slave端，拷贝相同的代码，输入同样的运行命令 scrapy runspider demo.py，进入等待
master端，安装redis，在redis_client输入命令 lpush spidername: start_url 就ok了。
```
--- 
最后总结一下scrapy-redis的总体思路：
1. 这个工程通过重写scheduler和spider类，实现了调度、spider启动和redis的交互。
2. 通过实现新的dupefilter和queue类，达到了判重和调度容器和redis的交互，因为每个主机上的爬虫进程都访问同一个redis数据库，所以调度和判重都统一进行统一管理，达到了分布式爬虫的目的。 
3. 当spider被初始化时，同时会初始化一个对应的scheduler对象，这个调度器对象通过读取settings，配置好自己的调度容器queue和判重工具dupefilter。
4. 每当一个spider产出一个request的时候，scrapy内核会把这个reuqest递交给这个spider对应的scheduler对象进行调度，scheduler对象通过访问redis对request进行判重，如果不重复就把他添加进redis中的调度池。当调度条件满足时，scheduler对象就从redis的调度池中取出一个request发送给spider，让他爬取。
5. 当spider爬取的所有暂时可用url之后，scheduler发现这个spider对应的redis的调度池空了，于是触发信号spider_idle，spider收到这个信号之后，直接连接redis读取strart url池，拿去新的一批url入口，然后再次重复上边的工作。

#### redis常用命令:
```md 
# 字符串
set key value  
get key  
getrange key start end  
strlen key  
incr/decr key   
append key value  
```
```md
# 哈希
hset key name value  
hget key  
hexists key fields  
hdel key filds  
hkeys key  
hvals key  
```
```md
# 列表
lpush/rpush mylist value  
lrange mylist 0 10  
blpop/brpop key1 timeout  
lpop/rpop key  
llen key  
lindex key index  
```
```md
# 集合
sadd myset value  
scard key  
sdiff key  
sinter key  
spop key  
smember key member  
```
```md
# 有序集合
zadd myset 0 value  
srangebyscore myset 0 100  
zcount key min max  
```
