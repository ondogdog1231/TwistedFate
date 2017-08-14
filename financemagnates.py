import threading
import requests
import re
import mysql.connector
import time
from tabulate import tabulate
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import Queue
from HTMLParser import HTMLParser
from lxml import html
from pprint import pprint
import abc


ArticleData = ""
urlType = [
        "technology",
        "Regulation",
        "products",
        "brokers",
        "analysis"
    ]

class UrlGrep(threading.Thread):

    def __init__(self, page_no):
        super(UrlGrep, self).__init__()
        self.cnx = mysql.connector.connect(user='adam.lok', password='demo1234',host='127.0.0.1',database='crawler')
        # self.cursor = self.cnx.cursor()
        self.page_no = page_no

    def run(self):

            for field in urlType:
                try:
                    targetUrl = "http://www.financemagnates.com/binary-options/" + field + "/page/" + str(self.page_no)
                    r = requests.get(targetUrl)
                    content = re.findall(r'<div.*?class=".?h2 entry-title">.?<a href="(.*?)">(.*?)</a></div>', r.content)
                    for c in content:
                        url = c[0].decode("utf-8")
                        title = c[1].decode("utf-8")
                        print tabulate([[title, url]], headers=['Title', 'URL'])
                        try:
                            with closing(self.cnx.cursor()) as cursor:
                                cursor.execute(
                                    "INSERT INTO summary(`type`,`title`,`href`,`created_time`) VALUES (%s,%s,%s,%s)",
                                    (field, title, url, int(time.time()),))
                            self.cnx.commit()
                        except:
                            print "error"
                except KeyboardInterrupt:
                    print 'exiting main url'
                    break


    def articleRun(self):
        for field in urlType:
            query =("select id,title,href from summary where type='"+field+"' order by `created_time` desc limit 20;")
            print query
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            for row in results:
                referId = row[0]
                referUrl = row[2]
                print referUrl
                # time.sleep(1)
                r =requests.get(referUrl)
                content = re.findall(r'<article .*?>.?<header><h1 class="entry-title">(.*?)</h1><div class=".*?">(.*?)</div>.*?<div class="entry-meta">.*?<span>(.*?)</span>.*?<span class="cat-link">.*?<a href="(.*?)">(.*?)</a>.*? href="(.*?)">(.*?)</a>.*?datetime="(.*?)">.*?class="the-content">(.*?)</div>',r.content)
                if not content:
                    # This will print the first paragraph only. Since the content is too long.
                    content = re.findall(r'<article .*?>.?<header><h1 class="entry-title">(.*?)</h1><div class=".*?">(.*?)</div>.*?<div class="entry-meta">.*?<span>(.*?)</span>.*?<span class="cat-link">.*?<a href="(.*?)">(.*?)</a>.*? href="(.*?)">(.*?)</a>.*?datetime="(.*?)">.*?class="entry-content">(.*?)</p>',r.content)
                    with open("Output.txt", "w") as text_file:
                        text_file.write("These website cant be grep perfectly : {}".format(referUrl))
                try:
                    title = content[0][0]  # title
                    brief = content[0][1]  # Brief
                    author = content[0][2]  # author
                    type = content[0][4] + "/" + content[0][6]  # small cata and mother cata name
                    article_time = content[0][7]  # Article create time
                    Articlecontent = content[0][8]  # Article content
                    print title + " By " + author + ": " + brief
                    cursor.execute(
                        "INSERT INTO articles(`refer_summary_id`,`url`,`title`,`brief`,`author`,`type`,`article_time`,`content`,`created_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                        referId, referUrl, title, brief, author, type, article_time, Articlecontent, int(time.time()),))
                    cnx.commit()
                    print("------ ----- ----- -----")
                except:
                    print "These website cant be grep perfectly :" + referUrl
                    text_file.write("These website cant be grep perfectly : {}".format(referUrl))
                    continue

    def urlTest(self):
        url = "http://www.financemagnates.com/binary-options/products/airsoft-rolls-out-a-new-upgrade-with-advanced-front-end-features/"
        r = requests.get(url)
        content = re.findall(r'<article .*?>.?<header><h1 class="entry-title">(.*?)</h1><div class=".*?">(.*?)</div>.*?<div class="entry-meta">.*?<span>(.*?)</span>.*?<span class="cat-link">.*?<a href="(.*?)">(.*?)</a>.*? href="(.*?)">(.*?)</a>.*?datetime="(.*?)">.*?class="the-content">(.*?)</div>',r.content)
        if not content:
            content = re.findall(r'<article .*?>.?<header><h1 class="entry-title">(.*?)</h1><div class=".*?">(.*?)</div>.*?<div class="entry-meta">.*?<span>(.*?)</span>.*?<span class="cat-link">.*?<a href="(.*?)">(.*?)</a>.*? href="(.*?)">(.*?)</a>.*?datetime="(.*?)">.*?class="the-content">(.*?)</p>',r.content)

        print content




for i in range(1, 8):
    try:
        url = UrlGrep(i)
        url.start()
        time.sleep(60)
    except KeyboardInterrupt:
        print 'exiting main thread'
        break



# url = UrlGrep()
# for pageNo in range(1, 8):
#     print "Thread-" + str(pageNo) + " Start: "
#     try:
#
#         # threading.Thread(target=url.run, args=(pageNo,url.cnx,url.cursor), name='thread-' + str(pageNo)).start()
#         # time.sleep(5)
#     except:
#         print "Error"
#         continue
# url.run()
# url.articleRun()
# url.urlTest()

