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

import noti

#오늘 날자 받아서 사용
def replyAptData(user,bngde, endde):
    res_list = noti.getData(bngde, endde)
    msg = ''
    for r in res_list:
        print( str(datetime.now()).split('.')[0], r )
        if len(r+msg)+1>noti.MAX_MSG_LENGTH:
            noti.sendMessage( user, msg )
            msg = r+'\n'
        else:
            msg += r+'\n'
    if msg:
        noti.sendMessage( user, msg )
    else:
        noti.sendMessage( user, '해당하는 데이터가 없습니다.')

def save( user, loc_param ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    try:
        cursor.execute('INSERT INTO users(user, location) VALUES ("%s", "%s")' % (user, loc_param))
    except sqlite3.IntegrityError:
        noti.sendMessage( user, '이미 해당 정보가 저장되어 있습니다.' )
        return
    else:
        noti.sendMessage( user, '저장되었습니다.' )
        conn.commit()

def check( user ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    cursor.execute('SELECT * from users WHERE user="%s"' % user)
    for data in cursor.fetchall():
        row = 'id:' + str(data[0]) + ', location:' + data[1]
        noti.sendMessage( user, row )


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        noti.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return

    text = msg['text']
    args = text.split(' ')

    if text.startswith('조회') and len(args)>1:
        print('try to 조회', args[1],args[2])
        replyAptData(chat_id, args[1],args[2])
    elif text.startswith('저장')  and len(args)>1:
        print('try to 저장', args[1])
        save( chat_id, args[1] )
    elif text.startswith('확인'):
        print('try to 확인')
        check( chat_id )
    else:
        noti.sendMessage(chat_id, '모르는 명령어입니다.\n조회 [시작날짜] [끝날짜], 저장 [시작날짜] [끝날짜], 확인 중 하나의 명령을 입력하세요.')

today = date.today()
current_month = today.strftime('%Y%m')

print( '[',today,']received token :', noti.TOKEN )


def message_loop():
    bot = telepot.Bot(noti.TOKEN)
    try:
        pprint( bot.getMe() )
    except:
        print("정상적인 토큰이 아닙니다.")
        return
    bot.message_loop(handle)
    print('Listening...')