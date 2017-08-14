import databaseConfig
import hashlib
import threading
import requests
import apiCall
import re
import time
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class asahi():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'http://www.asahi.com/information/service/rss.html'}

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            # title = _item.title.text
            detailUrl =  _item.link.text
            self.detail(detailUrl)

    def detail(self, detailUrl):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1").text
        token = hashlib.sha256(detailUrl).hexdigest()
        rawContent = soup.find("div", {"class", "ArticleText"})
        if rawContent is None:
            rawContent = soup.find("div", {"class", "article_body"})
        content = ""
        if rawContent is not None:
            for _content in rawContent.findAll("p"):
                    content += _content.text
            tag = apiCall.call("",token,content)
            try:
                with closing(self.cnx.cursor()) as cursor:
                    # cursor.execute(
                    #     "INSERT INTO news(token,`platform_id`,`title`,`content`,`href`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    #     (token,9, title, content, detailUrl, int(time.time()), int(time.time()),title, content,int(time.time()),))
                    cursor.execute(
                        "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                        (
                            token, 9, title, content, tag, detailUrl, 1, int(time.time()), int(time.time()), title,
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

t = asahi("http://rss.asahi.com/rss/asahi/newsheadlines.rdf")
t.run()
