import requests
import fake_headers
import json
from bs4 import BeautifulSoup
from pprint import pprint

headers_gen = fake_headers.Headers(browser='firefox', os='win')

response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=headers_gen.generate())
html_data = response.text

habr_main = BeautifulSoup(html_data, 'lxml')
vacancy_list_tag = habr_main.find('div', id='a11y-main-content')

vacancy_tags = vacancy_list_tag.find_all('div', class_='vacancy-serp-item__layout')

vacancy_list = []
for vacancy_tag in vacancy_tags:
    header_tag = vacancy_tag.find('h3')
    a_tag = header_tag.find('a')
    link = a_tag['href'] #Ссылка на вакансию

    vacancy_response = requests.get(link, headers=headers_gen.generate())
    vacancy = BeautifulSoup(vacancy_response.text, 'lxml')

    #Название компании
    company_name_tag = vacancy.find('div', class_='vacancy-company-details')
    company_name = company_name_tag.find('span')
    name = " ".join(company_name.text.split())

    #Город
    city = []
    city_name = vacancy.find_all('a', class_='bloko-link bloko-link_kind-tertiary bloko-link_disable-visited')
    for city_tag_ in city_name:
        city_name = city_tag_.find('span')
        name_city = city_name.text
        city.append(name_city)
        for element in city:
            city_ = "".join(element).split()[0]

    #Зарплата
    salary_tag = vacancy.find('span', class_='bloko-header-section-2')
    salary_vacancy = salary_tag['data-qa']

    if salary_vacancy == 'bloko-header-2':
        salary_vacancy = 'Заработная плата не указана'
    elif salary_vacancy == 'vacancy-salary-compensation-type-net':
        salary_vacancy = " ".join(salary_tag.text.split())


    #Поиск ключевых слов "Django" и "Flask в описании вакансии
    vacancy_body_tag = vacancy.find('div', class_='vacancy-section')
    vacancy_body_text = vacancy_body_tag.text

    if 'Flask' and 'Django' in vacancy_body_text:

        vacancy_list.append({
            'name': name,
            'link': link,
            'salary': salary_vacancy,
            'city': city_
        })

#pprint(vacancy_list)

with open('files.json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_list, f, ensure_ascii=False, indent=2)
