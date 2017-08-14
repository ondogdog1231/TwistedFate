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

reload(sys)
sys.setdefaultencoding('utf8')


class pingTester():
    def __init__(self, url):
        # super(pingTester, self).__init__()
        self.url = url
        self.count = 1
        self.cnx = databaseConfig.dbconn("")
        self.domain = "http://www.aastocks.com"
        # self.t = int(time.time())
        # self.condition = self.t - 3600
        ##Test
       # self.t =  datetime.strptime("2017-07-13 05:00", "%Y-%m-%d %H:00")
       # self.condition = time.mktime(self.t.timetuple()) - 3600
        self.t = int(time.time())
        self.condition = self.t - 3600
        ##test

    def Newsfeed(self):
        r = requests.get(self.url)
        ##First 10 content in page
        soup = BeautifulSoup(r.content, "lxml")
        contentBox = soup.findAll("div", {"class": "content_box"})
        for contentBoxText in contentBox:
            if contentBoxText.find("a") is not None:
                title = contentBoxText.find("a").text
                href = self.domain + contentBoxText.find("a").get("href")
                lastTime = contentBoxText.find("div", {"class": "newstime2"}).text
                print tabulate(
                    [[title, href, lastTime]],
                    headers=['title', 'Href', 'Time'])
                try:
                    with closing(self.cnx.cursor()) as cursor:
                        cursor.execute(
                            "INSERT INTO aastock(`title`,`href`,`article_time`,`created_time`) VALUES (%s,%s,%s,%s)",
                            (title, href, lastTime, int(time.time()),))
                    self.cnx.commit()
                except TypeError as e:
                    print(e)
                    print "error"

        #Find the lastId and Time to create API
        info = re.findall(r"var sLastNewsID = '([^']+)';.+var sLastNewsTime = '([^']+)';", r.content, re.DOTALL)
        id = str(info[0][0])
        infoTime = str(info[0][1])
        api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime="+infoTime+"&newsid="+id+"&period=0&key="
        apiReq = requests.get(api)
        i = 0
        for news in apiReq.json():
           ##Change the data time to unix time
           readTime = news['dt']
           rawTime = datetime.strptime(readTime, "%Y/%m/%d %H:%M")
           resultTime = datetime.strftime(rawTime, "%Y-%m-%d %H:00")
           dataTime = datetime.strptime(resultTime, "%Y-%m-%d %H:00")
           unixDataTime = time.mktime(dataTime.timetuple())
           ## end transformation
           if unixDataTime < self.condition:
               exit()
           else:
               title = news['h']
               lastTime = news['dtd']

               lastId = news['id']
               href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
               i +=1
               print tabulate(
                   [[title, lastId,readTime]],
                   headers=['title', 'ID', 'Time'])
               try:
                   with closing(self.cnx.cursor()) as cursor:
                       cursor.execute("INSERT INTO aastock(`title`,`href`,`article_time`,`created_time`) VALUES (%s,%s,%s,%s)",(title, href, readTime, int(time.time()),))
                   self.cnx.commit()
               except TypeError as e:
                   print(e)
                   print "error"
        self.recursive(lastTime,lastId)

    def recursive(self,lastTime,id):
        api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime=" + str(
            lastTime) + "&newsid=" + str(id) + "&period=0&key="
        apiReq = requests.get(api)
        time.sleep(10)
        for news in apiReq.json():
            ##Change the data time to unix time
            readTime = news['dt']
            rawTime = datetime.strptime(readTime, "%Y/%m/%d %H:%M")
            resultTime = datetime.strftime(rawTime, "%Y-%m-%d %H:00")
            dataTime = datetime.strptime(resultTime, "%Y-%m-%d %H:00")
            unixDataTime = time.mktime(dataTime.timetuple())
            ## end transformation
            if unixDataTime<self.condition:
                print tabulate([[unixDataTime, self.condition]],headers=['UNIX','Condition'])
                exit()
            else:
                title = news['h']
                lastTimeUnix = news['dtd']
                lastTime = news['dt']
                lastId = news['id']
                href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
                print tabulate(
                    [[title, lastId,lastTimeUnix, readTime]],
                    headers=['title', 'ID','UnixTime', 'Time'])
                try:
                    with closing(self.cnx.cursor()) as cursor:
                        cursor.execute(
                            "INSERT INTO aastock(`title`,`href`,`article_time`,`created_time`) VALUES (%s,%s,%s,%s)",
                            (title, href, lastTime, int(time.time()),))
                    self.cnx.commit()
                except TypeError as e:
                    print(e)
                    print "error"
        self.recursive(lastTimeUnix, lastId)

        # if self.count <= 30:
        #     api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime=" + str(lastTime) + "&newsid=" + str(id) + "&period=0&key="
        #     apiReq = requests.get(api)
        #     time.sleep(20)
        #     for news in apiReq.json():
        #         title = news['h']
        #         lastTimeUnix = news['dtd']
        #         lastTime = news['dt']
        #         lastId = news['id']
        #         href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
        #         print tabulate(
        #             [[title, lastId, lastTimeUnix]],
        #             headers=['title', 'ID', 'Time'])
        #         try:
        #             with closing(self.cnx.cursor()) as cursor:
        #                 cursor.execute(
        #                     "INSERT INTO aastock(`title`,`href`,`article_time`,`created_time`) VALUES (%s,%s,%s,%s)",
        #                     (title, href, lastTime, int(time.time()),))
        #             self.cnx.commit()
        #         except TypeError as e:
        #             print(e)
        #             print "error"
        #     self.count += 1
        #     print "count: " +str(self.count)
        #     self.recursive(lastTimeUnix, lastId)

    def run(self,url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.findAll("item")
        for _item in items:
            title = _item.title.text
            link = _item.link.text
            description = _item.description.text
            print tabulate([[title,link,description]], headers=['title', 'link', 'description'])



t = pingTester("http://www.aastocks.com/tc/stocks/news/aafn/latest-news")
t.Newsfeed()
