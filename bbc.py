import databaseConfig
import apiCall
import threading
import requests
import hashlib
import re
import time
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
os.environ['TZ'] = 'Asia/Hong_Kong'
time.tzset()


class bbc():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://unwire.hk/category/'}

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
        title = soup.find("h1").text
        # if soup.find("h1").has_attr("story-body__h1"):
        #     title = soup.find("h1", {"class": "story-body__h1"}).text
        # if soup.find("h1").has_attr("vxp-media__headline"):
        #     title = soup.find("h1", {"class": "vxp-media__headline"}).text
        token = hashlib.sha256(detailUrl).hexdigest()
        rawContent = None
        if soup.find("div", {"class", "vxp-media__summary"}) is not None:
            rawContent = soup.find("div", {"class", "vxp-media__summary"}).findAll("p")
        if soup.find("div", {"class", "story-body__inner"}) is not None:
            rawContent = soup.find("div", {"class", "story-body__inner"}).findAll("p")
        if rawContent is not None:

            content = ""
            for _content in rawContent:
                content += _content.text
            tag = apiCall.call("",token,content)
            print len(tag)
            try:
                with closing(self.cnx.cursor()) as cursor:
                    # cursor.execute(
                    #     "INSERT INTO news(`token`,`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    #     (
                    #         token,5, title, content, detailUrl, int(time.time()), int(time.time()),title, content,int(time.time()),
                    #      )
                    # )
                    cursor.execute(
                        "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                        (
                            token, 5, title, content, tag, detailUrl, 1, int(time.time()), int(time.time()), title, content,
                            int(time.time()),
                        )
                    )
                self.cnx.commit()
            except TypeError as e:
                print(e)
                print "error"

            print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
            # time.sleep(1)


w = bbc("http://feeds.bbci.co.uk/news/rss.xml")
w.run()
