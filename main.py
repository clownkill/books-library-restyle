import requests


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


if __name__ == '__main__':
    url = 'http://tululu.org/txt.php?id=32168'
    file_name = 'Пески Марса'
    get_book(url, file_name)

