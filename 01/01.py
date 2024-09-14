'''
Navrhněte algoritmus, který bude postupně procházet články webového portálu iDnes.cz.
Ke každému článku uloží název článku, obsah článku, kategorii, počet fotografií, datum publikace a počet komentářů. (pozor na neúplné údaje)
Informace bude ukládat do textového souboru ve formátu JSON. Doplňte i funkcionalitu pro načtení dat, bude potřebná pro další úlohy.
'''

import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

ARTICLES = []


def fetch_article(article_html):
    soup = BeautifulSoup(article_html, 'html.parser')

    title = soup.find('h1').text if soup.find('h1') else None
    content = ' '.join([p.text for p in soup
                        .find_all('p')]) if soup.find_all('p') else None
    category = soup.find(
        'span', class_='c-breadcrumbs__title').text if soup.find(
            'span', class_='c-breadcrumbs__title') else None
    photos = len(soup.find_all('img')) if soup.find_all('img') else 0
    date = soup.find('time').text if soup.find('time') else None
    comments = soup.find(
        'span', class_='c-article-meta__count').text if soup.find(
            'span', class_='c-article-meta__count') else None

    return {
        'title': title,
        'content': content,
        'category': category,
        'photos': photos,
        'date': date,
        'comments': comments
    }


def save_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.close()


def load_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        file.close()
    return data


def main():
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_driver_path = './chromedriver.exe'

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    URL = 'https://www.idnes.cz/zpravy'
    driver.get(URL)

    try:
        link = driver.find_element(By.XPATH,
                                   '//a[contains(text(), "Souhlasím")]')
        link.click()
    except Exception as e:
        print(f'No contentwall: {e}')

    time.sleep(15)

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    new = soup.find_all('div', class_='art')
    for i in new:
        if i.find('a')['href'] not in ARTICLES:
            ARTICLES.append(i.find('a')['href'])

    data = []

    for article in ARTICLES:
        driver.get(article)
        time.sleep(5)
        html = driver.page_source
        payed = False
        try:
            element = driver.find_element(By.XPATH, "//div[contains(@class, 'paywall-top-out')]")
            payed = True
        except Exception as e:
            print(f'No paywall')
        if payed:
            print('Payed article')
            continue
        else:
            data.append(fetch_article(html))
    save_to_file(data, 'articles.json')

    driver.quit()


if __name__ == '__main__':
    main()