import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import re
import sys
import json
import time
import datetime
from datetime import date
from datetime import datetime, timedelta
reload(sys)
sys.setdefaultencoding('utf8')


class pingTester():
    def __init__(self, url):
        # super(pingTester, self).__init__()
        self.url = url
        self.count = 1
        self.domain = "http://www.aastocks.com"
        self.t = t =datetime.strptime("2017-07-11 03:00" ,"%Y-%m-%d %H:00")
        self.condition = unixTimeNow = time.mktime(self.t.timetuple()) - 3600

    def Newsfeed(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, "lxml")
        contentBox = soup.findAll("div", {"class": "content_box"})
        for contentBoxText in contentBox:
            if contentBoxText.find("a") is not None:
                title =  contentBoxText.find("a").text
                href =  self.domain + contentBoxText.find("a").get("href")
                article_time =  contentBoxText.find("div",{"class":"newstime2"}).text
                print tabulate(
                    [[title, href, article_time]],
                    headers=['title', 'Href', 'Time'])
        info = re.findall(r"var sLastNewsID = '([^']+)';.+var sLastNewsTime = '([^']+)';", r.content, re.DOTALL)
        id = str(info[0][0])
        infoTime = str(info[0][1])
        api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime="+infoTime+"&newsid="+id+"&period=0&key="
        apiReq = requests.get(api)
        # print len(apiReq.json())
        # exit()
        i = 0
        # t = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M")
        # t =datetime.now()

        # t =datetime.strptime("2017-07-12 10:00" ,"%Y-%m-%d %H:00")
        # unixTimeNow = time.mktime(t.timetuple())
        # print "Now"
        # print unixTimeNow

        # print "Past Hour: "

        # print int(pastHour)
        ## Condition
        # condition =  time.strftime("%Y-%m-%d %H:%M", time.localtime(pastHour))
        # print "condition"
        # print condition

        for news in apiReq.json():
            ##Change the data time to unix time
            readTime = news['dt']
            rawTime = datetime.strptime(readTime, "%Y/%m/%d %H:%M")
            resultTime = datetime.strftime(rawTime, "%Y-%m-%d %H:00")
            dataTime = datetime.strptime(resultTime, "%Y-%m-%d %H:00")
            unixDataTime = time.mktime(dataTime.timetuple())
            ## end transformation
            if unixDataTime<self.condition:
                exit()
            else:
                title = news['h']
                lastTime = news['dtd']
                lastId = news['id']
                lastUnixDataTime = unixDataTime

                href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
                i +=1
           # print "First loop--the i is: "+ str(i)

                print tabulate([[title, href,lastId,readTime]],headers=['title','Link', 'ID', 'Time'])
        # print "lastTime: "+ str(lastTime)
           # if i == 20:
           #     print "last" + str(i)
        self.recursive(lastTime,lastId)

    def recursive(self,recursiveTime,id):
        api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime=" + recursiveTime + "&newsid=" + id + "&period=0&key="
        apiReq = requests.get(api)
        time.sleep(5)
        for news in apiReq.json():
            ##Change the data time to unix time
            readTime = news['dt']
            rawTime = datetime.strptime(readTime, "%Y/%m/%d %H:%M")
            resultTime = datetime.strftime(rawTime, "%Y-%m-%d %H:00")
            dataTime = datetime.strptime(resultTime, "%Y-%m-%d %H:00")
            unixDataTime = time.mktime(dataTime.timetuple())
            ## end transformation
            if unixDataTime<self.condition:
                exit()
            else:
                title = news['h']
                lastTimeUnix = news['dtd']
                lastTime = news['dt']
                lastId = news['id']
                href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
                print tabulate(
                    [[title, href, lastId, readTime]],
                    headers=['title', 'Link', 'ID', 'Time'])
        self.recursive(lastTimeUnix, lastId)

        ##Old Version (NO check date) ##
        # if self.count <= 2:
        #     api = "http://www.aastocks.com/tc/resources/datafeed/getmorenews.ashx?cat=latest-news&newstime=" + time + "&newsid=" + id + "&period=0&key="
        #     apiReq = requests.get(api)
        #     for news in apiReq.json():
        #         title = news['h']
        #         lastTimeUnix = news['dtd']
        #         lastTime = news['dt']
        #         lastId = news['id']
        #         href = self.domain + "/tc/stocks/news/aafn-content/" + lastId + "/latest-news"
        #         print tabulate(
        #             [[title, href,lastId, lastTime]],
        #             headers=['title', 'Link','ID', 'Time'])
        #     self.count += 1
        #
        #     self.recursive(lastTimeUnix, lastId)
            ##Old Version (NO check date)End ##

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
