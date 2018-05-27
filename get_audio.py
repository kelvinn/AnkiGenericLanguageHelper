# -*- encoding: utf-8 -*-
'''DISCLAIMER: DUE TO COPYRIGHT ISSUES, IMAGES GATHERED SHOULD
   ONLY BE USED FOR RESEARCH AND EDUCATION PURPOSES ONLY'''
from bs4 import BeautifulSoup as Soup
import json
import urllib
import base64
import logging
import re
import os
import threading

from urllib.request import urlopen, Request, urlretrieve
import requests
from urllib.parse   import quote

from time import sleep
# programtically go through google image ajax json return
# and save links to list
# num_images is more of a suggestion
# it will get the ceiling of the nearest 100 if available

pattern = re.compile("Play\(\d+,'(.*?)'")
AUDIO_URL = "https://audio00.forvo.com/mp3/"


def get_links(query_string, lang):
    # initialize place for links
    links = []
    # step by 100 because each return gives up to 100 links
    #query_string = str(query_string.encode('utf-8').strip())
    #for i in range(0, num_images, 100):

    if lang:
        url = 'https://forvo.com/word/' + quote(query_string) + '/#' + lang
    else:
        url = 'https://forvo.com/word/' + quote(query_string)

    # set user agent to avoid 403 error
    request = Request(url, None, {'User-Agent': 'Mozilla/5.0'})

    # returns json formatted string of the html
    html = urlopen(request).read()

    # parse as json
    #page = json.loads(json_string)

    # html found here
    #html = page[1][1]

    # use BeautifulSoup to parse as html
    new_soup = Soup(html, 'html.parser')

    # all img tags, only returns results of search
    #imgs = new_soup.find_all('li')
    plays = new_soup.find_all("span", "play")

    # loop through images and put src in links list
    for j in range(len(plays)):
        match = pattern.search(plays[j]["onclick"])
        if match:
            links.append(AUDIO_URL + base64.b64decode(match.group(1)).decode())

    return links


def download(term, links, directory):
    threads = []
    for i in range(0, len(links)):

        file_name = 'forvo_%s_%s.mp3' % (quote(term), i)

        thread = threading.Thread(target=urlretrieve, args=(links[i], "./" + directory + "/" + file_name))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    """
    with multiprocessing.Pool(5) as p:
        print('starting download"')
        multiple_results = [p.apply_async(urlretrieve, (links[i], "directory"+str(i)+".mp3",)) for i in range(10)]
        p.close()
        try:
            p.join()
        except TimeoutError:
            logging.error("Timed out waiting to download audio from Forvo")

    """

        #print([res.get(timeout=5) for res in multiple_results])
    return True

def search(term, lang, output="../../addons21/GenericLanguageHelper/user_files/"):
    all_links = get_links(term, lang)
    download(term, all_links, output)
    return len(all_links)


if __name__ == '__main__':
    term = "精确"
    search(term, "zh", output="user_files/")
