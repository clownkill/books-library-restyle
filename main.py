import os

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


def get_book_title_author(book_id):
    url = f'http://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find('table', class_='tabs').find('h1').text
    title = title_and_author.split('::')[0].strip()
    author = title_and_author.split('::')[1].strip()
    return title


def download_txt(response, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    valid_name = pathvalidate.sanitize_filename(filename)
    file_path = os.path.join(folder, f'{valid_name}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_books(max_id):
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
        filename = f'{id}. {get_book_title_author(id)}'
        download_txt(response, filename)


if __name__ == '__main__':
    download_books(10)
