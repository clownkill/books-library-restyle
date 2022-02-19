import argparse
import os
from urllib.parse import urljoin
from urllib.parse import urlsplit

import pathvalidate
import requests
from bs4 import BeautifulSoup
from requests import HTTPError
from tqdm import tqdm



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
    title, author = title_and_author.split('::')
    return title.strip(), author.strip()


def save_book_text(response, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    valid_name = pathvalidate.sanitize_filename(filename)
    file_path = os.path.join(folder, f'{valid_name}.txt')
    with open(file_path, 'w') as file:
        file.write(response.text)


def download_image(book_id, folder='images/'):
    url = get_book_image_url(book_id)
    os.makedirs(folder, exist_ok=True)
    filename = urlsplit(url).path.split('/')[-1]
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
    comments = [comment.find('span').text for comment in comments_tag]
    return comments


def get_book_genres(book_id):
    soup = get_book_soup(book_id)
    genres_tag = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_tag]
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


def download_books(book_id):
    url = 'http://tululu.org/txt.php'
    params = {
        'id': book_id,
    }
    response = requests.get(url, params)
    response.raise_for_status()
    filename = f'{book_id}. {get_book_title_author(book_id)[0]}'
    save_book_text(response, filename)
    download_image(book_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_id', type=int, help='start book id', default=1)
    parser.add_argument('-e', '--end_id', type=int, help='end book id', default=10)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for book_id in tqdm(range(start_id, end_id)):
        url = f'http://tululu.org/b{book_id}/'
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except HTTPError:
            continue
        download_books(book_id)
        parse_book_page(book_id)


if __name__ == '__main__':
    main()
