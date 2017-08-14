import threading
import requests
import re
import mysql.connector
import time
# from tabulate import tabulate
from contextlib import closing
import sys
reload(sys)
sys.setdefaultencoding('utf8')



def dbconn(self):
    return mysql.connector.connect(user='adam.lok', password='ondogdog1231',host='127.0.0.1',database='crawler',charset='utf8mb4',)
    # return cnx