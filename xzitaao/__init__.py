from PIL import Image
import pytesseract
import re
import requests
import time
import shutil
import lxml
from bs4 import BeautifulSoup
import os
from random import choice

ERROR_WRONG_CAPTCHA = "你输入的验证码错误，请您重新输入！"
ERROR_BUSY = "数据库忙请稍候再试"
ERROR_WRONG_PASSWORD = "你输入的证件号不存在，请您重新输入！"
WRONG_PWD = "密码错误"
SUCCESS = "选课成功！"

EVALUATE_ASS = ["老师讲的很好！", "好", "从老师那里学到了很多"]

PIC_FILE_PATH = r"pictures/"
CAPS_FILE_PATH = r"captcha/"
GRADE_FILE_PATH = r"grade/"
INFO_FILE_PATH = r"info/"
HOST = '211.87.126.78'
URL = r"http://" + HOST + r"/"
headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; Touch; .NET4.0C; .NET4.0E; Tablet PC 2.0; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
    'Connection': 'Keep-Alive',
    'Host': HOST
}


def auto_ip():
    global headers
    global URL
    global HOST
    ip_pool = ['211.87.126.77', '211.87.126.76', '211.87.126.78', '211.87.126.37']
    ip_pool.remove(HOST)
    HOST = choice(ip_pool)
    headers["HOST"] = HOST
    URL = r"http://" + HOST + r"/"
    print("change ip from pool", URL)


def test(r, count):
    data = r.content
    with open(count + '_test.html', 'wb') as f:
        f.write(data)
    print("test 已保存为 " + count + ".html")


def get_captcha(f, tesseract_dic):
    image = Image.open(f, "r")
    image = image.convert('L')
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if 140 <= pixels[x, y] <= 256:
                pixels[x, y] = 255
    testdata_dir_config = '--tessdata-dir ' + tesseract_dic
    captcha = pytesseract.image_to_string(image, lang='eng',
                                          config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 6")
    time.sleep(0.3)
    captcha = re.sub("\W", "", captcha)
    return captcha


class Student:
    sid = ''
    pwd = ''
    cid = ''
    status = ''
    session = None
    cookie = {'JSESSIONID': ''}
    set_tesseract_flag = False
    tesseract_dic = ""

    def __init__(self, sid, pwd, cid=''):
        self.sid = sid
        self.pwd = pwd
        self.cid = cid
        self.session = requests.Session()
        if not os.path.exists(PIC_FILE_PATH):
            os.makedirs(PIC_FILE_PATH)
        if not os.path.exists(CAPS_FILE_PATH):
            os.makedirs(CAPS_FILE_PATH)
        if not os.path.exists(GRADE_FILE_PATH):
            os.makedirs(GRADE_FILE_PATH)
        if not os.path.exists(INFO_FILE_PATH):
            os.makedirs(INFO_FILE_PATH)
        else:
            shutil.rmtree(CAPS_FILE_PATH)
            os.mkdir(CAPS_FILE_PATH)

    def set_tesseract_dic(self, tesseract_dic):
        # self.set_tesseract_flag = False
        if tesseract_dic:
            self.tesseract_dic = tesseract_dic
            self.set_tesseract_flag = True
        else:
            self.set_tesseract_flag = False

    def display(self):
        print(self.sid, self.pwd, self.cid)

    def login(self):
        global URL
        print("-------------------------")
        print("目前登录账号为", self.sid)
        r = self.session.get(URL, headers=headers)
        time.sleep(1)
        while True:
            # captcha = ''
            while True:
                time.sleep(1)
                r = self.session.get(URL + r'validateCodeAction.do', headers=headers)  # 取得验证码
                with open(CAPS_FILE_PATH + self.sid + 'capt.png', 'wb') as f:
                    f.write(r.content)
                if self.set_tesseract_flag:
                    with open(CAPS_FILE_PATH + self.sid + 'capt.png', 'rb') as f:
                        captcha = get_captcha(f, self.tesseract_dic)
                else:
                    with Image.open(CAPS_FILE_PATH + self.sid + 'capt.png') as f:
                        f.show()
                        captcha = input("请输入验证码:")
                    # f.close()
                self.cookie['JSESSIONID'] = r.cookies.get('JSESSIONID')
                if len(captcha) == 4:
                    break
            data = {
                'dzslh': '',
                'eflag': '',
                'evalue': '',
                'fs': '',
                'lx': '',
                'mm': self.pwd,
                'tips': '',
                'v_yzm': captcha,
                'zjh': self.sid,
                'zjh1': ''
            }
            time.sleep(1)
            r = self.session.post(URL + "loginAction.do", data=data, headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            flag = soup.find("font", {"color": "#990000"})
            if flag is not None:
                print("截取到网页消息：", flag.get_text())

            if flag is None:
                if r.status_code == 200:
                    print("密码正确")
                    return True
                else:
                    continue
            elif flag.get_text() == ERROR_WRONG_CAPTCHA:
                # print("验证码错误，正在重试")
                continue
            elif flag.get_text() == ERROR_WRONG_PASSWORD:
                print("密码错误")
                return False
            elif flag.get_text() == ERROR_BUSY:
                # print(ERROR_BUSY + "，正在重试")
                continue
            else:
                print("无")

    def save_score(self):
        headers['Referer'] = URL + 'menu/menu.jsp'
        r = self.session.get(
            URL + 'gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2017-2018%e5%ad%a6%e5%b9%b4%e6%98%a5(%e4%b8%a4%e5%ad%a6%e6%9c%9f)',
            headers=headers, cookies=self.cookie, stream=False)
        # r = s.get(BASE_URL + r'gradeLnAllAction.do?type=ln&oper=sxinfo&lnsxdm=001', headers=headers)
        #  按课程属性
        if r.status_code == 200:
            print("开始打印html")
            data = r.content
            with open(GRADE_FILE_PATH + self.sid + '_transcript.html', 'wb') as f:
                f.write(data)
            print("已保存为 " + GRADE_FILE_PATH + self.sid + "_Transcript.html")
        else:
            print("成绩保存失败，正在重试")
            self.login()
            self.save_score()

    def get_info(self):
        time.sleep(2)
        headers['Referer'] = URL + 'menu/menu.jsp'
        r = self.session.get(URL + 'xjInfoAction.do?oper=xjxx', headers=headers, cookies=self.cookie, stream=False)
        r.encoding = 'GB2312'
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            td = soup.find_all('td', width="275")
            content = [i.get_text().split() for i in td]
            if not content:
                print("服务器信息缺省，幽灵账户")
            else:
                print("服务器信息完整")
                info = ""
                for i in content:
                    if len(i):
                        info += " '%s'," % i[0]
                    else:
                        info += " '',"
                info = info[:-1]
                info += " );"
                try:
                    with open(INFO_FILE_PATH + self.sid + "_info.txt", "w") as f:
                        f.write(info)
                        f.close()
                    print(info)
                    # group.cur.execute(sql)
                except Exception as e:
                    print(e)
                    print("个人信息重复或其他错误")
                    raise e
                # group.conn.commit()
                print("个人信息保存成功")
                while True:
                    time.sleep(1)
                    headers['Referer'] = URL + r"xjInfoAction.do?oper=xjxx"
                    r = self.session.get(
                        URL + 'xjInfoAction.do?oper=img', headers=headers, cookies=self.cookie, stream=False)
                    if r.status_code == 200:
                        with open(PIC_FILE_PATH + self.sid + '.png', 'wb') as f:
                            f.write(r.content)
                        print("图片下载成功")
                        return True
                    else:
                        print("图片下载失败")
                        return False
        else:
            print("个人信息保存失败")

    def evaluate(self):
        time.sleep(2)
        global URL
        headers['Referer'] = URL + 'jxpgXsAction.do?oper=index'
        r = self.session.get(URL + 'jxpgXsAction.do?oper=listWj', stream=True, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        r.encoding = 'GB2312'
        content = soup.find_all('img', title='评估')
        headers['Referer'] = URL + 'jxpgXsAction.do?oper=listWj'
        time.sleep(2)
        flag = True
        # print(r.text)
        for data in content:
            cnt = 0
            # print(data)
            while cnt < 3:
                msg = data['name'].split('#@')
                # print(msg)
                ensure_data = {'wjbm': msg[0], 'bpr': msg[1], 'bprm': msg[2], 'wjmc': msg[3],
                               'pgnrm': msg[4], 'pgnr': msg[5], 'oper': 'wjShow', 'pageSize': 20,
                               'page': 1, 'currentPage': 1, 'pageNo': ''}
                print(ensure_data['pgnrm'], ensure_data['bprm'])
                self.session.post(URL + 'jxpgXsAction.do', data=ensure_data, headers=headers)
                evaluate_data = {
                    'wjbm': msg[0],
                    'bpr': msg[1],
                    'pgnr': msg[5],
                    'oper': 'wjpg',
                    'xumanyzg': 'zg',
                    'wjbz': '',
                    'zgpj': choice(EVALUATE_ASS).encode('gbk'),
                    '0000000003': '8_0.95',
                    '0000000004': '12_0.95',
                    '0000000005': '12_0.95',
                    '0000000006': '8_0.95',
                    '0000000007': '12_0.95',
                    '0000000008': '12_0.95',
                    '0000000009': '8_0.95',
                    '0000000010': '8_0.95',
                    '0000000011': '10_0.95',
                    '0000000012': '10_0.95'
                }
                time.sleep(1)
                post = self.session.post(URL + 'jxpgXsAction.do?oper=wjpg', headers=headers, data=evaluate_data)
                if post.status_code == 200:
                    print("评估成功")
                    break
                else:
                    print("某位老师评估失败")
                    cnt += 1
                    flag = False
        return flag

    def get_elective_course(self):
        print("开始抢课")
        time.sleep(2)
        global URL
        search_data = {
            'actionType': '2',
            'cxkxh': '',
            'jhxn': '',
            'kch': self.cid[:-3],
            'kcsxdm': '',
            'oper2': 'gl',
            'pageNumber': '-1'
        }
        headers['Referer'] = URL + 'xkAction.do'
        r = self.session.post(URL + 'xkAction.do?actionType=2&pageNumber=-1&oper1=ori', data=search_data,
                              headers=headers, cookies=self.cookie, stream=False, timeout=60)

        course_data = {
            'kcId': self.cid,  # 所选课程格式 '课程号_课序号'
            'preActionType': '2',  # 固定，无需改变
            'actionType': '9'  # 固定，无需改变
        }  # 所选课程请求的表单
        headers['Referer'] = URL + 'xkAction.do?actionType=2&pageNumber=-1&oper1=ori'
        r = self.session.post(URL + 'xkAction.do', data=course_data, headers=headers, cookies=self.cookie, stream=False,
                              timeout=60)
        time.sleep(1)
        r = self.session.get(URL + 'xkAction.do?actionType=7', headers=headers, cookies=self.cookie, stream=False,
                             timeout=60)
        tmp = BeautifulSoup(r.text, 'lxml').get_text()
        if self.cid[:-3] in tmp:
            print("课序号" + self.cid + "成功")
            return True
        else:
            print("课序号" + self.cid + "失败, 可能课余量为零")
            return False

    def cancel_course(self, course):
        course_data = {
            'actionType': '10',
            'kcId': course
        }
        r = self.session.get(URL + 'xkAction.do?actionType=10&kcId=' + course, data=course_data,
                             headers=headers, cookies=self.cookie, stream=False, timeout=60)
        print(r.status_code)
        time.sleep(2)

    def own_course(self):
        r = self.session.get(URL + 'xkAction.do?actionType=7', headers=headers, cookies=self.cookie,
                             stream=False, timeout=60)
        r.encoding = 'GB2312'
        soup = BeautifulSoup(r.text, 'lxml')
        elems = soup.find_all("td", rowspan="1")
        total = len(elems) // 11
        allcid = []
        detail = []

        #  2 课程号 3 课程名  4 课序号
        #  一张表有11个

        def inner_get(es, i, n):
            return es[i * 11 + n].get_text().split()[0]

        for i in range(total):
            tmp = []
            tmp.append(inner_get(elems, i, 2))
            tmp.append(inner_get(elems, i, 3))
            tmp.append(inner_get(elems, i, 3))
            detail.append(tmp)
            allcid.append(tmp[0])
        print("已有课程:")
        print(detail)
        return allcid

    def cancel_all(self):
        allcourse = self.own_course()
        for i in allcourse:
            self.cancel_course(i)
