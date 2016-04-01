from bs4 import BeautifulSoup
import requests
import re

class Searcher:

    def __init__(self, term):
        self.res = self.search(term)

    def search(self, term):
        page = requests.get("https://www.youtube.com/results?search_query=%s&page=&utm_source=opensearch"%term)
        pattern= re.compile('<ol id="section-list-\d+" class="section-list">((.|\n)*)<\/ol>')
        m=pattern.search(page.text)
        soup = BeautifulSoup(m.group(0), 'lxml')
        elements = soup.find_all("h3", class_="yt-lockup-title")
        res = []
        for h3 in elements:
            for child in h3.children:
                if child.name == 'a':
                    res.append([self.make_link(child['href']), self.make_unicode(child.string)])
                elif child.name == 'span':
                    res[-1][1] += child.string
        return res

    def get_res(self):
        return self.res
    
    def make_link(self, href):
        return "https://www.youtube.com"+href

    def make_unicode(self, stuff):
        return unicode(stuff)
                
if __name__ == "__main__":
    s = Searcher("david bowie")
    print s.get_res()
