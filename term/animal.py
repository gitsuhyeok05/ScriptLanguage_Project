class Animal:
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
    #무엇을 보관하는게 맞을까, 다 해도 되고
    def __init__(self, item=None):
        if item is None:
            return
        self.filename   = item.findtext("filename")
        self.popfile    = item.findtext("popfile")#popfile이거 주소 보니까 filename 주소에서 _s이거 하나 차이네
        self.kindCd     = item.findtext("kindCd")
        self.age        = item.findtext("age")
        self.specialMark = item.findtext("specialMark")
        self.careNm     = item.findtext("careNm")
        self.careAddr   = item.findtext("careAddr")
        self.careTel = item.findtext("careTel")

    def getPopfile(self):
        return self.filename[:-6]+".jpg" # 이렇게 해도 되는줄 알았는데 어떤건 jepg로 다름 ㅋㅋ

    def getSimpleData(self):
        return self.kindCd + " / " + self.age + "\n" + self.specialMark + "\n"+ self.careNm + "\n" + self.careAddr + "\n"  + self.careTel + "\n" + self.filename +"\n"

    def isSame(self, animal):
        if self is animal:
            return True
        if self.filename == animal.filename:
            return True
        return False