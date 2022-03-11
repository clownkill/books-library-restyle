import json
from pprint import pprint

with open('json/books.json', 'r', encoding='utf-8') as file:
    books_json = file.read()

books = json.loads(books_json)

for books_info in books.values():
    pprint(books_info['image_url'])
