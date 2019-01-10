# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import os
import pymongo
from Spider.settings import MONGO_DBNAME, MONGO_HOST, MONGO_PORT, MONGO_SHEETNAME


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class HaiwangPipeline(object):
    def __init__(self):
        store_file = os.path.dirname(__file__) + '/spiders/haiwang.csv'
        print(store_file)
        self.file = open(store_file, "a+", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)

    def process_item(self, item, spider):
        try:
            self.writer.writerow((
                item["nickName"],
                item["cityName"],
                item["content"],
                item["approve"],
                item["reply"],
                item["startTime"],
                item["avatarurl"],
                item["score"]
            ))

        except Exception as e:
            print(e.args)

    def close_spider(self, spider):
        self.file.close()


class MongoPipline(object):
    def __init__(self):
        host = MONGO_HOST
        port = MONGO_PORT
        dbname = MONGO_DBNAME
        sheetname = MONGO_SHEETNAME

        client = pymongo.MongoClient(host=host, port=port)
        # 得到数据库对象
        mydb = client[dbname]
        # 得到表对象
        self.table = mydb[sheetname]

    def process_item(self, item, spider):
        dict_item = dict(item)
        self.table.insert(dict_item)
        return item

    def close_spider(self, spider):
        print("close spider....")