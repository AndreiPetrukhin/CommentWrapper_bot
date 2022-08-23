#!pip install pandas
#!pip install docx2txt
#!pip3 install pyTelegramBotAPI
#!pip install requests

import telebot
import re
import pandas as pd
import docx2txt
import requests
import os

bot = telebot.TeleBot('5426660346:AAG5iyeWj1ZSBdsqpM5r1qXp6b_J_omBjUQ')

@bot.message_handler(content_types=['text', 'audio', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact', 'new_chat_members'])
def warning(message):
    bot.send_message(message.chat.id, 'This bot is intended for converting docx files to csv. Please, upload docx file. ')

@bot.message_handler(content_types=['document'])
def start_processing(message):
    #download docx from telegram bot
    my_text = download_doc(message)

    #convert docx to list
    list = docx_to_lst(my_text)

    #filtration
    regexp = r'(\"Нравится\": \d+|Нравится|Нравится: \d+|\d+ нед.|\d+ дн.|Подтвержденный|Ответить|Показать перевод|Скрыть ответы|\d+ ответов|\d+ ответа|\d+ ответ|В сети|Начало формы|Конец формы|Скрыть|\d+ ответов|\d+ д.|Автор|Отредактировано|Скрыть \d+ ответов|Скрыть \d+ ответ|Скрыть \d+ ответа|\d+|ОтветитьПоказать перевод\d+ д.|ОтветитьПоказать перевод\d+ ч.|Ответить\d+ д.|Ответить\d+ ч.|Комментарий, на который отвечает(.*?)был удален.)'
    list = filter_1(list)
    list = filter_2(list, regexp)
    list = filter_3(list, regexp)

    # define list of names and comments
    data = list_name_comment(list)

    #list names and comments to csv file
    list_to_csv(data, message)

    #send file back
    send_file_back(message)

    #delete all files
    delete_file(message)

def download_doc(message):
    #path = "/Users/apetrukh/Downloads/" + message.document.file_name#for pc
    path = "/home/" + message.document.file_name#for docker
    file_id = message.document.file_id
    file_url = bot.get_file_url(file_id)
    file = requests.get(file_url)
    with open(path, 'wb') as doc:
        doc.write(file.content)
    return docx2txt.process(path)

def docx_to_lst(text):
    list = []
    list += re.split(r'\n|\t', text)
    return list

#удаление пустых элементов списка и элементов, которые могут находиться между комментарием и никнеймом
def filter_1(list):
    for i in range(len(list) - 1, -1, -1):
        if list[i].strip() == '':
            del list[i]
        elif list[i].strip() in ('Подписаться', 'Топовый поклонник', 'Ещё'):
            del list[i]
    return list

#проверка элементов списка на наличие комментария без ника или наоборот
def filter_2(list, regexp):
    for i in range(len(list) - 2, -1, -1):
        if (re.fullmatch(regexp, list[i - 1].strip()) is not None) and (
                re.fullmatch(regexp, list[i + 1].strip()) is not None):
            del list[i]
    return list

def filter_3(list, regexp):
    i = len(list) - 1
    while i != -1:
        if (re.fullmatch(regexp, list[i].strip()) is not None):
            del list[i]
        elif (re.fullmatch(regexp, list[i].strip()) is None) and (re.fullmatch(regexp, list[i - 2].strip()) is None) and (
                re.fullmatch(regexp, list[i - 1].strip()) is None):
            list[i - 1] += list[i].strip()
            del list[i]
        i -= 1
    return list

def list_name_comment(list):
    data = []
    for i in range(0, len(list), 2):
        data += [[list[i]] + [list[i + 1]] + [list[i + 1].count(' ') + 1]]
    return data

def list_to_csv(data, message):
    df = pd.DataFrame(data, columns=['nickmane', 'comment', 'words'])
    #path = '/Users/apetrukh/PythonHW/TBot_docx_to_csv/' + message.document.file_name + '.csv' #for pc
    path = '/home/' + message.document.file_name + '.csv' # for docker
    df.to_csv(path)

def send_file_back(message):
    #path = '/Users/apetrukh/PythonHW/TBot_docx_to_csv/' + message.document.file_name + '.csv' #for pc
    path = '/home/' + message.document.file_name + '.csv'  # for docker
    file = open(path, 'rb')
    bot.send_document(message.chat.id, file, 'Your csv file is ready')

def delete_file(message):
    #docx_name = "/Users/apetrukh/Downloads/" + message.document.file_name #for pc
    #csv_name = '/Users/apetrukh/PythonHW/TBot_docx_to_csv/' + message.document.file_name + '.csv' #for pc
    docx_name = '/home/' + message.document.file_name  # for docker
    csv_name = '/home/' + message.document.file_name + '.csv'  # for docker
    os.remove(docx_name)
    os.remove(csv_name)


bot.polling()