## url去重

### 去重方案
- 关系数据库去重

例如将url保存到MySQL，每遇到一个url就启动一次查询，数据量大时，效率低

- 缓存数据库去重

Redis，使用其中的Set数据类型，可将内存中的数据持久化，应用广泛

- 内存去重

将url直接保存到HashSet中，也就是python的set，这种方式也很耗内存。进一步将url经过MD5或SHA-1等哈希算法生成摘要，再存到HashSet中。MD5处理后摘要长度128位，32个字符，SHA-1摘要长度160位，这样占内存要小很多。  
或者采用Bit-Map方法，建立一个BitSet，每一个url经过一个哈希函数映射到第一位，内存消耗最少，但是会发生冲突，长生误判。  
最后就是BloomFilter，对Bit-Map的扩展。  

**综上，比较好的方法为：url经过MD5或SHA-1加密，然后结合缓存数据库，基本满足大多数中型爬虫需要。数据量上亿或者几十亿时，用BloomFilter了。**

#### scrapy-redis当中的去重
```python
class RFPDupeFilter(BaseDuperFilter):
    def __init__(self, path=None, debug=False):
        self.fingerprints = set()
        ...
        
    def request_fingerprint(self, include_headers=None):
        if include_headers:
            include_headers = tuple(to_bytes(h.lower() for h in sorted(include_headers)))
            cache = _fingerprint_cache.setdefault(request, {})
        
        if include_headers not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(request.method))
            fp.update(to_bytes(canonicalize_url(request.url)))
            fp.update(request,body or b'')
            
        if include_headers:
            for hdr in include_headers:
                if hdr in request.headers:
                    fp.update(hdr)
                    for v in request.headers.getlist(hdr):
                        fp.update(v)
                        
        cache[include_headers] = fp.hexdigest()
        return cache[include_headers]

```
可以发现，PFPDuperFilter类中初始化默认采用redis的set()方法  
request_fingerprint方法中，去重指纹是sha1(method + url + body + header)，所以实际能够去掉重复的比例并不大。  
我们可以自定义使用url做指纹去重：
```python
class SeenURLFilter(RFPDuperFilter):
    """A dupe filter that contains the URl"""
    def __init__(self, path=None):
        self.urls_seen = set()
        RFPDuperFilter.__init__(self, path)
    
    def request_seen(self, request):
        if request.url in self.urls_seen:
            return True
        else:
            self.urls_seen.add(request.url)
```
#### 去重原理
1. set方法的去重
```python
class Foo:
    def __init__(self, name, count):
        self.count = count
        self.name = name
    
    def __hash__(self):
        return hash(self.count)
        
    def __eq__(self, other):
        print(self.__dict__, other.__dict__)
        return self.__dict__ == other.__dict__
        
```
  python中的set去重会调用__hash__这个魔法方法，如果传入的变量不可哈希，会直接抛出异常，如果返回哈希值相同，又会调用__eq__这个魔法方法。
所以，set去重是通过__hash__和__eq__结合实现的。

2. set 去重效率

   python的去重优点是去重速度快，但要将去重的对象同时加载到内存，然后进行比较判断，返回去重后的集合对象，虽然底层也是哈希后来判断，但还是比较耗内存，而且set方法并不是判断元素是否存在的方式。

   我们可以利用redis的缓存数据库当中的set类型，来判断元素是否存在集合中的方式，它的底层实现原理与python的set类似。Redis的set类型有sadd()方法与sismember()方法，如果redis当中不存在这条记录sadd则添加进去，simember返回False。如果存在，sadd不填加，sismember返回True。 接下来计算一下：  
    1GB=1024MB=1024×1024KB=1024×1024×1024Bit，不考虑哈希冲突情况下，1024×1024×1024Bit/32=33554432条，1G内存可以去重3300万条记录;考虑到哈希表存储效率通常小于50%，1G内存可以去重1600多万条记录。因此达到亿级别的数据，就得采用布隆过滤器了。

3. 布隆过滤器 
   具体实现百度吧，说说要点：
   1. 一个很长的二进制向量(位数组)
   2. 一系列随机函数(哈希)
   3. 空间效率和查询效率高
   4. 有一定误判率(哈希表是精确匹配)
   5. 广泛用于拼写检查，网络去重和数据库系统中
