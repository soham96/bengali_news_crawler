import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys
from bs4 import BeautifulSoup as bs
import requests

ROOT_LINK='anandabazar.com'
LANG='bengali/'
HTTP = 'http://www.'
HTTPS = 'https://www.'
TAGS=['entertainment/', 'international/', 'state/', 'national/', 'searchresult']

def get_visited_links():
    #import ipdb; ipdb.set_trace()
    if os.path.isfile(os.path.join('data', 'anandabazar.txt')):
        data = [line.strip() for line in open(os.path.join('data', 'anandabazar.txt'), 'r')]
        data=[link for link in data if remove_extra(link)]
        return list(set(data))
    else:
        return []

def url_check(a):
    if any(tag in a for tag in TAGS):
        if not 'photogallery/' in a:
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
    links_=[HTTP+ROOT_LINK+link for link in links_ if remove_extra(link)]
    links_=check_search(links_)
    LINKS.extend([i for i in links_ if i not in VISITED_LINKS])
    LINKS = list(set(LINKS))
    return LINKS

def get_all_links():
    #import ipdb; ipdb.set_trace()
    data = [line.strip() for line in open(os.path.join('data', 'words.txt'), 'r')]
    for d in tqdm(data):
        LINKS=[]#get_visited_links()
        if not LINKS:
            LINKS=['https://www.anandabazar.com/searchresult/site-search-7.1881001?q=army&page=1&short=desc&slab=0&tnp=230'.replace('army', d)]
        VISITED_LINKS=get_visited_links()

        total_links=0
        pbar = tqdm(total=10000)
        while len(VISITED_LINKS)<100000:
            current_link=LINKS.pop(0).strip()
            try:
                page=requests.get(current_link)
                soup=bs(page.content, 'html.parser')
                LINKS = extract_links(LINKS, VISITED_LINKS, soup)
                VISITED_LINKS.append(current_link)
                if len(VISITED_LINKS)%10==0:
                    pbar.update(10)
                    with open(os.path.join('data', 'new_anandabazar.txt'), 'w') as f:
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

def check_link(link):
    if 'searchresult' in link:
        return False
    
    return True


def get_saved_links():
    #import ipdb; ipdb.set_trace()
    if os.path.isfile(os.path.join('data', 'new_anandabazar.txt')):
        data = [line.strip() for line in open(os.path.join('data', 'new_anandabazar.txt'), 'r')]
        print(len(list(set(data))))
        return list(set(data))
    else:
        return []

def get_headline(link):
    # import ipdb; ipdb.set_trace()
    page=requests.get(link)
    soup=bs(page.content, 'html.parser')
    try:
        headline=soup.find_all('h1')[0].text
    except:
        print(link)
        return 'NA'
    return headline

def remove_extra_links(links):
    
    read_links=[]

    with open('data/anandabazar_classification.txt', 'r') as f:
        for line in f:
            read_links.append(line.split('||')[2].replace('\n', ''))
    
    new_link=[link for link in links if link not in read_links]
    new_link=[link.replace('www.anandabazar.com//', '') for link in new_link]
    return new_link

def process_page():
    links=get_saved_links()
    links=list(set(links))
    # import ipdb; ipdb.set_trace()
    links=remove_extra_links(links)
    print(len(links))
    lines=[]
    for link in tqdm(links):
        if check_link(link):
            cls=link.split('http://www.anandabazar.com/')[1].split('/')[0]
            if cls=='calcutta':
                cls='kolkata'
            
            headline=get_headline(link)
            
            text=f"\n{cls}||{headline}||{link}"
            lines.append(text)
            
            if len(lines)==20:
                with open(os.path.join('data', 'anandabazar_classification.txt'), 'a') as f:
                    for line in lines:
                        f.write(line)
                lines=[]

if __name__ == "__main__":
    get_all_links()

    # process_page()
