from bs4 import BeautifulSoup
import requests

BASE_URL = 'https://www.mangaupdates.com/series'

def scrape():
    page = requests.get(BASE_URL)
    print(page.text)

if __name__ == '__main__':
    scrape()