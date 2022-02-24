import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from main import download_book, parse_book_page


def download_book_from_all_pages():
    book_informations = {}

    for page in range(1, 2):
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
                book_informations[book_id] = parse_book_page(book_url)
            except HTTPError:
                continue

    with open('books.json', 'w', encoding='utf-8') as json_file:
        json.dump(book_informations, json_file, ensure_ascii=False)


def main():
    download_book_from_all_pages()



if __name__ == '__main__':
    main()
