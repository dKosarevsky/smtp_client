import streamlit as st
import smtplib
import ssl
import re

from time import sleep
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from PIL import Image
from io import BytesIO

# st.set_page_config(initial_sidebar_state="collapsed")
st.sidebar.image("logo.png", width=300)
SMTP_HOST = ["smtp.yandex.com", 465]
FROM = "bmstu.networks@ya.ru"
PWD = st.secrets["PWD"]
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


def show_task():
    st.markdown("""
    Написать smtp-клиент, который

        1) В качестве входных данных (аргументы командной строки) получает:
        
           адрес получателя, адрес отправителя, пароль.
        
        2) Использует один из открытых smtp-серверов для доставки MIME-сообщений, включая приложения, если они есть, в
           соответствии с вариантом.
        
        Вариант = номер студента по списку в Электронном Университете % кол-во вариантов.
        
        3) Дополнительная задача зависит от варианта.
        
           I. Доставка сообщений выполняется с регулярным интервалом. Интервал и тело сообщения, имя файла для прикрепления (
           опционально) вводятся с клавиатуры.
           
           II. В качестве дополнительного параметра задается ключевое слово. По данному ключевому слову выполняется поиск в
       текстовых файлах в папке клиента, При обнаружении слова файл прикрепляется к письму.
    """)


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
    st.markdown("**Тема:** Реализация SMTP-клиента. Вариант I")
    st.markdown("SMTP-клиент реализован на базе сервера почтовых сообщений Yandex")
    if st.checkbox("Показать задание"):
        show_task()
    st.markdown("---")

    from_email = None
    pwd = None
    if st.checkbox("Использовать свой ящик на Яндекс для отправки сообщений"):
        c4, c5 = st.columns(2)
        from_email = c4.text_input("Введите email отправителя:", value="example@yandex.ru")
        pwd = c5.text_input("Введите пароль:", type="password")

    from_ = from_email if from_email else FROM
    password_ = pwd if pwd else PWD

    with st.form("send_mail"):
        c1, c2, c3 = st.columns(3)
        email = c1.text_input("Введите email получателя:", value="if@kosarevsky.ru")
        subj = c2.text_input("Введите тему сообщения:", value="Привет")
        interval = c3.number_input("Введите интервал (сек):", min_value=1, max_value=100, value=3)

        message = st.text_area(
            label="Введите сообщение:",
            value="Если проект не укладывается в сроки, то добавление рабочей силы задержит его еще больше."
        )
        file = uploader(st.file_uploader("Загрузите файл:", type=FILE_TYPES))

        submitted = st.form_submit_button("Отправить сообщение")
        if submitted:
            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
                while True:
                    try:
                        context = ssl.create_default_context()
                        mime = fill_mail(from_, email, subj, message, file=file if file else None)
                        send_mail(mime, SMTP_HOST, password_, context)
                        st.code("Сообщение отправлено.")
                    except Exception as e:
                        st.error(e)
                    sleep(interval)
            else:
                st.error("Необходимо указать корректный email получателя.")


if __name__ == "__main__":
    main()
