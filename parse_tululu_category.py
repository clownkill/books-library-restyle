import argparse
import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from main import download_book, download_image, parse_book_page


def create_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page', default=1, type=int)
    parser.add_argument('-e', '--end_page', type=int)
    return parser


def download_book_from_all_pages(start_page, end_page):
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
                download_book(book_id, book_url)
                print(book_url)
                parsed_book_informations = parse_book_page(book_url)
                book_informations[book_id] = parsed_book_informations
                download_image(parsed_book_informations['image_url'])
            except HTTPError:
                continue

    with open('books.json', 'w', encoding='utf-8') as json_file:
        json.dump(book_informations, json_file, ensure_ascii=False)


def main():
    parser = create_argparser()
    namespace = parser.parse_args()
    start_page = namespace.start_page
    if not namespace.end_page:
        end_page = start_page + 1
    else:
        end_page = namespace.end_page
    download_book_from_all_pages(start_page, end_page)



if __name__ == '__main__':
    main()
