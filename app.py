import telebot
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import pylatex
from pylatex import Document, Section, Subsection, Command, Package, NewPage,  HorizontalSpace, Head, PageStyle, LineBreak, Foot, SmallText,  MediumText
from pylatex.utils import italic, bold, NoEscape
from ast import Sub

import re
import datetime
import shutil
import os
import random
import time
import pandas as pd
import numpy as np

import sys
import traceback
from werkzeug.utils import secure_filename

URL = 'https://stihi.ru'


def del_file(file: str):
    """
        delete file if exist or print exception
    """
    try:
        os.remove(file)
    except Exception as e:
        print(f"cant delete file {file}:\n", traceback.format_exc())        


def send_file(file: str, chat_id: int):
    # отправлут файл с именем file в чат c chat_id в телеграм
    try:
        with open(file=file, mode='rb') as f:
            bot.send_document(
                chat_id=chat_id,
                document=f
            )
    except Exception as e:
        print(f"cant send file {file}\n", traceback.format_exc())


def get_books(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}):
    """
    возвращает список элементов класса BeautifulSoup.Tag, которые содерджат ссылки на книги
    """
    html_current = requests.get(url=url, headers=headers).text
    parsed_current = BeautifulSoup(html_current, 'html.parser')
    current_books = parsed_current.find_all(name='a', attrs={'class': 'poemlink'})
    return current_books


def get_poem(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}):
    """
    Взвращает элемент класса BeautifulSoup.Tag содержащий текст стихотворения
    """
    html = requests.get(url=url, headers=headers).text
    parsed = BeautifulSoup(html, 'html.parser')
    poem = parsed.find(name='div', attrs={'class': 'text'})

    return poem.text if poem else ''


def create_latex_doc(dataframe, author_name='', author_title='', font_size: int=10):
    date = datetime.date.today()
    year = date.strftime("%Y")

    def add_poem(poem_title, poem_text):
        with doc.create(Subsection(poem_title, numbering=False, label=False)):
            doc.append(Command(command='addcontentsline', arguments=['toc', 'subsection', poem_title]))
            doc.append(poem_text)

    doc = Document(
        document_options=f'{font_size}pt, a5paper',
        documentclass='book',
        fontenc='T1, T2A',
        lmodern=True
    )
    doc.preamble.append(Package(name='babel', options='russian'))
    doc.preamble.append(Package(name='cmap'))

    doc.preamble.append(Package(name='extsizes'))
    # doc.preamble.append(Package(name='indentfirst'))

    doc.preamble.append(Package(name='geometry'))
    doc.preamble.append(Command(command='geometry', arguments='top=25mm'))
    doc.preamble.append(Command(command='geometry', arguments='bottom=35mm'))
    doc.preamble.append(Command(command='geometry', arguments='left=20mm'))
    doc.preamble.append(Command(command='geometry', arguments='right=25mm'))

    doc.preamble.append(Package(name='setspace'))

    doc.preamble.append(Package(name='lastpage'))
    # doc.preamble.append(Package(name='soul'))
    # doc.preamble.append(Package(name='hyperref'))


    doc.preamble.append(Command('title', author_name))
    # doc.preamble.append(Command('author', author_name))
    doc.preamble.append(Command('date', year))

    doc.preamble.append(Command(command='setcounter', arguments=['tocdepth', '4']))
    # doc.preamble.append(Command(command='renewcommand', arguments=[r'\chaptername', ' ']))


    # doc.preamble.append(Package(name='tocvsec2'))
    # doc.append(Command(command='settocdepth', arguments='2'))


    # https://jeltef.github.io/PyLaTeX/current/examples/header.html
    # https://mydebianblog.blogspot.com/2011/05/latex.html
    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("L")):
        header.append("")
    # Create center header
    with header.create(Head("C")):
        header.append("")
    # Create right header
    with header.create(Head("R")):
        header.append("")
    # Create left footer
    with header.create(Foot("L")):
        header.append("")
    # Create center footer
    with header.create(Foot("C")):
        header.append(Command(command='thepage'))   # внизу по центру заишем омер страницы
    # Create right footer
    with header.create(Foot("R")):
        header.append("")

    doc.preamble.append(header)
    doc.change_document_style("plain")

    doc.append(Command('maketitle'))
    doc.append(NewPage())
    doc.append(Command('tableofcontents'))
    doc.append(Command(command='clearpage'))
    # doc.append(NewPage())


    print(f"цикл по произведениям...")
    N = len(dataframe)
    for i in range(N):
        poem_title = dataframe['title'][N-i-1]
        poem = dataframe['poem'][N-i-1]

        # skip empty
        if not isinstance(poem, str):
            print(i, poem)
            continue
        # skip empty
        if not len(poem):
            continue
        poem_text = poem.strip()
        poem_text = re.sub("-", "- ", poem_text)    # добавляю пробелы после - чтобы не было ошибок
        add_poem(poem_title, poem_text)
    
    return doc





URL = "https://stihi.ru"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}
API_KEY = os.environ.get('TEL_API_TOKEN') or None




bot = telebot.TeleBot(token=API_KEY)

print("bot started")




@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.send_message(
        chat_id = message.chat.id,
        text=f"Бот качает стихи авторов с сайта stihi.ru\nПришлите боту ссылку на автора вида <code>https://stihi.ru/avtor/автор</code>" + \
        f"\nИли пришлите боту Excel или CSV файл со столбцами 'title' и 'poem', чтобы бот сгенерировал книжку в pdf.",
        parse_mode='html'
    )

# обрабатывем сообщение от пользователя (с ссылкой)
@bot.message_handler(content_types=["text"])
def default_mesage(message):
    text = message.text
    parse_result = urlparse(text)
    # print(parse_result)

    # если не упоминвется сайт stihi.ru - то выходим
    if parse_result.netloc != 'stihi.ru':
        bot.send_message(
            chat_id = message.chat.id,
            text=f"Бот качает стихи авторов с сайта stihi.ru\nПришлите боту ссылку на автора  вида <code>https://stihi.ru/avtor/автор</code>",
            parse_mode='html'
        )
        return
    
    response = requests.get(url=text, headers=headers)  

    # если страницы автора нет - выходим
    if not response.status_code == 200:
        bot.send_message(
            chat_id = message.chat.id,
            text = f"""<a href="{text}">{text}</a> - страница не найдена""",
            parse_mode="HTML"
        )
        return

    msg = bot.send_message(
        chat_id = message.chat.id,
        text = f"Ищу автора"
    )

    author_url = text

    html=response.text
    parsed = BeautifulSoup(html, 'html.parser')
    author_header = parsed.find(name='h1')  # получам имя автора из заголовка на странице (fj\\по ссылке его никнейм)
    
    # если заголовок с именем автора не найден, то ошибка и выходим
    if author_header is None:
        bot.send_message(
            chat_id = message.chat.id,
            text = f"""<a href="{text}">{text}</a> - автор не найден""",
            parse_mode="HTML"
        )
        return
    
    author_header = author_header.text

    bot.edit_message_text(
        chat_id = msg.chat.id,
        message_id = msg.message_id,
        text = f"Найден автор <b>{author_header}</b> <a href='{author_url}'>{author_url}</a>\nПолучаю список произведений...",
        parse_mode="HTML"
    )

    # качаем список произведений
    books = []
    current_books = get_books(url=author_url)       # книги со страницы автора
    books.extend(current_books)

    # если на титульной странице автора были книги, то изменяем номер страицы и пробуем скачать книги с нее
    counter = 0     # число книг
    while len(current_books) > 0:
        dt = random.random()
        time.sleep(dt/3)
        counter += len(current_books)
        url_current = f"{author_url}&s={counter}"
        current_books = get_books(url_current)
        books.extend(current_books)
        # print(f"{url_current}, links={len(current_books)}")
    # print(f"{len(books) = }")


    bot.edit_message_text(
        chat_id=msg.chat.id,
        message_id = msg.message_id,
        text = f"Найден автор <b>{author_header}</b> <a href='{author_url}'>{author_url}</a>\nУ автора {len(books)} произведений",
        parse_mode='HTML'
    )

    # смотрим сколько книг нашлось на страниц автора, и если их не нашлось, то выводим сообщение и выходим
    if len(books) == 0:
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id = msg.message_id,
            text = f"У автора <b>{author_header}</b> <a href='{author_url}'>{author_url}</a> не найдено произведений",
            parse_mode='HTML'
        )
        return
    

    data = np.array(books)      # посещаем все ссылки на книги в нп массив

    df = pd.DataFrame(data=[(f"{URL}{i.get('href')}", i.text) for i in books], columns=['url', 'title'])    # формируем таблицу с названиям ипроиведений и ссылкой на них

    poems = []

    msg_get = bot.send_message(
        chat_id=msg.chat.id,
        text = f"{0}/{len(df)} произведений получено"
    )

    for i in range(len(df)):
        dt = random.random()
        time.sleep(dt)
        poem_url = df.loc[i, 'url']
        text = get_poem(poem_url)
        poems.append(text)
        none_result = f"{'' if text else ' None'}"

        bot.edit_message_text(
            chat_id = msg_get.chat.id,
            message_id = msg_get.message_id,
            text = f"{i+1}/{len(df)} ({(i+1)/(len(df))*100:3.2f}%) произведений получено"
        )
        # print(f"{i+1}/{len(df)} ({(i+1)/(len(df))*100:3.2f}%) complete{none_result}")

    df['poem'] = poems
    poems_filename = f"{author_header}.csv"
    poems_filename_excel = f"{author_header}.xls"

    df.to_csv(poems_filename, index=False)
    df.to_excel(poems_filename_excel, index=False)

    os.makedirs(name=f"./{author_header}", exist_ok=True)

    for i in range(len(df)):
        title = df.loc[i, 'title']
        text_data = df.loc[i, 'poem']
        with open(file=f"./{author_header}/{i}_{title}.txt", mode='wt', encoding='utf8') as f:
            f.write(text_data)


    filename = '_'.join(author_header.split())
    format = 'zip'
    directory = f"./{author_header}"

    # создаю архив из директории и удаляю директорию 
    try:
        shutil.make_archive(filename, format, directory)
        shutil.rmtree(directory)
    except Exception as e:
        print(f"Exception: cant create arcive {filename} or delete directory {directory}\n {str(e)}")

    send_file(file=poems_filename, chat_id=msg.chat.id)             # отправляю csv файл
    send_file(file=poems_filename_excel, chat_id=msg.chat.id)       # отправляю exls файл

    author_name = author_header
    author_title = "Стихи"

    # генареция через латекс pdf
    bot.edit_message_text(
        chat_id = msg_get.chat.id,
        message_id = msg_get.message_id,
        text = f"Генерирую pdf"
    )
    print(f"start generate pdf for {author_name} {author_title}")
    print(f"генерация pdf")
    pdf_filename = '_'.join(author_name.split())

    # не знаю почему, но правильно оглавление получается с 4й попытке
    for i in range(5):
        time.sleep(1)
        doc = create_latex_doc(dataframe=df, author_name=author_name, font_size=10)
    
        try:
            doc.generate_pdf(pdf_filename, clean=True)
        except Exception as e:
            print(f"Exception during pdf generation: \n", traceback.format_exc())

    time.sleep(1)
    send_file(file=f"{pdf_filename}.pdf", chat_id=msg.chat.id)      # отправка pdf
    send_file(file=f"{filename}.zip", chat_id=msg.chat.id)      # отправляю архив в телеграм

    del_file(file=poems_filename)               # удаляю csv файл
    del_file(file=poems_filename_excel)         # удаляю excel файл
    del_file(file=f"{filename}.zip")            # удаляю архив с диска
    del_file(file=f"{pdf_filename}.zip")        # удаляю pdf
    



@bot.message_handler(content_types=['document'])
def get_document(message):
    allowed_types = [
        'text/csv',
        'application/vnd.ms-excel'
    ]
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_type = message.document.mime_type
    basename = os.path.basename(file_name)
    purename = os.path.splitext(basename)[0]
    print(f"{file_id = }, {file_name = }, {file_type = }, {basename = }, {purename = }")
    print()
    # print(message)

    allowed = file_type in allowed_types    # файл правильного типа
    if not allowed:
        bot.reply_to(
            message=message,
            text = f"файл <b>{file_name}</b> не является <code>CSV или EXCEL файлом</code>.\n Пришлите пожалуйста файл, который отправлял вам бот.",
            parse_mode="HTML"
        )
        return
    

    # сохраняем файл
    file_info = bot.get_file(file_id=file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    secure_file_name = secure_filename(file_info.file_path)
    print(f"{file_info.file_path = }, {secure_file_name = }\n")
    with open(file=secure_file_name, mode='wb') as f:
        f.write(downloaded_file)

    try:
        if file_type == 'application/vnd.ms-excel':
            df = pd.read_excel(secure_file_name)
        elif file_type == 'text/csv':
            df = pd.read_csv(secure_file_name)

    except:
        bot.reply_to(
            message=message,
            text=f"не удалось преобразовать <code>{secure_file_name}</code>-файл в DataFrame объект.\nПопробуйте другой файл.",
            parse_mode='HTML'
        )
        print(traceback.format_exc())
        return

    print(df.head(3))
    print(df.columns)


    del_file(file=secure_file_name)     # удаляю файл
    

    author_name = ' '.join([i.capitalize() for i in purename.split(' ')])
    pdf_filename = "_".join(author_name.casefold().split())     
    print(f"\n{author_name = }, {pdf_filename = }\n")

    for i in range(5):  # я не знаю почему, но правиьное оглавление формируется тоько на 4ю попытку
        time.sleep(1)
        doc = create_latex_doc(dataframe=df, author_name=author_name, font_size=10)
    
        try:
            doc.generate_pdf(pdf_filename, clean=True)
        except Exception as e:
            print(f"Exception during pdf generation: \n", traceback.format_exc())
            bot.reply_to(
                message=message,
                text=f"Не удалось сконвертировать файл <code>{file_name}<code> в <code>pdf</code>",
                parse_mode='HTML"'
            )
            return
    
    time.sleep(1)
    pdf_fullname = f"{pdf_filename}.pdf"        # pdf имя файла для отправки
    send_file(file=pdf_fullname, chat_id=message.chat.id)
    time.sleep(0.2)
    del_file(file=pdf_fullname)     # удаляю отправленный pdf


def main():
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=20)
        except Exception as e:
            print(traceback.format_exc(), str(e))
            time.sleep(5)

if __name__ == "__main__":
    main()
