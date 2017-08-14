# coding=utf-8
import databaseConfig
import requests
import time
import json
import sys

sys.setdefaultencoding('utf8')
import os

reload(sys)

os.environ['TZ'] = 'Asia/Hong_Kong'
time.tzset()

def call(self, token,content):
        '''
        Key Word List
        :return:
        '''
        cnx = databaseConfig.dbconn("")
        cursor = cnx.cursor()
        query = "SELECT count(*) FROM crawler.feeds where token=%s;"
        cursor.execute(query,(token,))
        result = cursor.fetchall()
        if result[0][0] is not 0:
            return "should not be displayed"

        keyWord = [
            "性侵",
            "裸體",
            "新北市"
        ]


        url = "https://language.googleapis.com/v1/documents:analyzeEntities?key=AIzaSyApD2KOIDycoDrmvsrzp6BrasIIRCDNawQ"
        data = {
            'encodingType': 'UTF8',
            'document': {
                'type': 'PLAIN_TEXT',
                'content': content
            }
        }

        json_data = json.dumps(data)

        response = requests.post(url, json_data)
        responseJson = response.json()
        tag = []
        for i in keyWord:
            if i in content:
                tag.append(i)

        for i in responseJson["entities"]:
            if len(tag) > 10:
                continue
            if len(i["name"]) > 30 or i["name"] in tag or len(i["name"]) < 1:
                continue
            if i["salience"] > 0.03 :
                tag.append(i['name'])
            if i["type"] == "LOCATION" and len(i["name"]) > 1:
                tag.append(i['name'])

        tagJson = json.dumps(tag, encoding='UTF-8', ensure_ascii=False)
        return tagJson



