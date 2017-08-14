# coding=utf-8
import databaseConfig
import threading
import requests
import re
import apiCall
import time
import datetime
import hashlib
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class appleDailyTw():
    def __init__(self, url):
        # super(appleDailyTw, self).__init__()
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        # self.createdDate = createdDate
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'http://www.appledaily.com.tw/'
        }

    # def run(self):
    #
    #     r = requests.get(self.url,headers=self.headers)
    #     soup = BeautifulSoup(r.content, "lxml")
    #     items = soup.findAll("article",{"nclns eclnms5"})
    #     for _item in items:
    #         section =  _item.h2.text
    #         if section == "要聞" or section == "社會" or section =="頭條":
    #             for new in _item.findAll("li"):
    #                 detailUrl = "http://www.appledaily.com.tw"+ new.a.get("href")
    #                 self.detail(detailUrl,"news")
    #         if section == "地方綜合":
    #             for new in _item.findAll("li"):
    #                 if new.text == "今天我最美":
    #                     detailUrl = "http://www.appledaily.com.tw"+ new.a.get("href")
    #                     self.detail(detailUrl,"adult")

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            detailUrl = _item.link.text
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1", {"id": "h1"}).text
        token = hashlib.sha256(detailUrl).hexdigest()
        rawContent = soup.find("div", {"class", "articulum trans"}).findAll("p")

        query = "SELECT count(*) FROM crawler.feeds where token=%s;"
        cursor = self.cnx.cursor()
        cursor.execute(query, (token,))
        result = cursor.fetchall()
        if result[0][0] is not 0:
            print "Already Record"
            exit()
        content = ""
        for _content in rawContent:
            content += _content.text
        tag = apiCall.call("",token,content)
        try:
            with closing(self.cnx.cursor()) as cursor:
                # cursor.execute(
                #     "INSERT INTO "+ table +" (`token`,`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ",
                #     (
                #         token,12, title, content, detailUrl, int(time.time()), int(time.time()),title,content,
                #     )
                # )
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token, 12, title, content, tag, detailUrl, 1, int(time.time()), int(time.time()), title,
                        content,
                        int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            pass

        print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
        time.sleep(1)
        # time.sleep(1)
# for i in range(20170801,20170807):
#     date = str(i)
#     rawCreatedDate = datetime.date(int(date[0:4]),int(date[4:6]),int(date[6:8]))
#     createdDate = int(time.mktime(rawCreatedDate.timetuple()))
#     w = appleDailyTw("http://www.appledaily.com.tw/appledaily/archive/"+str(i),createdDate)
#     w.start()
#     time.sleep(2)
w = appleDailyTw("http://www.appledaily.com.tw/rss/newcreate/kind/rnews/type/new")
w.run()
