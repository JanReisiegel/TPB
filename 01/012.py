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
ARTICLES = []
URL = 'https://www.idnes.cz/zpravy/archiv/'
COOKIES ={
    'colbda': 1
}

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


def get_articles_group():
    URL = 'https://www.idnes.cz/zpravy'
    
    return result


def get_articles():
    url_adresses = get_articles_group()
    index = 1
    for url in url_adresses:
        try:
            driver.get(url)
        except Exception as e:
            print(url)
            continue
        time.sleep(2)
        continued = True
        while continued:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('div', class_='art') if soup.find_all('div', class_='art') else []
            if len(articles) != 0:
                for article in articles:
                    link = article.find('a').get('href') if article.find('a') else None
                    if (link is not None and link not in ARTICLES):
                        ARTICLES.append(link)
            if (len(ARTICLES) >= 300000/len(url_adresses)*index):
                continued = False
                break
            try:
                element = driver.find_element(By.XPATH, "//a[@class='ico-right' and @title='další']")
                element.click()
                time.sleep(1)
            except Exception as e:
                continued = False
                continue
        index += 1
    


def main():
    response = requests.get(URL, cookies=COOKIES)
    print(response.text)
    


if __name__ == '__main__':
    main()
