from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import  pyautogui , time , os , re
import urllib.parse as rep
import urllib.request as req
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests as rq
from bs4 import BeautifulSoup as bs
import csv
from typing import Union
from conf import get_login_info

# CSV 클래스 정의
class SetCSV:
    def __init__(self):
        # 데이터 저장할 경로 지정하기
        self.savePath = os.path.abspath(f'인스타그램_{Application().keword}')
        self.imagePath = os.path.abspath(f"{self.savePath}/{self.savePath.split('_')[-1]}_이미지모음")
        self.fileName = f"{self.savePath.split('_')[-1]}.csv"

    def set_csv(self)-> any:
        # 이미지 저장할 경로 생성하기
        if not os.path.exists(self.savePath) :
            os.mkdir(self.savePath)

        if not os.path.exists(self.imagePath):
            os.mkdir(self.imagePath)

        f = open(os.path.join(self.savePath,self.fileName), 'w' , encoding='utf-8-sig' , newline='')

        return f


# 크롬드라이버 클래스 정의
class ChromeDriver:
    @staticmethod
    def set_driver():
        # options 객체
        chrome_options = Options()

        # headless Chrome 선언
        chrome_options.add_argument('--headless')

        # 브라우저 꺼짐 방지
        chrome_options.add_experimental_option('detach', True)

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.104 Whale/3.13.131.36 Safari/537.36")

        # 불필요한 에러메시지 없애기
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service(executable_path=ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)

        return browser

# 페이스북 로그인 클래스 정의
class Login:
    def __init__(self):
        self.BASEURL = 'https://www.instagram.com/'
        self.facebook_id = get_login_info('FACEBOOK_ID')
        self.facebook_pw = get_login_info('FACEBOOK_PW')
        self.browser = ChromeDriver().set_driver()

    def login(self)-> Union[None , int]:
        print('페이스북 로그인 중 ..')
        # 페이지 상태 체크
        response = rq.get(self.BASEURL)
        if response.status_code == 200:
            self.browser.get(self.BASEURL)
            self.browser.implicitly_wait(5)
            self.browser.maximize_window()

            id = self.facebook_id
            pw = self.facebook_pw
            try:
                # 페이스북으로 로그인하기 버튼 클릭
                fb_login = self.browser.find_element(By.CSS_SELECTOR, "button.sqdOP.yWX7d.y3zKF")
                self.browser.execute_script('arguments[0].click()', fb_login)
                time.sleep(1)

                # 페이스북 아이디 입력
                self.browser.find_element(By.CSS_SELECTOR, "input#email").send_keys(id)
                time.sleep(2)

                # 페이스북 패스워드 입력
                self.browser.find_element(By.CSS_SELECTOR, "input#pass").send_keys(pw)
                time.sleep(2)

                # 로그인 버튼 클릭
                login_btn = self.browser.find_element(By.CSS_SELECTOR, "button#loginbutton")
                self.browser.execute_script('arguments[0].click()', login_btn)
                time.sleep(2)

                # 페이지 잠깐 로딩
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

                # 알림설정 문구 뜨는 경우 : 설정 누르기
                try:
                    # 페이지 잠깐 로딩
                    WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.aOOlW.bIiDR')))

                    alarm_btn = self.browser.find_element(By.CSS_SELECTOR, "button.aOOlW.bIiDR")
                    self.browser.execute_script('arguments[0].click()', alarm_btn)
                    time.sleep(1)


                    print('\n\n페이스북 로그인이 완료되었습니다!\n')
                except:  # 알림설정 문구가 뜨지 않는경우
                    pass

                if "오류" in self.browser.find_element(By.CSS_SELECTOR, "body").text:
                    pyautogui.alert('페이지 오류!')
                    return 0

            except:  # 로그인 중 문제가 생긴 경우
                pyautogui.alert('로그인을 실패하였습니다!')
                return 0

        else:  # 페이지 status code가 200이 아닌경우
            pyautogui.alert(f"INSTAGRAM NOW PAGE STATUS CODE : {response.status_code} !!!")
            return 0

class Application:
    def __init__(self):
        self.browser = ChromeDriver().set_driver()
        self.keword : str = self.search_keword()
        self.URL : str = f'https://www.instagram.com/explore/tags/{rep.quote_plus(self.keword)}'


        # SetCSV 클래스의 객체 생성
        self.SetCSV = SetCSV()

        # 파일 객체 불러오기
        self.f = self.SetCSV.set_csv()

        # csv 객체 생성
        self.csvWriter = csv.writer(self.f)
        self.csvWriter.writerow(['닉네임','본문내용','해쉬태그','등록일','좋아요 수'])

    def run(self)-> None:
        # 페이스북 로그인하기
        login_result = Login().login()

        # login이 실패하지 않은 경우 아래 코드 실행
        if login_result != 0 :
            # 해시태그 페이지로 이동이 안되는 경우가 있음
            try:
                # 해시태그 페이지로 이동하기
                self.browser.get(url=self.URL)

                # 로딩 대기하기
                element = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.v1Nh3.kIKUG._bz0w > a'))
                )

                # 첫 번째 게시글 클릭하기
                a_tags = self.browser.find_elements(By.CSS_SELECTOR, 'div.v1Nh3.kIKUG._bz0w > a')[0]
                self.browser.execute_script('arguments[0].click()', a_tags)
                time.sleep(3)

                ## 수집할 게시물의 수 ##
                target_cnt = 5
                for i in range(1, target_cnt + 1):
                    try:
                        self.get_content(count=i)
                        self.move_next()
                    except:
                        print("DATA CRAWLING FAILED")
                        time.sleep(2)
                        self.move_next()

                # open 했던 f 객체 닫기
                self.f.close()
            except:
                pyautogui.alert('현재 페이지에 문제가 있습니다!')
                raise Exception('Page Error!')

    # 게시글 이동 메서드
    def move_next(self)-> None:
        next_btn = self.browser.find_element(By.CSS_SELECTOR, 'div.l8mY4.feth3 > button')
        self.browser.execute_script('arguments[0].click()', next_btn)
        time.sleep(2)

    # 게시글 추출 메서드
    def get_content(self,count)-> None:
        # 현재 드라이버의 페이지소스 파싱하기
        soup = bs(self.browser.page_source, 'html.parser')

        # 인스타그램 닉네임
        insta_nickname = soup.select('a.sqdOP.yWX7d._8A5w5.ZIAjV')[0]

        # 본문내용
        content = soup.select('div.MOdxS')[0]

        # 해쉬태그 가져오기
        hash_tag : list = content.select('a')
        # 해쉬태그 데이터의 '#' string 제거 -> List Comprehension 문법으로 작성
        hash_tag_list = str([re.sub('[#]', '', x.text.strip()) for x in hash_tag if len(hash_tag) > 0])

        # 게시글 등록일
        content_time = soup.select('time.FH9sR.RhOlS')[0]

        # 좋아요 개수
        like_cnt = soup.select_one('div._7UhW9.xLCgt.qyrsm.KV-D4.fDxYl.T0kll > span')

        # 이미지 가져오기 (여러 이미지가 있는 경우 썸네일만 가져옴)
        image = soup.select_one('div.pbNvD.QZZGH.bW6vo div.KL4Bh > img')

        if hash_tag_list != None or hash_tag_list and image != None:
            # 특수기호 , ' , " 없애기
            hash_tag_list = re.sub('[@\[\]\'"]', '', hash_tag_list)

            # content 분기처리
            if content == None or content.text == '':
                content = '-'
            else:
                content = content.text.strip()
                content = re.sub('#.*', '', content)

            # content_time 분기처리
            if content_time == None or content_time.text == '':
                content_time = '-'
            else:
                content_time = content_time.text.strip()

            # 인스타 닉네임 분기처리
            if insta_nickname == None or insta_nickname.text == '':
                insta_nickname = 'None'
            else:
                insta_nickname = insta_nickname.text.strip()

            if like_cnt == None or like_cnt.text == '':
                like_cnt = 0
            else:
                like_cnt = like_cnt.text.strip()
                like_cnt = int(re.sub('[,]', '', like_cnt))

            # 이미지 링크주소 추출하기
            image_link = image.attrs['src']

            # 이미지 파일명 지정하기
            fileName = os.path.join(self.SetCSV.imagePath, f'{count}.png')

            # 이미지 다운로드하기
            req.urlretrieve(image_link, fileName)

            # 열린 csv 파일에 데이터 옮겨담기
            self.csvWriter.writerow([insta_nickname, content, hash_tag_list, content_time, like_cnt])

            # 추출데이터 출력하기
            print(
                f"인스타그램 아이디 : {insta_nickname}\n본문내용 : {content}\n해쉬태그 : {hash_tag_list}\n등록일 : {content_time}\n좋아요 수 : {like_cnt}\n")

    # 키워드 입력 메서드
    def search_keword(self)-> str :
        while True:
            os.system('cls')
            keword : str = input('원하시는 키워드명을 입력해주세요\n\n:')

            if keword == "":
                pyautogui.alert("키워드 값이 정상적이지 않습니다")
                os.system('cls')
                continue

            if re.match('[0-9]', keword):
                print("입력이 올바르지 않습니다")
                os.system('cls')
                continue

            return keword


if __name__ == '__main__' :
    pass





