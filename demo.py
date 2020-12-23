import xzitaao

Sid = ""  # 学号
Pwd = ""  # 密码
Cid = ""  # 选课的课程号


def main():
    student = xzitaao.Student(Sid, Pwd, Cid)
    try:
        student.set_tesseract_dic("D:\\Program Files\\Tesseract-OCR\\tessdata")
        student.login()  # 登录
        student.get_info()  # 保存个人信息
        student.save_score()  # 保存成绩单
        student.evaluate()  # 教学评估
        # student.get_elective_course() #选课
    except Exception as e:
        xzitaao.auto_ip()
        print(e)


if __name__ == '__main__':
    main()
