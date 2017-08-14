# coding=utf-8
import threading
import requests
import time
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from tabulate import tabulate
import re
import hashlib
import sys
import databaseConfig
from contextlib import closing
import random
import urllib2
import json

reload(sys)
sys.setdefaultencoding('utf8')

cnx = databaseConfig.dbconn("")


##threading.Thread
class migration(threading.Thread):
    def __init__(self, platform_id, token, title, content, href, created_time, updated_time):
        super(migration, self).__init__()
        self.cnx = databaseConfig.dbconn("")
        self.platform_id = platform_id
        self.token = token
        self.title = title
        self.content = content
        self.href = href
        self.created_time = created_time
        self.updated_time = updated_time
        if self.token is None:
            self.token = hashlib.sha256(self.href).hexdigest()

    def run(self):
        tag = self.naturalLanguage()

        try:
            print tabulate(
                [[self.title]],
                headers=['title'])
            print tabulate(
                [[self.content[:50]]],
                headers=['content'])
            try:
                with closing(self.cnx.cursor()) as cursor:
                    cursor.execute(
                        "INSERT INTO feeds(`platform_id`,`token`,`title`,`content`,`tag`,`href`,`category`,`updated_time`,`created_time`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `title` = %s, `content` = %s ,`updated_time` = %s",
                        (
                            self.platform_id, self.token, self.title, self.content, tag, self.href, 1,
                            self.updated_time, self.created_time,
                            self.title, self.content, self.updated_time
                        )
                    )
                    self.cnx.commit()
            except TypeError as e:
                print e
                exit()
                raise
                # time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print "Exit now"
            raise

    time.sleep(1)

    def naturalLanguage(self):

        keyWord = [
            "性侵",
            "裸體",
            "新北市",
        ]
        try:
            url = "https://language.googleapis.com/v1/documents:analyzeEntities?key=AIzaSyApD2KOIDycoDrmvsrzp6BrasIIRCDNawQ"
            data = {
                'encodingType': 'UTF8',
                'document': {
                    'type': 'PLAIN_TEXT',
                    'content': self.content
                }
            }

            json_data = json.dumps(data)

            response = requests.post(url, json_data)
            responseJson = response.json()

            tag = []
            for i in keyWord:
                if i in self.content:
                    tag.append(i)
            print tabulate(
                [[self.token]],
                headers=['token'])

            for i in responseJson["entities"]:
                if i["salience"] > 0.03 and i["name"] not in tag:
                    tag.append(i['name'])
                if i["type"] == "LOCATION" and i["name"] not in tag:
                    tag.append(i['name'])

            tagJson = json.dumps(tag, encoding='UTF-8', ensure_ascii=False)

            return tagJson
        except TypeError as e:
            print e


cursor = cnx.cursor()
query = "SELECT platform_id,token, title, content, href,created_time, updated_time FROM crawler.news;"
cursor.execute(query)
results = cursor.fetchall()
i = 0
for row in results:
    print  "No: "+ str(i)
    m = migration(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
    m.start()
    i += 1
    if i == 900:
        time.sleep(100)
        i = 0
