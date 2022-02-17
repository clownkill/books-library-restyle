import os

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
    print(title)
    print(author)



def download_books(counts):
    file_path = 'books/'
    url = 'http://tululu.org/txt.php'
    os.makedirs(file_path, exist_ok=True)
    for id in range(1, counts+1):
        params = {
            'id': id,
        }
        response = requests.get(url, params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        get_book_title_author(id)
        # get_book_title_author(response)
        # file_name = f'{file_path}/{id}.txt'
        # with open(file_name, 'wb') as file:
        #     file.write(response.content)



if __name__ == '__main__':
    download_books(10)

