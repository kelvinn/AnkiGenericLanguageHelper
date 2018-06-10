# -*- encoding: utf-8 -*-
'''DISCLAIMER: DUE TO COPYRIGHT ISSUES, IMAGES GATHERED SHOULD
   ONLY BE USED FOR RESEARCH AND EDUCATION PURPOSES ONLY'''
from urllib.parse import quote
from bs4 import BeautifulSoup as Soup
import json
import base64
import re
import threading
import unicodedata

from urllib.request import urlopen, Request, urlretrieve

# programtically go through google image ajax json return
# and save links to list
# num_images is more of a suggestion
# it will get the ceiling of the nearest 100 if available


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


class Forvo:
    def __init__(self):
        self.pattern = re.compile("Play\(\d+,'(.*?)'")
        self.audio_url = "https://audio00.forvo.com/mp3/"

    def get_links(self, query_string, lang):
        # initialize place for links
        links = []

        if lang:
            url = 'https://forvo.com/word/' + quote(query_string) + '/#' + lang
        else:
            url = 'https://forvo.com/word/' + quote(query_string)

        # set user agent to avoid 403 error
        request = Request(url, None, {'User-Agent': 'Mozilla/5.0'})

        # returns json formatted string of the html
        html = urlopen(request).read()

        # use BeautifulSoup to parse as html
        new_soup = Soup(html, 'html.parser')

        # Find the anchor, go two parents up, then find all related links
        plays = new_soup.find("em", id=lang).parent.parent.find_all("span", "play")


        # loop through images and put src in links list
        for j in range(len(plays)):
            match = self.pattern.search(plays[j]["onclick"])
            if match:
                links.append(self.audio_url + base64.b64decode(match.group(1)).decode())

        return links

    def download(self, term, links, directory):
        threads = []
        links = links[:5]
        filenames = []
        for i in range(len(links)):

            file_name = slugify('forvo_%s_%s' % (term, i)) + ".mp3"
            filenames.append(file_name)

            thread = threading.Thread(target=urlretrieve, args=(links[i], "./" + directory + "/" + file_name))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


        return filenames

    def search(self, term, lang, output="../../addons21/GenericLanguageHelper/user_files/"):
        all_links = self.get_links(term, lang)
        filenames = self.download(term, all_links, output)
        return len(filenames)


class GoogleImages:
    def __init__(self):
        pass

    def get_links(self, query_string, lang):
        # initialize place for links
        links = []
        # step by 100 because each return gives up to 100 links

        url = 'https://www.google.com/search?ei=1m7NWePfFYaGmQG51q7IBg&q=' + quote(query_string) + '&tbm=isch&tbs=iar:s&tbs=ift:jpg&ved=' \
              '0ahUKEwjjovnD7sjWAhUGQyYKHTmrC2kQuT0I7gEoAQ&start=' \
              '&yv=2&vet=10ahUKEwjjovnD7sjWAhUGQyYKHTmrC2kQuT0I7gEoAQ.1m7NWePfFYaGmQG51q7IBg.i&ijn=1&asearch=' \
              'ichunk&async=_id:rg_s,_pms:s'

        # set user agent to avoid 403 error
        request = Request(url, None, {'User-Agent': 'Mozilla/5.0'})

        # returns json formatted string of the html
        json_string = urlopen(request).read()

        # parse as json
        page = json.loads(json_string)

        # html found here
        html = page[1][1]

        # use BeautifulSoup to parse as html
        new_soup = Soup(html, 'html.parser')

        # all img tags, only returns results of search
        imgs = new_soup.find_all('img')

        # loop through images and put src in links list
        for j in range(len(imgs)):
            links.append(imgs[j]["src"])

        return links

    def download(self, term, links, directory):
        threads = []

        links = links[:95]
        filenames = []
        for i in range(len(links)):

            file_name = slugify('glt_%s_%s' % (term, i)) + ".jpg"
            filenames.append(file_name)

            thread = threading.Thread(target=urlretrieve, args=(links[i], "./" + directory + "/" + file_name))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return filenames

    def search(self, term, lang, output="../../addons21/GenericLanguageHelper/user_files/"):
        all_links = self.get_links(query_string=str(term), lang=lang)
        filenames = self.download(str(term), all_links, output)
        return len(filenames)


if __name__ == '__main__':
    term = "美國"
    gi = GoogleImages()
    filenames = gi.search(term, lang='zh', output='user_files/')

    print(filenames)

    forvo = Forvo()
    filenames = forvo.search(term, lang='zh', output='user_files/')
    print(filenames)
