import streamlit as st
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

# st.set_page_config(initial_sidebar_state="collapsed")
st.sidebar.image('logo.png', width=300)
SMTP_HOST = ["smtp.yandex.ru", 465]


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


def fill_mime(from_address, to_address, msg_subject, msg_text, filenames=None):
    """
        Заполнение полей письма
    """
    mime = MIMEMultipart()
    mime['From'] = from_address
    mime['To'] = to_address
    mime['Date'] = formatdate(localtime=True)
    mime['Subject'] = msg_subject
    mime.attach(MIMEText(msg_text, 'plain'))
    # attach_files_to_mime(mime, filenames)
    return mime


def send_mime_mail(mime, smtp_host, from_address, password):
    """
        Отправка письма с вложениями
    """
    server = smtplib.SMTP(smtp_host[0], smtp_host[1])
    server.starttls()
    server.login(from_address, password)
    server.sendmail(mime['From'], mime['To'], mime.as_string())
    server.quit()


def main():
    header()
    st.markdown("### Лабораторная работа №5")
    st.markdown("**Тема:** Реализация SMTP-клиента")
    st.markdown("---")

    with st.form("send_mail"):
        c1, c2 = st.columns(2)
        from_ = c1.text_input("Введите email отправителя:", value="example@ya.ru")
        to = c2.text_input("Введите email получателя:", value="example@ya.ru")
        c3, c4 = st.columns(2)
        pwd = c3.text_input("Введите пароль:", type="password")
        subj = c4.text_input("Введите тему сообщения:", value="Привет")
        message = st.text_area(
            label="Введите сообщение:",
            value="Самые ужасные строения — это те, бюджет которых был слишком велик для поставленных целей."
        )

        if st.form_submit_button("Отправить сообщение"):
            # key_filenames = find_files_with_keyword(KEY)
            mime = fill_mime(from_, to, subj, message, filenames=None)
            send_mime_mail(mime, SMTP_HOST, from_, pwd)


if __name__ == "__main__":
    main()
