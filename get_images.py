# -*- encoding: utf-8 -*-
'''DISCLAIMER: DUE TO COPYRIGHT ISSUES, IMAGES GATHERED SHOULD
   ONLY BE USED FOR RESEARCH AND EDUCATION PURPOSES ONLY'''
from bs4 import BeautifulSoup as Soup
import json
import urllib
from urllib.request import urlopen, Request, urlretrieve
from urllib.parse   import quote

# programtically go through google image ajax json return
# and save links to list
# num_images is more of a suggestion
# it will get the ceiling of the nearest 100 if available


def get_links(query_string):
    # initialize place for links
    links = []
    # step by 100 because each return gives up to 100 links
    #query_string = str(query_string.encode('utf-8').strip())
    #for i in range(0, num_images, 100):
    url = 'https://www.google.com/search?ei=1m7NWePfFYaGmQG51q7IBg&hl=zh&q=' + quote(query_string) + '&tbm=isch&ved=' \
          '0ahUKEwjjovnD7sjWAhUGQyYKHTmrC2kQuT0I7gEoAQ&start=' \
          '&yv=2&vet=10ahUKEwjjovnD7sjWAhUGQyYKHTmrC2kQuT0I7gEoAQ.1m7NWePfFYaGmQG51q7IBg.i&ijn=1&asearch=' \
          'ichunk&async=_id:rg_s,_pms:s'

    print(url)
    #url = 'https://www.google.com/search?q=' + query_string + '&source=lnms&tbm=isch&sa=X&' \
    #                                                          'ved=0ahUKEwjRuPzEmvDaAhVCX5QKHarMAsAQ_AUICigB&biw=1280&bih=651&async=_id:rg_s,_pms:s'

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


def get_images(links, directory, pre):
    for i in range(10):
        urlretrieve(links[i], "./"+directory+"/"+str(pre)+str(i)+".jpg")


def search_images(terms, output="../../addons21/GenericLanguageHelper/user_files/"):
    for x in range(len(terms)):
        all_links = get_links(terms[x])
        get_images(all_links, output, x)


if __name__ == '__main__':
    terms = ["狗"]
    search_images(terms, output="images/")
