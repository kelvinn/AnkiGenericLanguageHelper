# -*- encoding: utf-8 -*-
'''DISCLAIMER: DUE TO COPYRIGHT ISSUES, IMAGES GATHERED SHOULD
   ONLY BE USED FOR RESEARCH AND EDUCATION PURPOSES ONLY'''
from bs4 import BeautifulSoup as Soup
import json
import urllib
import base64
import re
from urllib.request import urlopen, Request, urlretrieve
from urllib.parse   import quote

# programtically go through google image ajax json return
# and save links to list
# num_images is more of a suggestion
# it will get the ceiling of the nearest 100 if available

pattern = re.compile("Play\(\d+,'(.*?)'")
AUDIO_URL = "https://audio00.forvo.com/mp3/"


def get_links(query_string):
    # initialize place for links
    links = []
    # step by 100 because each return gives up to 100 links
    #query_string = str(query_string.encode('utf-8').strip())
    #for i in range(0, num_images, 100):
    url = 'https://forvo.com/word/%E7%8B%97/#zh'

    print(url)
    
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
        #pronunciation = re.findall("Play\(\d+,'(.*?)'", plays[j]["onclick"])
        match = pattern.search(plays[j]["onclick"])
        if match:
            links.append(url + base64.b64decode(match.group(1)).decode())

    return links


def get_audio(links, directory, pre):
    for i in range(10):
        urlretrieve(links[i], "./"+directory+"/"+str(pre)+str(i)+".mp3")


def search_images(terms, output="../../addons21/GenericLanguageHelper/user_files/"):
    for x in range(len(terms)):
        all_links = get_links(terms[x])
        get_audio(all_links, output, x)


if __name__ == '__main__':
    terms = ["狗"]
    search_images(terms, output="audio/")
