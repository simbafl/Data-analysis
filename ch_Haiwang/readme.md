# 猫眼爬取《海王》的评论信息

### 准备工作

准备虚拟环境

下载Fiddler抓包工具，前提是手机和电脑在同一局域网内，具体教程自行百度吧。

从猫眼寻找api规律，获取json数据

基本开始的链接为：url = 'http://m.maoyan.com/mmdb/comments/movie/249342.json?_v_=yes&offset=0&startTime=0'


#### 步骤
```md
    source venv3.5/bin/activate
    scrapy startproject Spider
    cd Spider
    scrapy genspider Haiwang m.maoyan.com
```


![bili-3](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-3.gif)

至于爬取后要怎么处理就看自己爱好了，我是先保存为 csv 文件，然后再汇总插入到mongodb，毕竟数据量不小，文件放不下。

汇总的 csv 文件

![bili-4]()

#### 数据库表

![sql-desc]()

由于这些内容是我在几个月前爬取的，所以数据其实有些滞后了。



#### 查询播放量前十的视频

![sql-view]()

#### 查询回复量前十的视频

![sql-reply]()

视频的链接为 `https://www.bilibili.com/video/av + v_aid`


对数据感兴趣的话可以邮箱联系我，共同进步。
