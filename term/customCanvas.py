from tkinter import *
from tkinter import font
from animal import *
from utils import *
import tkWindow

# 이미지 출력을 위한 모듈
from PIL import ImageTk, Image
import requests
import io

# 지도 출력을 위한 모듈
from threading import Thread
import sys
import folium
from cefpython3 import cefpython as cef

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
FONT10 = None
FONT12 = None
FONT14 = None
FONT16 = None
LIST_VIEW_HEIGHT = 220

S_IMAGE_SIZE = 200
M_IMAGE_SIZE = 250
L_IMAGE_SIZE = 300


# 이름이 라벨일뿐 캔버스로 써도 되고..
# 이걸 mainFrame 오른쪽 위에 노트북으로 처리하면 될듯
class SimpleViewCanvas:
    errorMsg = None  # 오류메시지
    reqNo = None  # 요청번호
    resultCode = None  # 결과코드
    resultMsg = None  # 결과메세지
    desertionNo = None  # 유기번호
    filename = None  # 썸네일 이미지
    happenDt = None  # 접수일
    happenPlace = None  # 발견장소
    kindCd = None  # 품종
    colorCd = None  # 색상
    age = None  # 나이
    weight = None  # 체중
    noticeNo = None  # 공고번호
    noticeSdt = None  # 공고시작일
    noticeEdt = None  # 공고종료일
    popfile = None  # 고화질 Image
    processState = None  # 상태
    sexCd = None  # 성별
    neuterYn = None  # 중성화여부
    specialMark = None  # 특징
    careNm = None  # 보호소이름
    careTel = None  # 보호소전화번호
    careAddr = None  # 보호장소
    orgNm = None  # 관할기관
    chargeNm = None  # 담당자
    officetel = None  # 담당자연락처
    noticeComment = None  # 특이사항
    numOfRows = None  # 한 페이지 결과 수
    pageNo = None  # 페이지 번호
    totalCount = None  # 전체 결과 수
    canvas = None
    image = None
    master = None
    animal = None

    Window = None

    def __init__(self, master):
        self.master = master
        self.master_master = master.master
        self.animal = None

    def destroy(self):
        self.canvas.destroy()

    def state(self):
        self.canvas.state()

    def pack(self, side=None):
        if side is None:
            self.canvas.pack()
            return
        self.canvas.pack(side=side)

    def grid(self, row, column):
        self.canvas.grid(row=row, column=column)

    def clearContent(self):
        self.animal = None
        self.kindCd['text'] = ''
        self.age['text'] = ''
        self.specialMark['text'] = ''
        self.careNm['text'] = ''
        self.careAddr['text'] = ''
        self.careTel['text'] = ''

    def setContent(self, animal):
        self.animal = animal
        self.kindCd['text'] = animal.kindCd
        self.age['text'] = animal.age
        self.specialMark['text'] = animal.specialMark
        self.careNm['text'] = animal.careNm
        self.careAddr['text'] = animal.careAddr
        self.careTel['text'] = animal.careTel

    def clearImage(self):
        self.image.configure(image='')

    def setImage(self, animal, ordPage=0, curPage=0, size=S_IMAGE_SIZE):
        if ordPage != curPage:
            return False
        try:
            imageGet = requests.get(animal.filename, stream=True)
            if ordPage != curPage: # 시간 걸리는 작업이므로 한번더 검사, 멀티쓰레딩이라도 참조이기에 가능한 검사
                return False
            imageSet = imageGet.content
            img = Image.open(io.BytesIO(imageSet))
            img = img.resize((size, size), Image.ANTIALIAS)
            imgTk = ImageTk.PhotoImage(img)
            self.image.configure(image=imgTk)
            self.image.image = imgTk
        except:
            return False
        return True

    def setHighImage(self, animal, ordPage=0, curPage=0, size=L_IMAGE_SIZE):
        if ordPage != curPage:
            return False
        try:
            imageGet = requests.get(animal.popfile, stream=True)
            if ordPage != curPage:  # 시간 걸리는 작업이므로 한번더 검사, 멀티쓰레딩이라도 참조이기에 가능한 검사
                return False
            imageSet = imageGet.content
            img = Image.open(io.BytesIO(imageSet))
            img = img.resize((size, size), Image.ANTIALIAS)
            imgTk = ImageTk.PhotoImage(img)
            self.image.configure(image=imgTk)
            self.image.image = imgTk
        except:
            print("이미지 파일이 너무 큼")
            self.setHighImage(animal, ordPage=ordPage, curPage=curPage, size=size)
            return False
        return True


class ListViewCanvas(SimpleViewCanvas):
    def __init__(self, master, width=0, height=0, x=0, y=0):
        super().__init__(master)
        # (int(self.Window.mainScrollbar['width']))
        self.canvas = Canvas(master, relief="groove", borderwidth=5, bg='cornsilk1', width=width - 35,
                             height=height)  # 스크롤바 두께만큼 작게함
        # self.master.create_window(x, y, anchor="nw", window=self.canvas)

        # X 라벨 배치
        self.image = Label(self.canvas, image='')
        self.kindCd = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.age = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.specialMark = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careNm = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careAddr = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careTel = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.canvas.create_window(10, 10, anchor="nw", window=self.image)
        self.canvas.create_window(230, 10, anchor="nw", window=self.kindCd)
        self.canvas.create_window(230, 40, anchor="nw", window=self.age)
        self.canvas.create_window(230, 70, anchor="nw", window=self.specialMark)
        self.canvas.create_window(230, 100, anchor="nw", window=self.careNm)
        self.canvas.create_window(230, 130, anchor="nw", window=self.careAddr)
        self.canvas.create_window(230, 160, anchor="nw", window=self.careTel)

        # 사진 클릭으로 동물에 대한 자세한 출력
        self.scrollBind()
        self.image.bind("<Button-1>", lambda event: self.Window.popUpCanvas.show(self.animal))

    def scrollBind(self):
        self.canvas.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))
        self.image.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))
        self.kindCd.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))
        self.age.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))
        self.careNm.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))
        self.careAddr.bind("<MouseWheel>", lambda event: scroll_canvas(event, self.master_master))


class GridViewCanvas(SimpleViewCanvas):
    pass


class PopUpCanvas(SimpleViewCanvas):
    def __init__(self, master, width=0, height=0, x=0, y=0):
        super().__init__(master)
        self.animal = Animal()
        self.x = x
        self.y = y
        self.canvas = Canvas(master, relief="groove", borderwidth=5, bg='lightgray', width=width,
                             height=height)  # 스크롤바 두께만큼 작게함
        # X 버튼
        self.hide()
        self.exitButton = Button(text=" X ", command=self.hide)
        self.canvas.create_window(width - 23, 10, anchor="nw", window=self.exitButton)

        # X 라벨 배치
        self.image = Label(self.canvas, image='')
        self.kindCd = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.age = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.specialMark = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careNm = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careAddr = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.careTel = Label(self.canvas, font=FONT10, text='', height=1, bg='cyan')
        self.canvas.create_window(10, 10, anchor="nw", window=self.image)
        self.canvas.create_window(330, 10, anchor="nw", window=self.kindCd)
        self.canvas.create_window(330, 40, anchor="nw", window=self.age)
        self.canvas.create_window(330, 70, anchor="nw", window=self.specialMark)
        self.canvas.create_window(330, 100, anchor="nw", window=self.careNm)
        self.canvas.create_window(330, 130, anchor="nw", window=self.careAddr)
        self.canvas.create_window(330, 160, anchor="nw", window=self.careTel)

        # 목록 추가 제거 버튼
        self.addButton = Button(text="", font=FONT10)
        self.canvas.create_window(330, 200, anchor="nw", window=self.addButton)

        self.image.bind("<Button-1>", lambda event: webOpen(self.animal.popfile))

        # 지도용 frame
        map_height = height - 320 + 5  # 왜 5를 더해야 맞는지는 모르겠음
        self.mapFrame = Frame(self.canvas, width=width, height=map_height)
        self.canvas.create_window(5, 320, anchor="nw", window=self.mapFrame)
        thread = Thread(target=self.setMap)
        thread.daemon = True
        thread.start()

    def hide(self):
        self.master.create_window(-2000, -2000, anchor="nw", window=self.canvas)  # 그냥 이상한데 숨기는거임
        pass

    def show(self, animal):
        self.master.create_window(self.x, self.y, anchor="nw", window=self.canvas)
        if self.animal.isSame(animal):
            return
        self.setContent(animal)
        self.clearImage()
        thread1 = Thread(target=lambda: self.setHighImage(self.animal))
        thread1.daemon = True
        thread2 = Thread(target=self.changeMap)
        thread2.daemon = True
        thread1.start()
        thread2.start()
        # 버튼 정하기
        found = False
        for i in range(len(self.Window.interestAnimals)):
            if self.animal.isSame(self.Window.interestAnimals[i]):
                found = True
                self.addButton.configure(text="관심 목록에서 제거", command=lambda: self.removeInterestAnimals(i))
                break
        if not found:
            self.addButton.configure(text="관심 목록에 등록", command=self.addInterestAnimals)

    def setMap(self):
        sys.excepthook = cef.ExceptHook
        window_info = cef.WindowInfo(self.mapFrame.winfo_id())
        window_info.SetAsChild(self.mapFrame.winfo_id(), [0, 0, self.mapFrame['width'], self.mapFrame['height']])
        m = folium.Map(location=[37.3402849, 126.7313189], zoom_start=13)
        folium.Marker([37.3402849, 126.7313189], popup='초기화').add_to(m)
        m.save('map.html')
        cef.Initialize()
        self.browser = cef.CreateBrowserSync(window_info, url='file:///map.html')
        cef.MessageLoop()
        cef.Shutdown()

    def changeMap(self):
        #여기에 지도 url 또는 html 만들기 코드 추가하면 됨.
        crd = makeGeo(self.animal.careAddr)
        m = folium.Map(location=[crd['lat'], crd['lng']], zoom_start=13)
        folium.Marker([crd['lat'], crd['lng']], popup='보호중').add_to(m)
        m.save('map.html')
        self.browser.Reload()
        #self.browser.GetMainFrame().LoadUrl("https://map.kakao.com/"+crd['lat']+crd['lng'])#sample
        pass

    def addInterestAnimals(self):
        self.Window.interestAnimals.insert(0, self.animal)
        canvas = ListViewCanvas(self.Window.interestMainFrame, width=WINDOW_WIDTH, height=LIST_VIEW_HEIGHT, x=0, y=0)
        canvas.grid(row=0, column=0)
        canvas.setContent(self.animal)
        self.Window.interestCanvases.insert(0, canvas)
        for j in range(1, len(self.Window.interestCanvases)):
            self.Window.interestCanvases[j].grid(row=j, column=0)
            #self.Window.interestMainCanvas.create_window(0, (j) * LIST_VIEW_HEIGHT, anchor="nw", window=self.Window.interestCanvases[j].canvas)
        thread = Thread(target=lambda: canvas.setImage(self.animal))
        thread.daemon = True
        thread.start()
        self.addButton.configure(text="관심 목록에서 제거")
        self.addButton.configure(command=lambda: self.removeInterestAnimals(0))

        self.Window.interestMainCanvas.config(scrollregion=self.Window.interestMainCanvas.bbox("all"))

        pass

    def removeInterestAnimals(self, i):
        self.Window.interestAnimals.pop(i)
        canvas = self.Window.interestCanvases.pop(i)
        canvas.destroy()
        # for j in range(i, len(self.Window.interestCanvases)):
        #     self.Window.interestMainCanvas.create_window(0, (j) * LIST_VIEW_HEIGHT, anchor="nw",
        #                                                  window=self.Window.interestCanvases[j].canvas)
        self.addButton.configure(text="관심 목록에 등록")
        self.addButton.configure(command=self.addInterestAnimals)

        self.Window.interestMainCanvas.config(scrollregion=self.Window.interestMainCanvas.bbox("all"))
        pass

# 상세 보기 라벨, 이거 자체에 지도를
class DetaileVeiwCanvas(SimpleViewCanvas): # 결국 귀찮아서 안만들었다고 한다...
    def __init__(self, master):
        super().__init__(master)

    pass
