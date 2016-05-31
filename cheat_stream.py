import requests
from bs4 import BeautifulSoup
import re

def get(url):
    if "usatf.tv" in url:
        return get_usatf(url)
    elif "flotrack.org" in url:
        return get_flotrack(url)
    else:
        return "#"
    
    

def get_flotrack(url):
    r = requests.get(url)
    #soup = BeautifulSoup(r.content, 'lxml')
    #img=soup.find(property="og:image")['content']
    m = re.search('http://32598.cdx.c.ooyala.com\/[^/]*\/', r.content)
    return m.group(0)+'DOcJ-FxaFrRg4gtDEwOjFjZjowazsSV4'

def get_usatf(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    img=soup.find(rel="image_src")['href']
    m = re.search('http:\/\/cf.c.ooyala.com\/[^/]*\/', img)
    return m.group(0)+'DOcJ-FxaFrRg4gtDEwOjFyazpvMTE79T'
