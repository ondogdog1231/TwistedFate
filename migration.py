import threading
import requests
import time
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from tabulate import tabulate
import re
import sys
import databaseConfig
from contextlib import closing
import random
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')

cnx = databaseConfig.dbconn("")
##threading.Thread
class migration(threading.Thread):
    def __init__(self, title,content,href):
        super(migration, self).__init__()
        self.cnx = databaseConfig.dbconn("")
        self.title = title
        self.content = content
        self.href = href

    def run(self):
        try:
            # proxy = self.proxyTest()
            # cursor = self.cnx.cursor()
            # query = "SELECT id,link FROM crawler.bloomberg limit 1 offset " + str(self.offset)
            # cursor.execute(query)
            # results = cursor.fetchall()
            # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            #            'referer':'https://www.bloomberg.com'}
            # # proxies = {"https" : "188.168.27.77:3128"}
            # r = requests.get(self.url,headers=headers)
            # soup =BeautifulSoup(r.content,'lxml')
        #     ## News title
        #     title = soup.find("h1",{"class":"lede-text-only__hed"})
        #     ## article Title
        #     if title is None:
        #         title = soup.find("h1", {"class": "article-title"})
        #     if title is None:
        #         title = soup.find("h1", {"class": "lede-large-content__highlight"})
        #     if title is None:
        #         title = soup.find("h1", {"class": "lede-large-content__hed"})
        #     if title is None:
        #         print self.url
        #         print "Title none"
        #         exit()
        #     ## News Content
        #     content = soup.find("div", {"class": "body-copy"})
        #     ## Article content
        #     if content is None:
        #         content = soup.find("div",{"class":"copy-block"})
        #     if content is None:
        #         print self.url
        #         print "Content none"
        #         exit()
        #     # for p in content.findAll("p"):
        #     #     print p.text
        #     rawTime = soup.find("time").get("datetime")
        #     rawTime = rawTime.replace("T"," ")
        #     rawTime = rawTime[:19]
        #     rawArticleTime = datetime.strptime(rawTime, "%Y-%m-%d %H:%M:%S")
        #     articleTime = int(time.mktime(rawArticleTime.timetuple()))
        #     print tabulate(
        #                 [[title.text]],
        #                 headers=['title'])
        #     print tabulate(
        #         [[content.text[:30]]],
        #         headers=['content'])
        #     print tabulate(
        #         [[rawTime]],
        #         headers=['DisplayTime'])
        #     try:
        #         with closing(self.cnx.cursor()) as cursor:
        #             cursor.execute(
        #                 "INSERT INTO crawler_article(`platform_id`,`article_id`,`title`,`href`,`content_short`,`content`,`display_time`,`updated_time`,`created_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        #                 ("bloomberg", self.id, title.text, self.url, content.text[:50], content.text, articleTime, int(time.time()),
        #                  int(time.time()),))
        #             self.cnx.commit()
        #     except TypeError as e:
        #         pass
        #         # print(e)
        #         # print "error"
        #     time.sleep(5)
        # except (KeyboardInterrupt, SystemExit):
        #     print "Exit now"
        #     raise


            # url = row[0]  ##This is the hyperlink
            # headers = {
            #             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            #             'referer': 'https://www.bloomberg.com'}
            # # proxies = {"https" : "188.168.27.77:3128"}
            # r = requests.get(self.url, headers=headers)
            # soup = BeautifulSoup(r.content, 'lxml')
            # title = soup.find("span", {"id": "lblSTitle"}).text
            # rawDate = soup.find("span", {"id": "spanDateTime"}).text
            # rawArticleTime = datetime.strptime(rawDate, "%Y/%m/%d %H:%M")
            # articleTime = int(time.mktime(rawArticleTime.timetuple()))
            # articleId = self.id
            # content = soup.find("p").text

            print tabulate(
                [[self.href]],
                headers=['href'])
            print tabulate(
                [[self.title]],
                headers=['title'])
            print tabulate(
                [[self.content[:50]]],
                headers=['content'])
            try:
                with closing(self.cnx.cursor()) as cursor:
                    cursor.execute(
                            "INSERT INTO news(`platform_id`,`title`,`href`,`content`,`updated_time`,`created_time`) VALUES (%s,%s,%s,%s,%s,%s)",
                            ('4', self.title, self.href, self.content,  int(time.time()),int(time.time()),))
                    self.cnx.commit()
            except TypeError as e:
                pass
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
                print "Exit now"
                raise

cursor = cnx.cursor()
query = "SELECT title,content,href FROM crawler.hkej"
cursor.execute(query)
results = cursor.fetchall()
for row in results:
    print row[0]
    m = migration(row[0], row[1],row[2])
    m.start()



