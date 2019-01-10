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


![haiwang-3](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/list.png)

至于爬取后要怎么处理就看自己爱好了，我是先保存为 csv 文件，然后再汇总插入到mongodb，毕竟文件存储有限。

#### 汇总的 csv 文件

![csv-desc](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/csv.png)

#### 数据库表

![sql-desc](https://github.com/fenglei110/Data-analysis/blob/master/ch_Haiwang/images/mongo.png)


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
