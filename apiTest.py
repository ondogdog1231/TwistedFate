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
        query = "SELECT tag FROM crawler.feeds where token=%s;"
        cursor.execute(query,(token,))
        results = cursor.fetchall()
        for i in results:
            print str(i)
        tag = ["None"]
        if results is not None:
            return tag

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
        print tagJson
call("","72411a914a6fa2cc58e7aba1cff569e05444f1ccc0b8eaf1b267f488789d6020","鴻海董事長郭台銘上個月才在白宮宣布，將在威斯康辛州投資3000億元，且已與威斯康辛州政府簽訂MOU合作備忘錄，不過，根據財經媒體CNBC報導，鴻海這樁投資案在威州參議院遭到阻礙，有可能遭到該院的否決。據了解，該州參議院多數黨領袖透露尚未掌握到足夠的票數，可以通過給予鴻海30億美元的獎勵補助。根據共和黨籍威州參院共和黨領袖費茲傑羅（Scott Fitzgerald）周三與州長沃克（Scott Walker）會晤後透露，對於這起投資案部分內容有疑慮，建議應謹慎斟酌是否對威州及州民是好的投資案。（財經中心／台北報導")

