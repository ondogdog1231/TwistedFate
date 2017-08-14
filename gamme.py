import databaseConfig
import threading
import apiCall
import requests
import re
import time
import hashlib
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class gamme():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://news.gamme.com.tw/'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        items = soup.findAll("div",{"class","List-4"})
        for _item in items:
            # print _item
            detailUrl = _item.h3.a.get("href")
            # print detailUrl
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1", {"class": "title"}).text
        token = hashlib.sha256(title[:20]).hexdigest()
        content = soup.find(attrs={"itemprop":"articleBody"}).text.lstrip()
        tag = apiCall.call("",token,content)

        try:
            with closing(self.cnx.cursor()) as cursor:
                # cursor.execute(
                #     "INSERT INTO adult(`token`,`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                #     (token,10, title, content, detailUrl, int(time.time()), int(time.time()),title,content,int(time.time()),))
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token, 10, title, content, tag, detailUrl, 5, int(time.time()), int(time.time()), title,
                        content,
                        int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
        time.sleep(3)

w = gamme("https://news.gamme.com.tw/tag/av%E5%A5%B3%E5%84%AA/")
w.run()
