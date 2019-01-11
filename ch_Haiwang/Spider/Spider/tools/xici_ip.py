import requests
from scrapy.selector import Selector
import pymysql

conn = pymysql.connect(host="127.0.0.1", user="root", passwd="root", db="ip_spider", charset="utf-8")
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺ip代理
    headers = {"User-Agent": "Mozilla/5.0 Chrome/63.0.3239.26 Mobile Safari/537.36"}
    for i in range(1568):
        re = requests.get("http://www.xicidaili.com/nn/{}".format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []
        speed = None
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, 'HTTP')".format(
                    ip_info[0], ip_info[1], ip_info[3]
                )
            )
            conn.commit()


class GetIp(object):
    def judge_ip(self, ip, port):
        http_url = "http://baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http:": proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)

        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if 300 > code >= 200:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)

    def delete_ip(self, ip):
        # mysql中删除无效的ip
        sql = """delete from proxy_ip where ip='{0}'""".format(ip)
        cursor.execute(sql)
        conn.commit()
        return True

    def get_random_ip(self):
        # 随机取出一个可用ip
        sql = """SELECT ip, port FROM proxy_ip ORDER BY RAND() LIMIT 1"""
        result = cursor.execute(sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == '__main__':
    IP = GetIp()
    IP.get_random_ip()