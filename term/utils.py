# 잡스러운 함수들 모아두는 파일
import ctypes
import webbrowser
from geopy.geocoders import Nominatim
#geopy 패키지 설치
import re

pattern = r"\([^)]*\)"
def remove_bracket_content(text): # 괄호같은걸로 둘러싸인부분 삭제
    clean_text = re.sub(pattern, "", text)
    return clean_text

def get_windows_text_scaling():
    user32 = ctypes.windll.user32
    # DPI 스케일링 모드 가져오기
    dpi_scaling = user32.GetDpiForSystem()
    # 확대 비율 계산
    text_scaling = dpi_scaling / 96.0
    return text_scaling


def webOpen(url):
    webbrowser.open(url)


def bring_to_front(widget):
    widget.lift()

def scroll_canvas(event, canvas):
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")

def on_configure(event, canvas):
    # 스크롤바의 길이를 콘텐츠에 맞게 조절
    canvas.config(scrollregion=canvas.bbox('all'))

#주소를 받아 경도,위도로 변환
def geoCoding(address):
    geolocoder = Nominatim(user_agent='South Korea', timeout=None)
    geo = geolocoder.geocode(address)
    crd = {"lat": str(geo.latitude), "lng": str(geo.longitude)}

    return crd

def makeGeo(address):
    newaddress = address
    while True:
        try:
            crd = geoCoding(newaddress)
            if crd is not None:
                break
        except:
            words = newaddress.split()
            newaddress = " ".join(words[:-1])
            continue

    return crd

def makeCalendarStr(nowYear,nowMonth,nowMday,i):
    newNowYear = nowYear
    newNowMonth = nowMonth-i
    newNowMday = nowMday
    if newNowMonth<=0:
        newNowYear -= 1
        newNowMonth = 12+newNowMonth
    if newNowMonth<10:
        newNowMonth='0'+str(newNowMonth)
    if newNowMday<10:
        newNowMday='0'+str(newNowMday)
    return str(newNowYear)+str(newNowMonth)+str(newNowMday)

