# -*- coding: utf-8 -*-
import scrapy
import json

from Spider.items import HaiwangItem


class HaiwangSpider(scrapy.Spider):
    name = 'Haiwang'
    allowed_domains = ['m.maoyan.com']
    start_urls = ['http://m.maoyan.com/mmdb/comments/movie/249342.json?_v_=yes&offset=0&startTime=0']

    def parse(self, response):
        print(response.url)
        data = json.loads(response.text)
        print(data)
        item = HaiwangItem()
        for info in data["cmts"]:
            item["nickName"] = info["nickName"]
            item["cityName"] = info["cityName"] if "cityName" in info else ""
            item["content"] = info["content"]
            item["score"] = info["score"]
            item["startTime"] = info["startTime"]
            item["approve"] = info["approve"]
            item["reply"] = info["reply"]
            item["avatarurl"] = info["avatarurl"]
            print(item)
            yield item

        yield scrapy.Request("http://m.maoyan.com/mmdb/comments/movie/249342.json?_v_=yes&offset=0&startTime={}".
                             format(item["startTime"]), callback=self.parse)


