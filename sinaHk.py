import databaseConfig
import threading
import requests
import apiCall
import hashlib
import re
import time
import json
from tabulate import tabulate
from bs4 import BeautifulSoup
from contextlib import closing
from pprint import pprint
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
os.environ['TZ'] = 'Asia/Hong_Kong'
time.tzset()


class sinaHk():
    def __init__(self, url):
        self.cnx = databaseConfig.dbconn("")
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'referer': 'http://sina.com.hk'}
        self.domain = "http://sina.com.hk"

    def run(self):

        r = requests.get(self.url,headers=self.headers)
        # soup = BeautifulSoup(r.content, "lxml")
        # print soup
        # print r.content
        data = json.loads(r.content)
        for d in data["data"]:
            date =  d["newsdate"]
            url =  self.domain + d["url"]
            self.detail(url,date)

    def detail(self, detailUrl,date):
        r = requests.get(detailUrl,headers=self.headers)
        soup = BeautifulSoup(r.content, "lxml")
        title =  soup.find("div",{"class","news-title"}).text
        token = hashlib.sha256(detailUrl).hexdigest()
        unixDate =  int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))
        rawContent = soup.find("div", {"class", "news-body"}).findAll("p")
        content = ""
        for _content in rawContent:
                content += _content.text
        tag = apiCall.call("",token,content)
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(
                    "INSERT INTO feeds(`token`,`platform_id`,`title`,`content`,`tag`,`href`,`category`,`created_time`,`updated_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                    (
                        token,13, title, content, tag,detailUrl, 1,unixDate, unixDate,title, content,int(time.time()),
                    )
                )
            self.cnx.commit()
        except TypeError as e:
            print(e)
            print "error"

        print tabulate([[title,  content[:10]]], headers=['title',  'summary'])
        time.sleep(2)

w = sinaHk("http://sina.com.hk/p/api/news/main/category/8/0/0/1")
w.run()
