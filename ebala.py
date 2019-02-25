import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys

ROOT_LINK='ebela.in'
LANG='bengali/'
HTTP = 'http://www.'
HTTPS = 'https://www.'
TAGS=['sports/', 'entertainment/', 'international/', 'state/', 'national/', 'search-results-page/']

def get_visited_links():
    #import ipdb; ipdb.set_trace()
    if os.path.isfile(os.path.join('data', 'ebala.txt')):
        data = [line.strip() for line in open(os.path.join('data', 'ebala.txt'), 'r')]
        #data=[link for link in data if remove_extra(link)]
        return list(set(data))
    else:
        return []

def url_check(a):
    if any(tag in a for tag in TAGS):
        return True

def check_search(links):
    # import ipdb; ipdb.set_trace()
    extra_links=[]
    for link in links:
        if 'searchresult' in link:
            page_search = re.search('(page=)(\d+)', link, re.IGNORECASE)

            if page_search:
                int2=str(int(page_search.group(2))+1)
                new_link=re.sub('(page=)(\d+)', r"\g<1>"+f"{int2}", link)
                extra_links.append(new_link)
    
    links.extend(extra_links)
    return links

def remove_extra(link):
    if not link.startswith('https://www.anandabazar.com//'):
        if not link.startswith('http://www.anandabazar.com//'):
            return True

def extract_links(LINKS, VISITED_LINKS, soup):
    links_ = [a.get('href')
              for a in soup.find_all('a', href=True)
              if url_check(a.get('href'))]
    links_=[HTTP+ROOT_LINK+link for link in links_ if url_check(link)]
    links_=check_search(links_)
    LINKS.extend([i for i in links_ if i not in VISITED_LINKS])
    LINKS = list(set(LINKS))
    return LINKS

def get_all_links():
    #import ipdb; ipdb.set_trace()
    LINKS=[]#get_visited_links()
    if not LINKS:
        LINKS=['https://ebela.in/search-results-page/search-7.519094?q=sports&fromSearch=yes&page=1&short=desc&slab=0&tnp=59']
    VISITED_LINKS=get_visited_links()

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
                with open(os.path.join('data', 'ebala.txt'), 'w') as f:
                    for link in list(set(VISITED_LINKS)):
                        f.write(f"{link}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            try:
                LINKS.remove(current_link)
                VISITED_LINKS.remove(current_link)
            except Exception as e:
                pass

if __name__ == "__main__":
    get_all_links()
