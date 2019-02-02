# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HaiwangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    nickName = scrapy.Field()  # 昵称
    cityName = scrapy.Field()  # 城市
    content = scrapy.Field()  # 评论
    score = scrapy.Field()  # 评分
    startTime = scrapy.Field()  # 评论时间
    approve = scrapy.Field()  #
    reply = scrapy.Field()  # reply num
    avatarurl = scrapy.Field()  # image url
