布隆过滤器是通过写文件的方式，多进程使用需要添加同步和互斥，较为繁琐，不推荐多线程/多进程时候使用，另外写文件耗费时间长，可以累积一次性写入，过着利用上下文管理器推出时写入。
```python
import os
import json

class Spider(object):
    def __init__(self):
    # 布隆过滤器初始化
        self.bulongname = 'test.bl'
        if not os.path.isfile(self.bulongname):
            self.bl = BloomFilter(capacity=100000, error_rate=0.00001)
        else:
            with open(self.bulongname, 'rb') as f:
                self.bl = BloomFilter.fromfile(f)
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, *args):
        """
        上下文管理器退出入口
        """
        if self.conn is not None:
            self.conn.close()
        with open(self.bulongname, 'wb') as f:
            self.fingerprints.tofile(f)
    
    def get_info(self):
        """
        抓取主函数
        """
        x = json.dumps(" ")
        if x not in self.bl:
            self.bl.add(x)

if __name__ == '__main__':
    with Spider() as S:
        S.get_info()

```

redis 集合去重能够支持多线程和多进程
步骤：
1. 建立连接池
2. 重复检查

```python
import os
import sys
import hashlib
import redis

def redis_init():
    pool = redis.ConnectionPool(host=host, port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    return pool, r
    
def redis_close(pool):
    """
    释放连接池
    """
    pool.disconnct()
    
def sha1(x):
    sha1obj = hashlib.sha1()
    sha1obj.update(x)
    hash_value = sha1obj.hexdigest()
    return hash_value
    
def check_repeate(r, check_str, set_name):
    """
    向redis集合中添加元素，重复返回0, 不重复则添加，返回1
    """
    hash_value = sha1(check_str)
    result = r.sadd(set_name, hash_value)
    return result

def main():
    pool, r= redis_init()
    temp_str = 'aaaaaa'
    result = check_repeate(r, temp_str, 'test:test')
    if result == 0:
        # TODO
        print('重复')
    else:
        # TODO
        print('不重复')
    redis_close(pool)
    

if __name__ == '__main__':
    main()

```