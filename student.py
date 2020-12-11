import MySQLdb
from PIL import Image
import pytesseract
import re
import requests
import time
import lxml
import shutil
from bs4 import BeautifulSoup
import os
from random import choice


ERROR_WRONG_CAPTCHA = "你输入的验证码错误，请您重新输入！"
ERROR_BUSY = "数据库忙请稍候再试"
ERROR_WRONG_PASSWORD = "你输入的证件号不存在，请您重新输入！"
UNEVALUATED = "未评"
UNDONE = "已评未抢"
DONE = "已抢"
WRONG_PWD = "密码错误"
SUCCESS = "选课成功！"


PIC_FILE_PATH = r"pictures/"
CAPS_FILE_PATH = r"captcha/"
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


def get_captcha(f):
    image = Image.open(f, "r")
    image = image.convert('L')
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if 140 <= pixels[x, y] <= 256:
                pixels[x, y] = 255
    testdata_dir_config = '--tessdata-dir "C:\\Softwares\\Tesseract-OCR\\tessdata"'
    captcha = pytesseract.image_to_string(image, lang='eng',
                                           config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
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

    def __init__(self, sid, pwd, cid='', status=''):
        self.sid = sid
        self.pwd = pwd
        self.cid = cid
        self.status = status
        self.session = requests.Session()

    def display(self):
        print(self.sid, self.pwd, self.cid, self.status)

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
                with open(CAPS_FILE_PATH + self.sid + 'capt.png', 'rb') as f:
                    captcha = get_captcha(f)
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
            with open(self.sid + '_transcript.html', 'wb') as f:
                f.write(data)
            print("已保存为 " + self.sid + "_Transcript.html")
        else:
            print("成绩保存失败，正在重试")
            self.login()
            self.save_score()

    def get_info(self, group):
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
                sql = "INSERT INTO info(学号) values(%s) " % self.sid
            else:
                print("服务器信息完整")
                sql = '''INSERT INTO info values( '''
                for i in content:
                    if len(i):
                        sql += " '%s'," % i[0]
                    else:
                        sql += " '',"
                sql = sql[:-1]
                sql += " );"
                try:
                    group.cur.execute(sql)
                except Exception as e:
                    print(e)
                    print("个人信息重复或其他错误")
                    raise e
                group.conn.commit()
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
                    'zgpj': '老师上课认真，学习了很多'.encode('gbk'),
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
            'cxkxh':'',
            'jhxn':'',
            'kch': self.cid[:-3],
            'kcsxdm':'',
            'oper2': 'gl',
            'pageNumber': '-1'
        }
        headers['Referer'] = URL + 'xkAction.do'
        r = self.session.post(URL + 'xkAction.do?actionType=2&pageNumber=-1&oper1=ori', data=search_data, headers=headers, cookies=self.cookie, stream=False, timeout=20)

        course_data = {
            'kcId': self.cid,   # 所选课程格式 '课程号_课序号'
            'preActionType': '2',    # 固定，无需改变
            'actionType': '9'        # 固定，无需改变
        }   # 所选课程请求的表单
        headers['Referer'] = URL + 'xkAction.do?actionType=2&pageNumber=-1&oper1=ori'
        r = self.session.post(URL + 'xkAction.do', data=course_data, headers=headers, cookies=self.cookie, stream=False, timeout=20)
        time.sleep(1)
        r = self.session.get(URL + 'xkAction.do?actionType=7', headers=headers, cookies=self.cookie, stream=False, timeout=20)
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
                             headers=headers, cookies=self.cookie, stream=False, timeout=20)
        print(r.status_code)
        time.sleep(2)

    def own_course(self):
        r = self.session.get(URL + 'xkAction.do?actionType=7', headers=headers, cookies=self.cookie,
                             stream=False, timeout=20)
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


class StudentGroup:
    group_name = ""
    items = []
    conn = None
    cur = None

    def __init__(self):
        self.conn = MySQLdb.connect(
            host='127.0.0.1',
            port=3306,
            user='xrandx',
            passwd='5492184',
            db='xzitdb',
            charset='utf8'
        )
        self.cur = self.conn.cursor()
        if not os.path.exists(PIC_FILE_PATH):
            os.makedirs(PIC_FILE_PATH)
        if not os.path.exists(CAPS_FILE_PATH):
            os.makedirs(CAPS_FILE_PATH)
        else:
            shutil.rmtree(CAPS_FILE_PATH)
            os.mkdir(CAPS_FILE_PATH)

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def __getitem__(self, i):
        return self.items[i]

    def get_total(self):
        return len(self.items)

    def import_database(self):
        with open("user_list.txt", "r", encoding="utf-8") as f:
            while True:
                tmp = f.readline().strip()
                if not tmp:
                    break
                tmparr = tmp.split()
                if len(tmparr) == 3:
                    sql = '''INSERT INTO get_course(main, sid, pwd, cid, status)
                    SELECT '{}','{}','{}', '{}', '{}' FROM dual 
                    WHERE not exists(select * from get_course where `main` = '{}');'''.format(tmparr[0] + "_" + tmparr[2], tmparr[0], tmparr[1], tmparr[2], UNDONE, tmparr[0] + "_" + tmparr[2])
                else:
                    sql = "insert ignore into get_course values( '{}','{}','{}', '{}', '{}') ;".format(
                        tmparr[0] + "_" + tmparr[2], tmparr[0], tmparr[1], tmparr[2], UNEVALUATED)
                self.cur.execute(sql)
        self.conn.commit()

    #  读取未完成的代码
    def pull_database(self):
        self.items.clear()
        sql = "select * from get_course where status != '{}'".format(DONE)
        self.cur.execute(sql)
        rs = self.cur.fetchall()
        self.conn.commit()
        if rs is None:
            print("暂无数据需要处理")
        else:
            for i in rs:
                s = Student(i[1], i[2], i[3], i[4])
                s.display()
                self.items.append(s)

    def set_status(self, single):
        sql = "update get_course set status = '{} ' where sid =  '{}' and cid = '{}';".format(
            single.status, single.sid, single.cid)
        self.cur.execute(sql)
        self.conn.commit()

    def all_scores(self):
        # i.cancel_all()
        while self.items:
            for i in self.items:
                try:
                    i.login()
                    i.save_score()
                    self.items.remove(i)
                except Exception as e:
                    auto_ip()
                    print(e)

    def all_info(self):
        # path = r"C:\Users\kevty\PycharmProjects\xzitCrawler\新建文件夹\infomation"
        # arr = os.listdir(path)
        # seta = set()
        # for j in arr:
        #     seta.add(j[:11])
        # path = r"C:\Users\kevty\PycharmProjects\xzitCrawler\新建文件夹\2015info"
        # arr = os.listdir(path)
        # for i in arr:
        #     seta.add(j[:11])
        # arr = list(seta)
        # print(arr)
        # for i in arr:
        #     sql = '''INSERT INTO get_course(main, sid, pwd, cid, status)
        #                         SELECT '{}','{}','{}', '{}', '{}' FROM dual
        #                         WHERE not exists(select * from get_course where `main` = '{}');'''.format(
        #         i + "_" + i[:4], i, i, i, UNDONE, i + "_" + i[:4])
        #     self.cur.execute(sql)
        # self.conn.commit()
        print("需要处理", len(self.items), "个任务")
        while self.items:
            for i in self.items:
                try:
                    if not i.login():
                        i.status = DONE
                        self.items.remove(i)
                        continue
                    if i.get_info(self):
                        i.status = DONE
                        self.set_status(i)
                        self.items.remove(i)
                except Exception as e:
                    auto_ip()
                    print(e)

    def all_get_courses(self):
        print("需要处理", len(self.items), "个任务")
        while self.items:
            for i in self.items:
                try:
                    i.login()
                    if i.status == UNEVALUATED:
                        if i.evaluate():
                            i.status = UNDONE
                    if i.get_elective_course():
                        i.status = DONE
                        self.items.remove(i)
                    self.set_status(i)
                except Exception as e:
                    auto_ip()
                    print(e)
        print("任务结束")


