import databaseConfig
import threading
import requests
import re
import time
from tabulate import tabulate
from contextlib import closing
import sys

reload(sys)
sys.setdefaultencoding('utf8')

countryArr = [
    "us",
    "asia",
    "europe"
]
htmlClass = {
    # div or h1 class                #hyperlink class
    "top-news-v3-story-headline": "top-news-v3-story-headline__link",
    "hero-v6-story__headline": "hero-v6-story__headline-link",
    "highlights-v6-story__headline": "highlights-v6-story__headline-link"
}


class bloomberg(threading.Thread):
    def __init__(self, country):
        super(bloomberg, self).__init__()
        self.cnx = databaseConfig.dbconn("")
        self.country = country

    def run(self):
        for key, value in htmlClass.iteritems():
            # print str(i)+" "+key+" and "+value
            urlCountry = self.country
            if urlCountry == "us":
                urlCountry = ""
            targetUrl = "https://www.bloomberg.com/" + urlCountry
            time.sleep(5)
            r = requests.get(targetUrl)
            if key == "top-news-v3-story-headline":
                requestClass = r'<h1 class="' + key + '">.*?<a href="(.*?)" class="' + value + '".*?>(.*?)</a>'
            else:
                requestClass = r'<div class="' + key + '">.*?<a href="(.*?)" class="' + value + '".*?>(.*?)</a>'
            content = re.findall(requestClass, r.content)
            for c in content:
                url = c[0]
                if "https" not in url:
                    url = "https://www.bloomberg.com" + url
                urlDecode = url.decode("utf-8")
                titleDecode = c[1].decode("utf-8")
                print tabulate([[self.country,titleDecode, urlDecode, key]], headers=['Country','Title', 'URL', 'key'])
                try:
                    with closing(self.cnx.cursor()) as cursor:
                        cursor.execute("INSERT INTO bloomberg(`title`,`link`,`country`,`created_at`) VALUES (%s,%s,%s,%s)",
                                       (titleDecode, urlDecode, self.country, int(time.time()),))
                    self.cnx.commit()
                except TypeError as e:
                    print(e)
                    print "error"



for _country in countryArr:
    b = bloomberg(_country)
    b.run()
    time.sleep(5)