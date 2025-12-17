import xml.etree.ElementTree as ET
import tkinter.ttk
from tkinter import font
from customCanvas import *
from requestValue import *
#graph 관련 모듈
import time

#c연동
import average


# 텍스트 배율 가져오기
class TkWindow:
    def __init__(self):
        global FONT10, FONT12, FONT14, FONT16
        self.window = Tk()
        SimpleViewCanvas.Window = self
        scaling_factor = get_windows_text_scaling()  # 윈도우 텍스트 배율 받아옴
        FONT10 = font.Font(size=int(10.0 / scaling_factor), family='Helvetica')  # font설정은 Tk()생성자 이후에만 할 수 있음. 불편...
        FONT12 = font.Font(size=int(12.0 / scaling_factor), family='Helvetica')
        FONT14 = font.Font(size=int(14.0 / scaling_factor), family='Helvetica')
        FONT16 = font.Font(size=int(16.0 / scaling_factor), family='Helvetica')
        self.window.geometry(str(WINDOW_WIDTH) + "x" + str(WINDOW_HEIGHT) + "+100+40")  # 마지막은 윈도우 시작 위치
        self.window.title("BohoBada")
        self.window.configure(bg='light salmon')
        self.rootCanvas = Canvas(self.window, bg='light salmon')
        self.rootCanvas.pack(expand=True, fill="both")
        self.ListViewCanvases = []
        self.animals = []
        self.animalsPrev = []  # 이전 10페이지 분량의 동물들 쓰레드로 읽을것임
        self.animalsNext = []  # 다음 10페이지 분량의 동물들
        self.animalsNextReady = False
        self.animalsPrevReady = False
        self.interestAnimals = []
        self.interestCanvases = []
        self.root = None
        self.totalCount = 0  # len(self.animals)과는 다름, 페이지와 상관없이 검색 조건에 해당되는 모든 동물의 수
        self.numOfPage = 16  # 한페이지에 표시할 수
        self.curPage = 1
        self.lastPage = 1
        self.rqValue = RequestValue(self.numOfPage)  # 페이지의 10배만큼 읽음.
        self.Searchdog_reg_no = StringVar() #등록 검색
        self.Searchowner_birth = StringVar()
        self.SearchResult = []

        self.TabBar = tkinter.ttk.Notebook(self.rootCanvas)
        self.TabBar.pack(side="top", expand=True, fill="both")

        self.inquiryCanvas = Canvas(self.rootCanvas, bg='light salmon')
        self.TabBar.add(self.inquiryCanvas, text="조회")
        self.regiSearchCanvas = Canvas(self.rootCanvas, bg='light salmon')
        self.TabBar.add(self.regiSearchCanvas, text="등록검색")
        self.interestCanvas = Canvas(self.rootCanvas, bg='light salmon')
        self.TabBar.add(self.interestCanvas, text="관심목록")
        # 아래 tabChanged
        self.TabBar.bind("<<NotebookTabChanged>>", self.tabChanged)
        # 조회에 관한 실행

        self.setCategoriCanvas(self.inquiryCanvas)
        self.setMainCanvas(self.inquiryCanvas)  # selectViewMode Notebook 추가 예정
        self.setPageCanvas(self.inquiryCanvas)
        self.setAndPrint()  # 이걸 init에서 해줘야 초기에 값이 나오는데 프로그램 실행이 느려짐

        # 등록검색에 관한 실행
        #self.setSearchCanvas(self.regiSearchCanvas)
        self.setSearchFrame(self.regiSearchCanvas)
        t = Thread(target=lambda: self.setGraph(self.graphCanvas))
        t.daemon = True
        t.start()
        # 관심목록에 관한 실행
        self.setInterestFrame(self.interestCanvas)
        #동시에 검색을 하게 돼서 스레드로 뺌

        # 상세보기 탭에 들어갈 프레임 껍데기 만들어줘야함

        self.popUpCanvas = PopUpCanvas(self.rootCanvas, width=WINDOW_WIDTH * 2 / 3, height=WINDOW_HEIGHT * 0.88,
                                       x=WINDOW_WIDTH * 1 / 3 * 0.5, y=WINDOW_HEIGHT * 0.05)

        self.window.mainloop()
        cef.Shutdown()

    # tab변경 시 화면 변경
    # 이거를 사용하면 탭 마다 위젯만 추가 제거하는 식으로 실행
    # 미세한 차이의 성능 저하, 큰 영향 없음
    def tabChanged(self, tab):
        selectedTab = tab.widget.select()
        currentTab = tab.widget.tab(selectedTab, "text")
        if currentTab == "조회":
            print("inquiry")
            self.popUpCanvas.hide()
            pass
        elif currentTab == "등록검색":
            print("regiSearch")
            self.popUpCanvas.hide()
            pass
        elif currentTab == "관심목록":
            print("interest")
            self.popUpCanvas.hide()
            pass

    def setRoot(self):
        self.rqValue.setParams()
        self.response = self.rqValue.getValue()
        print(self.response.url)
        if self.response.status_code == 200:  # 성공했을때
            self.root = ET.fromstring(self.response.text)  # 루트 세팅!
            return True
        return False  # 실패

    def setAnimals(self):
        if not self.setRoot():
            print("읽는데 실패함")
            return
        self.animals.clear()
        for item in self.root.iter("item"):
            self.animals.append(Animal(item))

    def setAnimalsPrev(self):
        self.animalsPrev.clear()
        self.animalsPrevReady = False
        rqPageNo = (self.curPage + 9) // 10  # 현재 보고있는 animals의 페이지 요청변수
        if rqPageNo <= 1:
            print("미리 읽을 이전 페이지가 없음")
            return
        self.rqValue.pageNo = rqPageNo - 1
        if not self.setRoot():
            print("읽는데 실패함")
            return
        if self.animalsPrev:  # 읽어오는 사이에 다시 다음으로 넘어가서 animalsPrev에 animals의 값이 복사되어버렸으면. 다음 작업이 덮어쓰기가 되버림
            self.animalsPrevReady = True
            return
        for item in self.root.iter("item"):
            self.animalsPrev.append(Animal(item))
        self.animalsPrevReady = True

    def setAnimalsNext(self):
        self.animalsNext.clear()  # 일단 밀어버림
        self.animalsNextReady = False
        rqPageNo = (self.curPage + 9) // 10  # 현재 보고있는 animals의 페이지 요청변수
        if self.totalCount < rqPageNo * self.numOfPage * 10:  # 읽어올 다음 페이지가 없으면
            print("미리 읽을 다음 페이지가 없음")
            return
        self.rqValue.pageNo = rqPageNo + 1
        if not self.setRoot():
            print("읽는데 실패함")
            return
        if self.animalsNext:  # 읽어오는 사이에 다시 이전으로 돌아가서 animalsNext에 animals의 값이 복사되어버렸으면. 다음 작업이 덮어쓰기가 되버림
            self.animalsNextReady = True
            return
        for item in self.root.iter("item"):
            self.animalsNext.append(Animal(item))
        self.animalsNextReady = True

    def setAndPrint(self):
        self.rqValue.pageNo = 1  # 출력을 이용하면 조건을 변경하지 않았어도 첫페이지로
        self.curPage = 1
        self.setAnimals()
        for item in self.root.iter("body"):  # body는 하나라서 반복은 한번만 함. 반복문 안쓰는법을 모름 ㅋ
            self.totalCount = int(item.findtext("totalCount"))  # 총 개수를 받아옴
            self.lastPage = (self.totalCount + self.numOfPage - 1) // self.numOfPage  # 마지막 페이지 정의
        print("검색 기준 마지막 페이지는 ", self.lastPage)
        thread = Thread(target=self.setAnimalsNext)  # 다음페이지 애니멀 세팅
        thread.daemon = True
        thread.start()
        self.pageLabel['text'] = str(self.curPage)
        self.prevButton['state'] = 'normal'
        self.nextButton['state'] = 'normal'
        self.printListView()

    def disablePrevNext(self):
        self.prevButton['state'] = 'disable'
        self.nextButton['state'] = 'disable'

    def printListView(self):
        self.mainScrollbar.set(0, 0)  # 스크롤바의 위치를 맨 위로 설정
        self.mainCanvas.yview_moveto(0)
        i = 0  # 라벨 인덱스
        curPageFirstIndex = (self.curPage - 1) % 10 * self.numOfPage
        curPageCount = min(self.numOfPage, len(self.animals) - curPageFirstIndex)
        # print(curPageFirstIndex, curPageCount, len(self.animals))
        thread = Thread(target=self.loadCurPageThumbnail, args=(curPageFirstIndex, curPageCount))
        thread.daemon = True
        thread.start()
        while i < curPageCount:
            self.ListViewCanvases[i].setContent(self.animals[curPageFirstIndex + i])
            self.ListViewCanvases[i].clearImage()  # 일단 이미지 싹 밀어버림
            i += 1
        while i < self.numOfPage:  # 페이지의 라벨 수보다 동물이 적으면 공백
            self.ListViewCanvases[i].clearContent()
            self.ListViewCanvases[i].clearImage()
            i += 1

    # 두 개의 함수로 나눠서 스레드 사용 after(0, )으로 예약을 걸어둬 실행시키는 방식
    def loadCurPageThumbnail(self, curPageFirstIndex, curPageCount):
        i = 0  # 라벨 인덱스
        ordPage = self.curPage
        while i < curPageCount:
            # 페이지 빨리 넘기면 이전 쓰레드 남아서 덮어쓰기든 없어야하는데 나오는등 문제 발생함, setImage에서 False 반환하도록 수정함
            if not self.ListViewCanvases[i].setImage(self.animals[curPageFirstIndex + i], ordPage, self.curPage, size=S_IMAGE_SIZE):
                # print(i, ordPage, self.curPage)#참조 전달이라 제대로 먹는듯
                return
            i += 1
        while i < self.numOfPage:  # 페이지의 라벨 수보다 동물이 적으면 공백
            if ordPage != self.curPage:
                return
            self.ListViewCanvases[i].clearImage()
            i += 1

    def prevPage(self):
        if self.curPage <= 1:
            print("첫 페이지 입니다.")
            return
        self.curPage -= 1
        if self.curPage % 10 == 0:  # 11->10, 21->20, 31->30
            if not self.animalsPrevReady:
                self.curPage += 1
                print('기다려!')
                return
            self.animalsNext = self.animals.copy()
            self.animalsNextReady = True
            self.animals = self.animalsPrev.copy()
            # print(len(self.animalsPrev), len(self.animals), len(self.animalsNext))
            thread = Thread(target=self.setAnimalsPrev)
            thread.daemon = True
            thread.start()


        self.pageLabel['text'] = str(self.curPage)
        self.printListView()

    def nextPage(self):
        if self.curPage >= self.lastPage:
            print("마지막 페이지 입니다.")
            return
        self.curPage += 1
        if self.curPage % 10 == 1:  # 10->11, 20->21, 30->31
            if not self.animalsNextReady:
                self.curPage -= 1
                print('기다려!')
                return
            self.animalsPrev = self.animals.copy()  # 이동연산을 못하는것이 파이썬의 한계인가...
            self.animalsPrevReady = True
            self.animals = self.animalsNext.copy()
            # print(len(self.animalsPrev), len(self.animals), len(self.animalsNext))
            thread = Thread(target=self.setAnimalsNext)
            thread.daemon = True
            thread.start()

        self.pageLabel['text'] = str(self.curPage)
        self.printListView()

    def setGraph(self, Canvas):
        now = time
        nowYear = now.localtime().tm_year
        nowMonth = now.localtime().tm_mon
        nowMday = now.localtime().tm_mday
        bar_width = 60
        x_gap = 30
        x0 = 60
        y0 = 300
        max_level = 3000
        totalList = []
        for i in range(12):
            nowBgnde = makeCalendarStr(nowYear,nowMonth,nowMday,i+1)
            nowEndde = makeCalendarStr(nowYear,nowMonth,nowMday,i)
            totalList.append(getTotal(nowBgnde,nowEndde))
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 60 * totalList[i]//max_level
            Canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='peach puff')
            Canvas.create_text(x1, y0 + 5, text=str(nowEndde), anchor='n')
            Canvas.create_text(x1 + int(bar_width//2), y1 - 10, text=str(totalList[i]), anchor='s')
        totalaver = average.average(totalList)
        Canvas.create_text(600, 0, text='월 단위 유기동물 수', fill='cyan',font=FONT14, anchor='n')
        Canvas.create_text(600, 20, text='평균 : '+str(int(totalaver)), fill='cyan',font=FONT14, anchor='n')
    def setCategoriCanvas(self, master):
        self.categoryFrame = Frame(master)
        self.categoryFrame.pack()

        row_count = 0
        Label(self.categoryFrame, font=FONT10, text='검색 시작일', width=10).grid(row=row_count, column=0)
        Entry(self.categoryFrame, font=FONT10, textvariable=self.rqValue.bgnde, justify=RIGHT, width=10).grid(
            row=row_count, column=1)
        Label(self.categoryFrame, font=FONT10, text='검색 종료일', width=10).grid(row=row_count, column=2)
        Entry(self.categoryFrame, font=FONT10, textvariable=self.rqValue.endde, justify=RIGHT, width=10).grid(
            row=row_count, column=3)
        row_count += 1

        Radiobutton(self.categoryFrame, font=FONT10, text='전체', variable=self.rqValue.upkind, value=' ',
                    command=self.disablePrevNext).grid(row=row_count, column=0)
        Radiobutton(self.categoryFrame, font=FONT10, text='개', variable=self.rqValue.upkind, value='417000',
                    command=self.disablePrevNext).grid(row=row_count, column=1)
        Radiobutton(self.categoryFrame, font=FONT10, text='고양이', variable=self.rqValue.upkind, value='422400',
                    command=self.disablePrevNext).grid(row=row_count, column=2)
        Radiobutton(self.categoryFrame, font=FONT10, text='기타', variable=self.rqValue.upkind, value='429900',
                    command=self.disablePrevNext).grid(row=row_count, column=3)
        row_count += 1

        Radiobutton(self.categoryFrame, font=FONT10, text='전체', variable=self.rqValue.state, value=' ',
                    command=self.disablePrevNext).grid(row=row_count, column=0)
        Radiobutton(self.categoryFrame, font=FONT10, text='공고중', variable=self.rqValue.state, value='notice',
                    command=self.disablePrevNext).grid(row=row_count, column=1)
        Radiobutton(self.categoryFrame, font=FONT10, text='보호중', variable=self.rqValue.state, value='protect',
                    command=self.disablePrevNext).grid(row=row_count, column=2)
        row_count += 1

        self.setAndPrintButton = Button(self.categoryFrame, font=FONT10, text='출력', command=self.setAndPrint)
        self.setAndPrintButton.grid(row=row_count, column=0)

        return self.categoryFrame

    def setMainCanvas(self, master):
        self.mainScrollbar = Scrollbar(master, orient="vertical")
        self.mainScrollbar.pack(side="right", fill="y")
        self.mainCanvas = Canvas(master, width=WINDOW_WIDTH, bg='light salmon',yscrollcommand=self.mainScrollbar.set)
        self.mainCanvas.pack(expand=True, side="top", fill="both")
        self.mainScrollbar.config(command=self.mainCanvas.yview)
        self.mainFrame = Frame(self.mainCanvas)
        self.mainCanvas.create_window(0, 0, window=self.mainFrame, anchor='nw')
        self.mainFrame.bind('<Configure>', lambda event: on_configure(event, self.mainCanvas))
        for i in range(self.numOfPage):
            canvas = ListViewCanvas(self.mainFrame, width=WINDOW_WIDTH, height=LIST_VIEW_HEIGHT, y=i * 200)
            canvas.grid(row=i, column=0)
            self.ListViewCanvases.append(canvas)

        #self.mainCanvas.config(scrollregion=self.mainCanvas.bbox("all"))

        return self.mainCanvas

    def setPageCanvas(self, master):
        self.pageFrame = Frame(master)
        self.pageFrame.pack(side="bottom")
        self.prevButton = Button(self.pageFrame, font=FONT10, text='이전', command=self.prevPage)
        self.prevButton.grid(row=0, column=0)
        self.pageLabel = Label(self.pageFrame, font=FONT10, text=str(self.curPage), width=8)
        self.pageLabel.grid(row=0, column=1)
        self.nextButton = Button(self.pageFrame, font=FONT10, text='다음', command=self.nextPage)
        self.nextButton.grid(row=0, column=2)

        return self.pageFrame

    def setSearchFrame(self, master):
        self.SearchMainCanvas = Canvas(master, width=WINDOW_WIDTH ,bg='light salmon')
        self.SearchMainCanvas.pack(expand=True, side="top", fill="both")

        row_count = 0
        Label(self.SearchMainCanvas, font=FONT10, text='동물등록번호', width=10).place(
            x=300,y=30)
        Entry(self.SearchMainCanvas, font=FONT10, textvariable=self.Searchdog_reg_no, justify=RIGHT, width=20).place(
            x=390, y=30)
        Label(self.SearchMainCanvas, font=FONT10, text='소유자 생년월일', width=13).place(
            x=550, y=30)
        Entry(self.SearchMainCanvas, font=FONT10, textvariable=self.Searchowner_birth, justify=RIGHT, width=20).place(
            x=670, y=30)

        for i in range(5):
            self.SearchResult.append(Label(self.SearchMainCanvas, font=FONT16, text='', width=50,bg='peach puff'))

        self.setAndPrintButton = Button(self.SearchMainCanvas, font=FONT10, text='검색',
                                        command=lambda: setSearchRq(self.Searchdog_reg_no, self.Searchowner_birth,self.SearchResult))
        self.setAndPrintButton.place(x=870, y=30)
        row_count += 1

        for i in range(5):
            self.SearchResult[i].place(x=300, y=70+i*45)

        self.graphCanvas = Canvas(master,width=WINDOW_WIDTH,bg='light salmon')
        self.graphCanvas.pack(expand=True, side="top",fill="both")
        return self.SearchMainCanvas

    def setInterestFrame(self, master):
        self.interestMainScrollbar = Scrollbar(master, orient="vertical")
        self.interestMainScrollbar.pack(side="right", fill="y")
        self.interestMainCanvas = Canvas(master, width=WINDOW_WIDTH, bg='light salmon', yscrollcommand=self.interestMainScrollbar.set)
        self.interestMainCanvas.pack(expand=True, side="top", fill="both")
        self.interestMainScrollbar.config(command=self.interestMainCanvas.yview)
        self.interestMainFrame = Frame(self.interestMainCanvas)
        self.interestMainCanvas.create_window(0, 0, window=self.interestMainFrame, anchor='nw')
        self.interestMainFrame.bind('<Configure>', lambda event: on_configure(event, self.interestMainCanvas))

        return self.interestMainCanvas
