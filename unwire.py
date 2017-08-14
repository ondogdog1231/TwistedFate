import databaseConfig
import apiCall
import threading
import requests
import hashlib
import re
import time
import datetime
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
os.environ['TZ'] = 'Asia/Hong_Kong'
time.tzset()


class unwire():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://unwire.hk/category/'}

    def run(self):
        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        items = soup.findAll("li", {"class": "bloglike"})
        for _item in items:
            detailUrl = _item.h3.a.get("href")
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1", {"class": "post entry-title"}).text
        token = hashlib.sha256(detailUrl).hexdigest()
        # print title.encode("utf-8")
        rawContent = soup.find("div", {"class", "entry"}).findAll("p")
        content = ""
        for _content in rawContent:
            if _content.get("class") is None:
                content += _content.text
        tag = apiCall.call("",token,content)


        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token,1, title, content,tag, detailUrl,3, int(time.time()), int(time.time()),title, content,int(time.time()),
                     )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
        # time.sleep(3)

today = datetime.datetime.today()
year = str(today.year)
month = str(today.month)
day = str(today.day)
w = unwire("https://unwire.hk/"+year+"/"+month+"/"+day+"/")
w.run()
