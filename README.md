## XZITAAO

> 本项目是 http://jwc.xzit.edu.cn 的爬虫
>
> 非常感谢[xrandx](https://github.com/xrandx)将其开源
>
> 我现在把它整理出来供大家使用

### 使用方法

`pip install xzitaao`

**一些说明**

`student.set_tesseract_dic("D:\\Program Files\\Tesseract-OCR\\tessdata")`设置`tesseract`目录（可选）
如果没有设置，将会显示验证码，你需要自己手动输入

**Demo**

```python
import xzitaao

Sid = ""  # 学号
Pwd = ""  # 密码
Cid = ""  # 选课的课程号
Tesseract_Dic = "D:\\Program Files\\Tesseract-OCR\\tessdata"

def main():
    student = xzitaao.Student(Sid, Pwd, Cid)
    try:
        student.set_tesseract_dic(Tesseract_Dic)
        student.login()  # 登录
        student.get_info()  # 保存个人信息
        student.save_score()  # 保存成绩单
        student.evaluate()  # 教学评估
        student.get_elective_course() #选课
    except Exception as e:
        xzitaao.auto_ip()
        print(e)


if __name__ == '__main__':
    main()
```

### 已知 Bug

如果你没有设置`tesseract`目录，验证码图片无法自己关掉，需要手动关

### LICENSE

[Apache License 2.0](LICENSE)