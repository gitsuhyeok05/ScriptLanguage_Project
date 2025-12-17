#!/usr/bin/python
# coding=utf-8

import sys
import time
import sqlite3
import telepot
from pprint import pprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import traceback
from requestValue import*
from animal import*
from requestValue import*
from animal import*

MAX_MSG_LENGTH = 300

TOKEN ='토큰필요'

baseurl = 'https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic?serviceKey=Bst8DsrxQ7RorD2aw2vb4FGO7mfU4MQ7yrH%2FSYzAN6hYr5OaDJZDV4fYUgUjGtexpTALuChYvNgqV5Uhc8%2BSgQ%3D%3D'

bot = telepot.Bot(TOKEN)
def getData(bgn_param,end_param):
    url = baseurl+'&bgnde='+bgn_param+'&endde='+end_param+'&pageNo=1&numOfRows=10'
    response = requests.get(url)
    root = ET.fromstring(response.text)
    animal_list = []
    for item in root.iter("item"):
        animal = Animal(item)
        animal_list.append(animal.getSimpleData())
    return animal_list


def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)

def run(date_param, param='11710'):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()

    user_cursor = sqlite3.connect('users.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        user, param = data[0], data[1]
        print(user, date_param, param)
        res_list = getData( param, date_param )
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                print( str(datetime.now()).split('.')[0], r )
                if len(r+msg)+1>MAX_MSG_LENGTH:
                    sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            sendMessage( user, msg )
    conn.commit()

if __name__=='__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    print( '[',today,']received token :', TOKEN )
    try:
        pprint( bot.getMe() )
    except:
        print("정상적인 토큰이 아닙니다.")

    run(current_month)
