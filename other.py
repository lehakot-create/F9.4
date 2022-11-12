import requests


def main():
    url = 'http://0.0.0.0:8080/news/'

    data = {
        'news': 'heelo news!'
    }
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
