import argparse
import json
import os
from urllib.parse import urljoin

import bs4
import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from parse_tululu_book_page import download_book, download_image


def create_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page', default=1, type=int)
    parser.add_argument('-e', '--end_page', type=int)
    parser.add_argument('-df', '--dest_folder', default='./', type=str)
    parser.add_argument('-jp', '--json_path', default='json/', type=str)
    parser.add_argument('-si', '--skip_image', action='store_true', default=False)
    parser.add_argument('-st', '--skip_text', action='store_true', default=False)

    return parser


def save_books_json(book_informations, dest_folder='./', folder='json/'):
    folder_path = os.path.join(dest_folder, folder)
    os.makedirs(folder_path, exist_ok=True)
    file_name = 'books.json'
    file_path = os.path.join(folder_path, f'{file_name}')
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(book_informations, json_file, ensure_ascii=False)


def get_book_from_pages(
        start_page, end_page,
        dest_folder='./', json_path='./json',
        skip_image=False, skip_text=False):
    book_informations = {}

    for page in range(start_page, end_page):
        url = f'http://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        base_url = 'http://tululu.org'
        book_links = soup.select('.d_book')

        for book_a_tag in book_links:
            book_link = book_a_tag.select_one('a')['href']
            book_url = urljoin(base_url, book_link)
            book_id = book_link.strip('/').lstrip('b')
            try:
                if not skip_text:
                    parsed_book_informations = download_book(book_id, book_url, dest_folder)
                    book_informations[book_id] = parsed_book_informations
                    if not skip_image:
                        download_image(parsed_book_informations['image_url'], dest_folder)
            except HTTPError:
                continue

    save_books_json(book_informations, dest_folder, json_path)


def get_last_page():
    url = 'http://tululu.org/l55/'
    response = requests.get(url)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    last_page = soup.select('.npage')[-1].text

    return int(last_page)


def main():
    parser = create_argparser()
    namespace = parser.parse_args()
    start_page = namespace.start_page
    dest_folder = namespace.dest_folder
    json_path = namespace.json_path
    skip_image = namespace.skip_image
    skip_text = namespace.skip_text

    if not namespace.end_page:
        end_page = get_last_page()
    else:
        end_page = namespace.end_page

    get_book_from_pages(start_page, end_page, dest_folder, json_path, skip_image, skip_text)


if __name__ == '__main__':
    main()
