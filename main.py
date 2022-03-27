import streamlit as st
import smtplib
import ssl

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from PIL import Image
from io import BytesIO

# st.set_page_config(initial_sidebar_state="collapsed")
st.sidebar.image("logo.png", width=300)
SMTP_HOST = ["smtp.yandex.com", 465]
FILE_TYPES = ["png", "bmp", "jpg", "jpeg"]


def header():
    author = """
        made by [Kosarevsky Dmitry](https://github.com/dKosarevsky) 
        for [Networks](https://github.com/dKosarevsky/iu7/blob/master/8sem/networks.md) labs
        in [BMSTU](https://bmstu.ru)
    """
    st.header("МГТУ им. Баумана. Кафедра ИУ7")
    st.markdown("**Курс:** Компьютеные сети")
    st.markdown("**Преподаватель:** Рогозин Н.О.")
    st.markdown("**Студент:** Косаревский Д.П.")
    st.sidebar.markdown(author)


def uploader(file):
    show_file = st.empty()
    if not file:
        show_file.info("valid file extension: " + ", ".join(FILE_TYPES))
        return False
    return file


def image_to_byte_array(image: Image):
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def attach_files_to_mail(mime, file):
    filename = file.name
    img = Image.open(file)
    img = image_to_byte_array(img)

    part = MIMEApplication(img, Name=filename)
    part["Content-Disposition"] = f"attachment; filename={filename}"
    mime.attach(part)


def fill_mail(from_address, to_address, msg_subject, msg_text, file=None):
    mime = MIMEMultipart()
    mime["From"] = from_address
    mime["To"] = to_address
    mime["Date"] = formatdate(localtime=True)
    mime["Subject"] = msg_subject
    mime.attach(MIMEText(msg_text, "plain"))
    if file:
        attach_files_to_mail(mime, file)
    return mime


def send_mail(mime, smtp_host, password, context):
    with smtplib.SMTP_SSL(smtp_host[0], smtp_host[1], context=context) as server:
        server.login(mime["From"], password)
        server.sendmail(mime["From"], mime["To"], mime.as_string())


def main():
    header()
    st.markdown("### Лабораторная работа №5")
    st.markdown("**Тема:** Реализация SMTP-клиента")
    st.markdown("---")

    with st.form("send_mail"):
        c1, c2 = st.columns(2)
        from_ = c1.text_input("Введите email отправителя:", value="example@ya.ru")
        to = c2.text_input("Введите email получателя:", value="if@kosarevsky.ru")
        c3, c4 = st.columns(2)
        pwd = c3.text_input("Введите пароль:", type="password")
        subj = c4.text_input("Введите тему сообщения:", value="Привет")
        message = st.text_area(
            label="Введите сообщение:",
            value="Самые ужасные строения — это те, бюджет которых был слишком велик для поставленных целей."
        )
        file = uploader(st.file_uploader("Загрузите файл:", type=FILE_TYPES))

        submitted = st.form_submit_button("Отправить сообщение")
        if submitted:
            context = ssl.create_default_context()
            mime = fill_mail(from_, to, subj, message, file=file if file else None)
            send_mail(mime, SMTP_HOST, pwd, context)


if __name__ == "__main__":
    main()
