# B 站全站视频信息

B 站魔性的网站，n多次被本山大叔的改革春风待跑偏了，冲着爬虫来，结果彻底吹凌乱。**纸上得来终觉浅，绝知此事要躬行**。

### 准备工作

打开首页，随便找一个视频点击进去。刚开始我是奔着解析网页去的，抱着正则和xpath就匹配起来了。但是视频链接没有任何规律，改找api，反而容易很多，又不担心反爬。

从链接参数就能看出怎么获取数据了

![bili-0](https://github.com/fenglei110/Data-analysis/blob/master/ch_Bilibili/images/small.png)

找到了 api 的地址
                
![bili-1](https://github.com/fenglei110/Data-analysis/blob/master/ch_Bilibili/images/bin.png)

复制下来整个url，用浏览器打开，会得到如下的 json 数据

![bili-2](https://github.com/fenglei110/Data-analysis/blob/master/ch_Bilibili/images/three.png)

### 代码

为了让爬虫更高效，可以利用多线程。当然现成的scrapy框架也不错，多线程都封装好了，自己需要写很少的代码

#### spider核心代码
```py
    def parse(self, response):
        if response.statue_code == 20:
            text = json.loads(response.text)
            res = text.get('result')
            numpages = text.get('numPages')
            numResults = text.get('numResults')
            msg = text.get('msg')
            if msg == 'success':
                for i in res:
                    author = i.get('author')
                    id = i.get('id')
                    pubdate = i.get('pubdate')
                    favorite = i.get('favorites')
                    rank_sore = i.get('rank_score')
                    video_review = i.get('video_review')
                    tag = i.get('tag')
                    title = i.get('title')
                    arcurl = i.get('arcurl')

                    item = BilibiliItem()
                    item['numResults'] = numResults
                    item['author'] = author
                    item['id'] = id
                    item['pubdate'] = pubdate
                    item['favorite'] = favorite
                    item['rank_sore'] = rank_sore
                    item['video_review'] = video_review
                    item['tag'] = tag
                    item['title'] = title
                    item['arcurl'] = arcurl
                    yield item    
```

#### item代码
```py
class BilibiliItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    numResults = scrapy.Field()  # 总共视频数
    author = scrapy.Field()  # 作者
    id = scrapy.Field()  # 视频id
    pubdate = scrapy.Field()  # 日期
    favorite = scrapy.Field()  # 收藏量
    rank_sore = scrapy.Field()  # 播放量
    video_review = scrapy.Field()  # 弹幕数
    tag = scrapy.Field()  # 标签
    title = scrapy.Field()  # 题目
    arcurl = scrapy.Field()  # 视频链接
```

不要一次性爬取全部链接，我是利用两个进程，这样就是多进程+多线程了，一个进程一次大概爬取 50w 条数据。100w 条数据的话大概一个多小时吧。分多次爬取，分别将数据保存为不同的文件名，最后再汇总。

运行的效果大概是这样的，数字是已经已经爬取了多少条链接，其实完全可以在一天或者两天内就把全站信息爬完的。

![bili-3](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-3.gif)

至于爬取后要怎么处理就看自己爱好了，我是先保存为 csv 文件，然后再汇总插入到数据库。

汇总的 csv 文件

![bili-4](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-4.png)

#### 数据库表

![sql-desc](https://github.com/chenjiandongx/bili-spider/blob/master/images/sql-desc.png)

由于这些内容是我在几个月前爬取的，所以数据其实有些滞后了。

#### 数据总量

![sql-sum](https://github.com/chenjiandongx/bili-spider/blob/master/images/sql-sum.png)

#### 查询播放量前十的视频

![sql-view](https://github.com/chenjiandongx/bili-spider/blob/master/images/sql-view.png)

#### 查询回复量前十的视频

![sql-reply](https://github.com/chenjiandongx/bili-spider/blob/master/images/sql-reply.png)

各种花样查询任君选择！！视频的链接为 https://www.bilibili.com/video/av + v_aid

#### 详细代码请移步至 [bili.py](https://github.com/chenjiandongx/bili-spider/blob/master/bili.py)

对数据感兴趣的话可以邮箱联系我，可以打包赠与。
