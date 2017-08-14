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
class wallStreet():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url

    def Newsfeed(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, "lxml")
        items = soup.find("ul", {"class": "showSubsect"}).findAll("li")
        for li in items:
            href = "http://www.wsj.com/" + str(li.a.get("href"))
            self.run(href, str(li.a.text))
            time.sleep(30)

    def run(self, url, category):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            title = _item.title.text
            link = _item.link.text
            summary = _item.description.text
            try:
                with closing(self.cnx.cursor()) as cursor:
                    cursor.execute("INSERT INTO wallstreet(`title`,`summary`,`link`,`created_time`,`category`) VALUES (%s,%s,%s,%s,%s)",
                                   (title, summary, link, int(time.time()),category,))
                self.cnx.commit()
            except TypeError as e:
                print(e)
                print "error"

            print tabulate([[title, link, summary]], headers=['title', 'link', 'summary'])



w = wallStreet("http://www.wsj.com/public/page/rss_news_and_feeds.html")
w.Newsfeed()
