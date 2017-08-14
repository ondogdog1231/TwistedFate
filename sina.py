import databaseConfig
import threading
import requests
import re
import time
import apiCall
import hashlib
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class gamme(threading.Thread):
    def __init__(self, url):
        super(gamme, self).__init__()
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://news.gamme.com.tw/'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            # print _item
            detailUrl = _item.link.text
            # print detailUrl
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1", {"id": "artibodyTitle"}).text
        token = hashlib.sha256(detailUrl).hexdigest()
        content = soup.find("div",{"class":"article"}).text.lstrip()
        tag = apiCall.call("",token,content)

        try:
            with closing(self.cnx.cursor()) as cursor:
                # cursor.execute(
                #     "INSERT INTO newsTest(`token`,`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                #     (token,11, title, content, detailUrl, int(time.time()), int(time.time()),title,content,int(time.time()),))
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token, 11, title, content, tag, detailUrl, 1, int(time.time()), int(time.time()), title, content,
                        int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title, detailUrl[:30], content[:10]]], headers=['title', 'link', 'summary'])
        time.sleep(1)

w = gamme("http://rss.sina.com.cn/news/china/focus15.xml")
w.run()

