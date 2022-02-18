import os
from pprint import pprint
from urllib.parse import urljoin
from urllib.parse import urlsplit

import pathvalidate
import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def get_dvmn_logo():
    url = 'https://dvmn.org/filer/canonical/1542890876/16/'
    file_name = 'dvmn.svg'
    response = requests.get(url)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_book(url, file_name):
    response = requests.get(url)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_soup(book_id):
    url = f'http://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_book_title_author(book_id):
    soup = get_book_soup(book_id)
    title_and_author = soup.find('table', class_='tabs').find('h1').text
    title = title_and_author.split('::')[0].strip()
    author = title_and_author.split('::')[1].strip()
    return title, author


def download_txt(response, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    valid_name = pathvalidate.sanitize_filename(filename)
    file_path = os.path.join(folder, f'{valid_name}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image(book_id, folder='images/'):
    url = get_book_image_url(book_id)
    os.makedirs(folder, exist_ok=True)
    filename = str(urlsplit(url).path.split('/')[-1])
    file_path = os.path.join(folder, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_book_image_url(book_id):
    soup = get_book_soup(book_id)
    url = soup.find('div', class_='bookimage').find('img')['src']
    base_url = 'http://tululu.org'
    image_url = urljoin(base_url, url)
    return image_url


def get_book_comments(book_id):
    soup = get_book_soup(book_id)
    comments_tag = soup.find_all('div', class_='texts')
    comments = []
    if comments_tag:
        for comment in comments_tag:
            comments.append(comment.find('span').text)
    return comments


def get_book_genres(book_id):
    soup = get_book_soup(book_id)
    genres_tag = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in genres_tag:
        genres.append(genre.text)
    return genres


def parse_book_page(book_id):
    title, author = get_book_title_author(book_id)
    image_url = get_book_image_url(book_id)
    genres = get_book_genres(book_id)
    comments = get_book_comments(book_id)
    book_informations = {
        'title': title,
        'author': author,
        'image_url': image_url,
        'genres': genres,
        'comments': comments,
    }
    return book_informations


def parse_books(max_id):
    url = 'http://tululu.org/txt.php'
    for id in range(1, max_id+1):
        params = {
            'id': id,
        }
        response = requests.get(url, params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        # filename = f'{id}. {get_book_title_author(id)}'
        # download_txt(response, filename)
        # download_image(id)
        # get_book_comments(id)
        # get_book_genres(id)
        pprint(parse_book_page(id))


if __name__ == '__main__':
    parse_books(10)
