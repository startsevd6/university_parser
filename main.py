import requests
import csv
import time

time_start = time.time()


# from bs4 import BeautifulSoup as bs
# import pandas as pd

def info_from_table(text, l, r, curr_competition):
    delo, snils, priority, kon = 0, '', 0, []
    exam_rus, exam_mat, exam_vyb, ind = 0, 0, 0, 0
    for i in range(l, r + 1):
        if text[i:i + 4] == '</a>' and text[i + 10:i + 17] == '</span>':
            delo = text[i + 4:i + 10]
            if int(delo) == 0:
                return None
        if text[i:i + 20] == 'СНИЛС / Номер дела: ':
            snils = text[i + 27:i + 41].strip()
            if snils == delo:
                snils = 'нет'
        if text[i:i + 8] == 'priority':
            priority = int(text[i + 103])
            if priority == 0:
                return None
        if text[i:i + 2] == 'РЯ':
            if text[i + 11:i + 46].strip().isdigit():
                exam_rus = int(text[i + 11:i + 46])
            else:
                exam_rus = 0
        if text[i:i + 3] == 'Мат':
            if text[i + 13:i + 46].strip().isdigit():
                exam_mat = int(text[i + 13:i + 46])
            else:
                exam_mat = 0
        if text[i:i + 10] == 'Инф./ Физ.':
            if text[i + 19:i + 46].strip().isdigit():
                exam_vyb = int(text[i + 19:i + 46])
            else:
                exam_vyb = 0
        if text[i:i + 121] == ('<span class="rating__table--hidden">Балл за индивидуальные достижения в соответствии с '
                               'разделом IV правил приема: </span>'):
            if text[i + 122:i + 145].strip():
                ind = int(text[i + 122:i + 145])
            else:
                ind = 0
        if text[i:i + 15] == 'Другие конкурсы':
            kon = text[i + 24:text.find('<', i + 24)].lstrip().rstrip().split('; ')
    summa = exam_rus + exam_mat + exam_vyb + ind
    return delo, snils, priority, summa, curr_competition, *kon


def page_processing(program, url_template):
    r = requests.get(url_template)
    text = r.text
    l = 0
    while l >= 0:
        l = text.find('<div class="rating__card "', l + 1)
        r = text.find('remark', l)
        result = info_from_table(text, l, r, program)
        if result is not None:
            data.append(result)
        else:
            break
    return data


data = []
data_chunk = []
url_templates = {
    'АВТФ.1': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.1&fk_tr_basis=1",
    'АВТФ.2': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.2&fk_tr_basis=1",
    'АВТФ.3': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.3&fk_tr_basis=1",
    'АВТФ.4': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.4&fk_tr_basis=1",
    'АВТФ.5': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.5&fk_tr_basis=1",
    'АВТФ.9': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.9&fk_tr_basis=1",
    'ФПМИ.1': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%A4%D0%9F%D0%9C%D0%98.1&fk_tr_basis=1",
    'ФПМИ.2': "https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%A4%D0%9F%D0%9C%D0%98.2&fk_tr_basis=1"
}

for i in url_templates.keys():

    name = i
    url = url_templates[i]
    print(name, url)
    data_chunk = page_processing(name, url)
    for j in range(len(data_chunk)):
        if data_chunk[j][0] == 0:
            del data_chunk[j]
data.extend(data_chunk)
contests_university = ['АВТФ.1', 'АВТФ.2', 'АВТФ.3', 'АВТФ.4', 'АВТФ.5', 'АВТФ.9', 'ФПМИ.1', 'ФПМИ.2']
data = list(set(data))
data.sort()
for i in range(len(data)):
    contests_enrollee = ['-' for k in range(8)]
    for j in range(len(contests_university)):
        if contests_university[j] in data[i]:
            if contests_university[j] == data[i][4]:
                contests_enrollee[j] = data[i][2]
            elif i > 0:
                if data[i - 1][j + 4] not in [0, 9] and data[i][0] == data[i - 1][0]:
                    contests_enrollee[j] = data[i - 1][j + 4]
            else:
                contests_enrollee[j] = '-'
    print(data[i])
    data[i] = list(data[i][:4]) + contests_enrollee
    print(data[i])

i = 1
while i < len(data):
    if data[i - 1][0] == data[i][0]:
        del data[i - 1]
    else:
        i += 1

with open('nstu.csv', 'w', newline='') as csvfile:
    nstuwriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    nstuwriter.writerow(
        ['номер_дела', 'СНИЛС', 'программ', 'баллы', 'АВТФ.1', 'АВТФ.2', 'АВТФ.3', 'АВТФ.4', 'АВТФ.5', 'АВТФ.9',
         'ФПМИ.1', 'ФПМИ.2'])

    for i in range(len(data)):
        nstuwriter.writerow(data[i])

    # nstuwriter.writerow(['приоритет/программа', 'АВТФ.1', 'АВТФ.2', 'АВТФ.3', 'АВТФ.4', 'АВТФ.5', 'АВТФ.9',
    #                      'ФПМИ.1', 'ФПМИ.2'])

print('time:', time.time() - time_start)
print(data)
