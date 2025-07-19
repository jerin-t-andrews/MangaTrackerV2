from bs4 import BeautifulSoup
import requests
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

BASE_URL = ["https://www.mangaupdates.com/series?perpage=100&page=", "1"]
#https://www.mangaupdates.com/series?perpage=25 -> perpage=100 (consider this)
#https://www.mangaupdates.com/series?page=400

def get_page_list(url):
    print(f"Scraping {url}")
    page = requests.get("".join(url))
    soup = BeautifulSoup(page.text, 'html.parser')
    series_parent_div = soup.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})

    # <a href="https://www.mangaupdates.com/series/dkd0yz5" title="Click for Series Info">
    # print(len(series_parent_div))
    
    curr_page_series = []
    for p in series_parent_div:
        link = p.find_all("a", href=re.compile('www.mangaupdates.com/series/'))
        curr_page_series.append(link)
        
    return curr_page_series

def scrape_iterative(page_count, link_list): # 182.40774083137512 sec
    for i in range(1, page_count + 1):
        curr_url = BASE_URL[0] + str(i)
        links = get_page_list(curr_url)
        link_list.extend(links)

def scrape_batch(start, end, link_list_lock, link_list): # 53.673600912094116 sec
    for i in range(start, end+1):
        curr_url = BASE_URL[0] + str(i)
        links = get_page_list(curr_url)
        with link_list_lock:
            link_list.extend(links)
            
def scrape_pool(page_num): # 33.65859413146973 sec
    url = BASE_URL[0] + str(page_num)
    print(f"Scraping {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    series_parent_div = soup.find_all("div", {"class": "col-12 col-lg-6 p-3 text"})

    # <a href="https://www.mangaupdates.com/series/dkd0yz5" title="Click for Series Info">
    # print(len(series_parent_div))
    
    curr_page_series = []
    for p in series_parent_div:
        link = p.find_all("a", href=re.compile('www.mangaupdates.com/series/'))
        curr_page_series.append(link)
        
    return curr_page_series

def scrape():
    page = requests.get("".join(BASE_URL))
    soup = BeautifulSoup(page.text, 'html.parser')
    
    try:
        page_count = soup.find("span", {"class": "d-inline-block"}).get_text()
        page_count = int("".join([ch for ch in page_count if ch.isdigit()]))
    except Exception as e:
        print(f"Error: Total page count could not be identified: {e}")
    
    link_list = []
    #batch_size = page_count // 5
    # link_list_lock = threading.Lock()
    # threads = []

    # Multithread batch processing
    # for batch in range(5):
    #     start = batch * batch_size + 1
    #     end = (batch + 1) * batch_size if batch < 4 else page_count
    #     t = threading.Thread(target=scrape_batch, args=(start, end, link_list_lock, link_list))
    #     threads.append(t)
    #     t.start()
        
    # for t in threads:
    #     t.join()

    # Iterative processing
    # scrape_iterative(page_count, link_list)
    
    # Multithread pool processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_pool, i) for i in range(1, page_count + 1)]
        for future in as_completed(futures):
            link_list.extend(future.result())
    
    print(f"Total links collected: {len(link_list)}")
    
if __name__ == '__main__':
    start = time.time()
    scrape()
    end = time.time()
    print(f"Run Time: {end - start}")