# B 站爬取视频信息
一个魔性网站，n多次被鬼畜视频带跑了，尤其最近本山大叔的改革春风，彻底是把我吹狂乱了，时刻提醒自己我是来爬虫的...

### 准备工作

`scrapy`  `python3.5`

寻找api规律，获取json数据

基本开始的链接为：`url = 'https://s.search.bilibili.com/cate/search?main_ver=v3&search_type=video&view_type=hot_rank&pic_size=160x100&order=click&copy_right=-1&cate_id=1&page=1&pagesize=20&time_from=20181201&time_to=20190109'`

`cate_id`可以从网页中正则匹配到，闲麻烦就直接从1遍历到200了，基本就这范围。

 如果想爬更多数据，`page` `time`都可以自行设置。

#### spider代码
```py
    def parse(self, response):
        if response:
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
                    rank_score = i.get('rank_score')
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
                    item['rank_score'] = rank_score
                    item['video_review'] = video_review
                    item['tag'] = tag
                    item['title'] = title
                    item['arcurl'] = arcurl
                    yield item
    
```
![bili-1](https://github.com/fenglei110/Data-analysis/blob/master/Spider/ch_Bilibili/images/big.png)

![bili-2](https://github.com/fenglei110/Data-analysis/blob/master/Spider/ch_Bilibili/images/small.png)

![bili-3](https://github.com/fenglei110/Data-analysis/blob/master/Spider/ch_Bilibili/images/three.png)

至于爬取后要怎么处理就看自己爱好了，最好保存为 csv 文件，方便pandas处理


Bilibili视频的链接为 `https://www.bilibili.com/video/av + v_aid`

对数据感兴趣的话可以邮箱联系我，共同进步。
