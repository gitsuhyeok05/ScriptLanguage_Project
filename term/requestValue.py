from tkinter import StringVar
import xml.etree.ElementTree as ET
import requests
url = 'http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic'
service_key = "Bst8DsrxQ7RorD2aw2vb4FGO7mfU4MQ7yrH/SYzAN6hYr5OaDJZDV4fYUgUjGtexpTALuChYvNgqV5Uhc8+SgQ=="

url1 = 'https://apis.data.go.kr/1543061/animalInfoSrvc/animalInfo'
service_key1 = "EqR/QnVxnMELK13ieeIC/IHSz6q2ANxJLi5IJCtyGR2mw1149RbLOOSa9IyzAxsma4H66LwRumQEV26v8JYlqw=="
class RequestValue:
    def __init__(self, numOfPage):
        self.numOfRows = 10 * numOfPage
        self.pageNo = 1
        self.queryParams = {'serviceKey': service_key, 'numOfRows': str(self.numOfRows), 'pageNo': str(self.pageNo)}

        self.bgnde = StringVar()
        self.endde = StringVar()
        self.upkind = StringVar()
        self.upkind.set(' ') # 라디오박스에 쓸거면 ''같은 빈문자열은 안되고 쓰레기 값이라도 있어야함 그래서 공백 한칸 씀
        self.careAddr = StringVar()
        self.state = StringVar()
        self.state.set(' ')


    def setParam(self, key, value):
        if value and value != ' ': # 값이 있으면, 공백 제거로 할 수도 있지만 이게 더 빠를듯
            self.queryParams[key] = value
        else: #
            self.queryParams.pop(key, None) # 없으면 None이 반환되는데 딱히 반환값은 필요 없음

    def setParams(self):
        self.setParam('bgnde', self.bgnde.get())
        self.setParam('endde', self.endde.get())
        self.setParam('upkind', self.upkind.get())
        self.setParam('state', self.state.get())
        # 지역코드 set 추가해야함

        self.setParam('numOfRows', str(self.numOfRows))
        self.setParam('pageNo', str(self.pageNo))
    def getValue(self):
        return requests.get(url, params=self.queryParams)

#오직 그래프를 위한 totalcount 구하기
#numOfRows가 1개부터 검색가능 totalcount는 제대로 나옴
def getTotal(bgnde,endde):
    params = {'serviceKey': service_key,'bgnde':str(bgnde),'endde':str(endde), 'numOfRows': str(1), 'pageNo': str(1)}
    response = requests.get(url,params=params)
    root = ET.fromstring(response.content)
    totalCount = root.find("body").find("totalCount").text
    return int(totalCount)


def setSearchRq(rfid, name, result):
    print(rfid.get(), name.get())
    for i in range(5):
        result[i].configure(text="")
    if rfid and name:
        params = {'serviceKey': service_key1, 'dog_reg_no': str(rfid.get()), 'owner_birth': str(name.get())}
        print(params)
        response = requests.get(url1,params=params)
        root = ET.fromstring(response.content)
        if root.find("body").find("item"):
            result[0].configure(text="등록번호 : "+root.find("body").find("item").find("dogRegNo").text)
            result[1].configure(text="이름 : "+root.find("body").find("item").find("dogNm").text)
            result[2].configure(text="성별 : "+root.find("body").find("item").find("sexNm").text)
            result[3].configure(text="품종 : "+root.find("body").find("item").find("kindNm").text)
            result[4].configure(text="중성화 여부 : "+root.find("body").find("item").find("neuterYn").text)
        else:
            result[0].configure(text="없는 결과입니다.")
    else:
        result[0].configure(text="빈칸을 채워주세요.")

