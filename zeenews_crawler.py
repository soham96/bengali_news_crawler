import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys
from mucri import fetch_pages


FORMAT_STRING = "%(levelname)-8s:%(name)-8s.%(funcName)-8s>> %(message)s"

import logging
logging.basicConfig(format=FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ROOT_LINK='zeenews.india.com/'
LANG='bengali/'
HTTP = 'http://www.'
HTTPS = 'https://www.'
TAGS=['sports/', 'entertainment/', 'world/', 'state/', 'nation/', 'kolkata'] #removed 'kolkata/'

def get_visited_links():
    #import ipdb; ipdb.set_trace()
    if os.path.isfile(os.path.join('data', 'zeenews_links.txt')):
        data = [line.strip() for line in open(os.path.join('data', 'zeenews_links.txt'), 'r')]
        
        return list(set(data))
    else:
        return []

def is_url(urls):
    checked_urls=[]
    for url in urls:
        if url.startswith(HTTP+ROOT_LINK+LANG) or url.startswith(HTTPS+ROOT_LINK+LANG):
            if any(tag in url for tag in TAGS) and '.html' in url:
                checked_urls.append(url)
    
    return checked_urls

def url_check(a):
    if (a.startswith('/'+LANG) or a.startswith('/'+LANG)):
        if any(tag in a for tag in TAGS):
            return True

def extract_links(LINKS, VISITED_LINKS, soup):
    links_ = [a.get('href').lstrip('/')
              for a in soup.find_all('a', href=True)
              if url_check(a.get('href'))]
    links_=[HTTP+ROOT_LINK+link for link in links_]
    LINKS.extend([i for i in links_ if i not in VISITED_LINKS])
    LINKS = list(set(LINKS))
    return LINKS

def get_all_links():
    # import ipdb; ipdb.set_trace()
    LINKS=get_visited_links()
    LINKS=[]
    if not LINKS:
        LINKS=['http://zeenews.india.com/bengali/state/', 'http://zeenews.india.com/bengali/nation/', 
        'http://zeenews.india.com/bengali/world/', 'http://zeenews.india.com/bengali/entertainment/']
    VISITED_LINKS= get_visited_links()

    total_links=0
    pbar = tqdm(total=10000)
    while len(VISITED_LINKS)<10000:
        current_link=LINKS.pop(0).strip()
        try:
            page=requests.get(current_link)
            soup=bs(page.content, 'html.parser')
            LINKS = extract_links(LINKS, VISITED_LINKS, soup)
            VISITED_LINKS.append(current_link)
            if len(VISITED_LINKS)%10==0:
                pbar.update(10)
                with open(os.path.join('data', 'links.txt'), 'w') as f:
                    for link in list(set(VISITED_LINKS)):
                        f.write(f"{link}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(current_link)

def process_page():
    links=get_visited_links()
    import ipdb; ipdb.set_trace()
    links2=[links[10*i : 10*(i+1)] for i in range(810)]
    #import ipdb; ipdb.set_trace()
    # links=fetch_pages(links[:100])

    for link_list in tqdm(links2):
        try:
            link_list=is_url(link_list)
            pages=fetch_pages(link_list)
        except:
            print(link_list)
        
        if not pages:
            continue
        for page in pages:
            # page = requests.get(link)
            # import ipdb; ipdb.set_trace()

            # page=bs(link.decode('utf-8'), 'html5lib')
            soup = bs(page, 'html.parser')
            
            link=soup.find('meta', property='og:url')['content']        
            for script in soup(["script", "style"]): 
                script.extract()
            
            title_text=soup.find('h1', class_='article-heading').text

            if not title_text:
                log.info(f"No Title for {link}")
            
            yo=re.search('(/bengali/)([a-z]+)', link)
            news_class=yo.group(2)

            with open(os.path.join('data', 'classification.txt'), 'a') as f:
                f.write(f"\n{news_class}||{title_text}||{link}")

if __name__ == "__main__":
    get_all_links()
    # process_page()