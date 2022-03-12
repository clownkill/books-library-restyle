import json

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
    book_pairs = list(chunked(books, 2))

    rendered_page = template.render(book_pairs=book_pairs)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)

    server.serve(root='.')


if __name__ == '__main__':
    main()
