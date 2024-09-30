# pylint: skip-file
# flake8: noqa
'''
Navrhněte algoritmus, který bude postupně procházet články webového portálu iDnes.cz.
Ke každému článku uloží název článku, obsah článku, kategorii, počet fotografií, datum publikace a počet komentářů. (pozor na neúplné údaje)
Informace bude ukládat do textového souboru ve formátu JSON. Doplňte i funkcionalitu pro načtení dat, bude potřebná pro další úlohy.
'''
import re
from bs4 import BeautifulSoup
import json
import requests
import time
import logging
import logging.config
ARTICLES = []
URL = 'https://www.idnes.cz/zpravy/archiv/'
SORTING = '?datum=&idostrova=idnes'
COOKIES ={
    'kolbda': '1'
}
NUMBER_OF_ARTICLES = 40
ARTICLES_DATA = []


def load_logging_config(config_file):
    """
    Načte konfiguraci loggeru z JSON souboru
    """
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config


def setup_logger(logger_name="idnesScrapper", config_file="logging_config.json"):
    """
    Připraví logger se dvěma výstupy
    """
    logging_config = load_logging_config(config_file)
    logging.config.dictConfig(logging_config)
    return logging.getLogger(logger_name)


LOGGER = setup_logger(logger_name="idnesScrapper")


def fetch_article(article_html):
    soup = BeautifulSoup(article_html, 'html.parser')
    title = soup.find('h1').text if soup.find('h1') else None
    article_body = soup.find('div', id='art-text') if soup.find('div', id='art-text') else None
    content = ' '.join([p.text for p in article_body.find_all('p')])
    content = content.replace('\n', ' ')
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    category_html = soup.find('ul', class_='iph-breadcrumb').find_all('li')[-1] if soup.find('ul', class_='iph-breadcrumb') else None
    category_soup = BeautifulSoup(str(category_html), 'html.parser')
    category = category_soup.find('a').text if category_html else None
    fotos_html = soup.find('div', class_='more-gallery').prettify() if soup.find('div', class_='more-gallery') else None
    photos = 0
    if fotos_html:
        soup_photos = BeautifulSoup(fotos_html, 'html.parser')
        photos = int(soup_photos.find('b').text) if soup_photos.find('b') else 0
    else:
        photos = len(article_body.find_all('img')) if article_body.find_all('img') else 0
    date = soup.find('meta', {
        'itemprop': 'datePublished'
        }).get('content') if soup.find('meta', {
            'itemprop': 'datePublished'}) else soup.find('span', {'itemprop': 'datePublished'}).get('content')
    html_comments = soup.find('a', id='moot-linkin').prettify() if soup.find('a', id='moot-linkin') else None
    comments = 0
    if(html_comments is not None):
        soup_comments = BeautifulSoup(html_comments, 'html.parser')
        comments = int(re.search(r'\d+', soup_comments.find('span').text).group()) if soup_comments.find('span') else 0
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


def get_articles():
    page = 0
    while len(ARTICLES) < NUMBER_OF_ARTICLES:
        page += 1
        #print(URL + str(page) + SORTING)
        response = requests.get(URL + str(page) + SORTING, cookies=COOKIES)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='art') if soup.find_all('div', class_='art') else []
        if len(articles) == 0:
            LOGGER.error('No articles found')
            #print('No articles found')
            return
        for article in articles:
            link = article.find('a').get('href')
            if (link is not None) and ('https://www.idnes.cz' in link) and ('/foto' not in link) and (link not in ARTICLES):
                ARTICLES.append(link)
        #print(len(ARTICLES))
        
    #print(page)
    LOGGER.info(f'{page} Pages done')
    LOGGER.info(f'Articles totaly found: {len(ARTICLES)}')



def main():
    LOGGER.info('Starting iDnes.cz scrapper')
    not_articles = 0
    paywaaled = 0
    start = time.time()
    get_articles()
    
    
    for article in ARTICLES:
        response = requests.get(article, cookies=COOKIES)
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        paywall = True if soup.find('div', class_='paywall') else False
        if paywall:
            LOGGER.warning('Paywall detected')
            LOGGER.info(article)
            #print('Paywall detected')
            paywaaled += 1
            continue
        is_article = True if soup.find('div', id='art-text') else False
        if(not is_article):
            LOGGER.warning('Not an article')
            LOGGER.info(article)
            #print('Not an article')
            not_articles += 1
            continue
        article_data = fetch_article(html_text)
        ARTICLES_DATA.append(article_data)
    
    end = time.time()
    #print(f'Execution time: {end - start}')
    save_to_file(ARTICLES_DATA, 'articles.json')
    #print(len(ARTICLES_DATA))
    LOGGER.info(f'Execution time: {end - start}')
    LOGGER.info(f'Articles scrapped: {len(ARTICLES_DATA)}')
    LOGGER.info(f'Not articles: {not_articles}')
    LOGGER.info(f'Paywalled: {paywaaled}')
    

if __name__ == '__main__':
    main()
