import databaseConfig
import threading
import apiCall
import hashlib
import requests
import re
import time
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class hksilicon():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://www.hksilicon.com'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        items = soup.findAll("div", {"class": "media-heading"})

        for _item in items:
            detailUrl =  _item.a.get("href")
            self.detail(detailUrl)


    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        article = soup.find("div",{"class","fluid-fixed pull-left"})
        title = article.h1.text
        token = hashlib.sha256(detailUrl).hexdigest()
        rawContent = soup.find("div",{"class","blog-content"}).findAll("p")
        content = ""
        for _content in rawContent:
            content += _content.text
        tag = apiCall.call("",token,content)
        try:
            with closing(self.cnx.cursor()) as cursor:
                # cursor.execute(
                #     "INSERT INTO technology(`platform_id`,`token`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `title`= %s, `content`=%s,`updated_time`= %s",
                #     (
                #         2,token, title, content, detailUrl, int(time.time()), int(time.time()),title,content,int(time.time()),
                #     )
                # )
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token, 2, title, content, tag, detailUrl, 3, int(time.time()), int(time.time()), title,
                        content,
                        int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
        time.sleep(2)

w = hksilicon("https://www.hksilicon.com/categories/48")
w.run()
