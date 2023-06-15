import requests
import bs4
import re
from fake_headers import Headers
from pprint import pprint
import json
from tqdm import tqdm


headers = Headers(browser="chrome", os="win")

header_data = headers.generate()
vacancy_rate = []
count = 0

for page in tqdm(range(0, 3), desc='Поиск по страницам... '):
    response = requests.get(
        f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page}', headers=header_data)
    html_data = response.text
    soup = bs4.BeautifulSoup(html_data, 'lxml')
    tag = soup.find_all('div', class_='serp-item')
    # Получаем ссылку на вакансию
    for mask in tag:
        lay = mask.find('a')
        link = lay['href']

        # зарплата
        sal = mask.find('span', class_="bloko-header-section-3")
        if sal is not None:
            gat = sal.text
            pattern = re.compile(r'\u202f')
            pattern1 = re.compile(r' руб.')
            repl = ' '
            salary = re.sub(pattern, repl, gat)

        # Название вакансии
        name = mask.find(class_="bloko-header-section-3").text

        # Название компании
        company_name = mask.find(
            'div', class_='vacancy-serp-item__meta-info-company').text
        company = re.sub(r'\s+', ' ', company_name).strip()

        # Город вакансии
        city_1 = mask.find('div', class_="vacancy-serp-item-company").text
        variant = re.findall(r'(?:Москва|Санкт-Петербург)', city_1)
        city = variant[0]

        # Создаем словарь для хранения полученных данных
        vacancy = {
            'link': link,
            'salary': salary,
            'company': company,
            'city': city,
            'name': name
        }

        response1 = requests.get(link, headers=header_data)
        html_data1 = response1.text
        soup1 = bs4.BeautifulSoup(html_data1, 'lxml')
        tag1 = soup1.find('div', class_='g-user-content')
        if tag1 is not None:
            text = tag1.text
            match = re.search(r'\b(Django|Flask)\b', text)
            if match:
                match_word = match.group(0)
                vacancy_rate.append(vacancy)
                count += 1
            else:
                continue


        with open('vacancies1.json', 'w', encoding='utf-8') as file:
            json.dump(vacancy_rate, file, indent=4, ensure_ascii=False)

print(f'Кол-во найденых вакансий: {count}')