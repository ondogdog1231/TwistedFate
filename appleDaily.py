import databaseConfig
import threading
import hashlib
import apiCall
import requests
import re
import time
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class appleDaily():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'http://hk.apple.nextmedia.com'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        items = soup.findAll("div",{"class":"enews_box"})
        for _item in items:
            # title = _item.title.text
            title = _item.span.text
            detailUrl =  _item.a.get("href")
            # print detailUrl
            # print title
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        token = hashlib.sha256(detailUrl).hexdigest()
        title =  soup.find("div", {"class", "LHSBorderBox"}).h1.text.lstrip()
        content = soup.find("div", {"class", "ArticleContent_Inner"}).text.lstrip()
        tag = apiCall.call("",token,content)
        try:
            with closing(self.cnx.cursor()) as cursor:
                # cursor.execute(
                #     "INSERT INTO entertainment(`platform_id`,`token`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                #     (8, token, title, content, detailUrl, int(time.time()), int(time.time()),title,content,int(time.time()),))
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token, 8, title, content, tag, detailUrl, 2, int(time.time()), int(time.time()), title,
                        content,
                        int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title[:10], detailUrl[:10], content[:30]]], headers=['title', 'link', 'summary'])
        time.sleep(1)

t = appleDaily("http://hk.apple.nextmedia.com/enews/realtime/hit")
t.run()
