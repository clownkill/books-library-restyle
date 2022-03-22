import json
import os

from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def on_reload():
    template = env.get_template('template.html')

    with open('json/books.json', 'r', encoding='utf-8') as file:
        books_json = file.read()
    books = json.loads(books_json).values()

    folder_path = 'pages/'
    os.makedirs(folder_path, exist_ok=True)

    books_splite_by_20 = list(chunked(books, 10))
    for page_num, splitted_books in enumerate(books_splite_by_20, 1):
        book_pairs = list(chunked(splitted_books, 2))

        file_name = f'index{page_num}.html'
        file_path = os.path.join(folder_path, file_name)

        rendered_page = template.render(book_pairs=book_pairs)

        with open(file_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
