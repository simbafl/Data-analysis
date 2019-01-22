## 分布式爬虫

#### 分布式爬虫的优点

1. 充分利用多机器的带宽加速爬取
2. 充分利用多机的ip加速爬取速度

#### 分布式爬虫需要解决的问题

1. request队列集中管理
2. 去重集中管理

#### scrapy不支持分布式，结合redis的特性自然而然产生了scrapy-redis

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