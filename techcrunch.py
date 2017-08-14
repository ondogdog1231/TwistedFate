import databaseConfig
import threading
import requests
import re
import time
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class techcrunch():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'https://techcrunch.com'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            title = _item.title.text
            articleDate = _item.pubDate.text
            detailUrl =  _item.link.text
            self.detail(title, articleDate, detailUrl)

    def detail(self, title, articleDate, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        rawContent = soup.find("div", {"class", "article-entry text"}).findAll("p")
        content = ""
        for _content in rawContent:
            content += _content.text
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO technology(`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s)",
                    (3, title, content, detailUrl, int(time.time()), int(time.time()),))
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title, detailUrl, content[:10]]], headers=['title', 'link', 'summary'])
        time.sleep(3)

t = techcrunch("https://techcrunch.com/social/feed/")
t.run()
