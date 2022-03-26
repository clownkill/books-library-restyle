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
    if len(response.history) != 1:
        raise HTTPError


def get_book_title_author(soup):
    title_and_author = soup.find('table', class_='tabs').find('h1').text
    title, author = title_and_author.split('::')
    return title.strip(), author.strip()


def get_book_image_url(soup):
    url = soup.find('div', class_='bookimage').find('img')['src']
    base_url = 'http://tululu.org'
    image_url = urljoin(base_url, url)
    return image_url


def get_book_comments(soup):
    comments_tag = soup.find_all('div', class_='texts')
    comments = [comment.find('span').text for comment in comments_tag]
    return comments


def get_book_genres(soup):
    genres_tag = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_tag]
    return genres


def save_book_text(response, filename, dest_folder, folder='books/'):
    folder_path = os.path.join(dest_folder, folder)
    os.makedirs(folder_path, exist_ok=True)
    valid_name = pathvalidate.sanitize_filename(filename)
    file_path = os.path.join(folder_path, f'{valid_name}.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)


def download_image(book_image_url, dest_folder, folder='images/'):
    url = book_image_url
    folder_path = os.path.join(dest_folder, folder)
    os.makedirs(folder_path, exist_ok=True)
    filename = urlsplit(url).path.split('/')[-1]
    file_path = os.path.join(folder_path, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, book_id):
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = get_book_title_author(soup)
    image_url = get_book_image_url(soup)
    image_name = urlsplit(image_url).path.split('/')[-1]
    genres = get_book_genres(soup)
    comments = get_book_comments(soup)
    book_informations = {
        'book_file_name': f'{book_id}.{title}.txt',
        'title': title,
        'author': author,
        'image_url': image_url,
        'image_name': image_name,
        'genres': genres,
        'comments': comments,
    }
    return book_informations


def download_book(book_id, parsed_book_informations, dest_folder='./'):
    url = 'http://tululu.org/txt.php'
    params = {
        'id': book_id,
    }
    response = requests.get(url, params)
    response.raise_for_status()
    book_title = parsed_book_informations['title']
    book_image_url = parsed_book_informations['image_url']
    filename = f'{book_id}.{book_title}'
    save_book_text(response, filename, dest_folder)
    download_image(book_image_url, dest_folder)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_id', type=int, help='start book id', default=1)
    parser.add_argument('-e', '--end_id', type=int, help='end book id', default=10)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    for book_id in tqdm(range(start_id, end_id)):
        url = f'http://tululu.org/b{book_id}/'
        try:
            response = requests.get(url)
            check_for_redirect(response)
            parsed_book_informations = parse_book_page(response, book_id)
            download_book(book_id, parsed_book_informations)
        except HTTPError:
            continue


if __name__ == '__main__':
    main()
