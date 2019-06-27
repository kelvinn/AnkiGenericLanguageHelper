# -*- encoding: utf-8 -*-
'''DISCLAIMER: DUE TO COPYRIGHT ISSUES, IMAGES GATHERED SHOULD
   ONLY BE USED FOR RESEARCH AND EDUCATION PURPOSES ONLY'''
from urllib.parse import quote
import json
import os
import re
import threading
import unicodedata

from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
import ssl
import requests


# programtically go through google image ajax json return
# and save links to list
# num_images is more of a suggestion
# it will get the ceiling of the nearest 100 if available

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ssl._create_default_https_context = ssl._create_unverified_context


class Config:
    def __init__(self):
        with open("../../addons21/AnkiGenericLanguageHelper/config.json") as file:  # Use file to refer to the file object
            data = file.read()
            self.parsed = json.loads(data)

    def forvo_api_key(self):
        return os.getenv('FORVO_API_KEY') or self.parsed.get('forvo_api_key')

    def bing_api_key(self):
        return os.getenv('BING_API_KEY') or self.parsed.get('bing_api_key')


def silent_urlretrieve(url, local_filename):
    try:
        urlretrieve(url, local_filename)
        return True
    except HTTPError:
        return False


def slugify(value, allow_unicode=True):
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
        c = Config()
        self.forvo_api_key = c.forvo_api_key()
        self.audio_url = "https://apifree.forvo.com"

    def get_links(self, query_string, lang):

        # initialize place for links
        links = []
        query_string = query_string.replace(" ", '') # Forvo API doesn't deal that well with multiple words
        url = f'https://apifree.forvo.com/id_order/rate_desc/key/{self.forvo_api_key}/format/json/action/word-pronunciations/word/' \
              f'{quote(query_string)}/language/{lang}'

        # set user agent to avoid 403 error
        request = Request(url, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                                                    'like Gecko) Chrome/44.0.2403.157 Safari/537.36'})

        # returns json formatted string of the html
        response = urlopen(request, context=ctx).read()

        d = json.loads(response)
        for item in d['items']:
            links.append(item.get('pathmp3'))

        return links

    def download(self, term, links, directory):
        threads = []
        links = links[:5]
        filenames = []
        for i in range(len(links)):

            file_name = slugify('glt_forvo_%s_%s' % (term, i)) + ".mp3"
            filenames.append(file_name)

            thread = threading.Thread(target=urlretrieve, args=(links[i], "./" + directory + "/" + file_name))
            threads.append(thread)

        for thread in threads:
            thread.start()

        # Blocks returning filenames until all but 5 threads have died and or downloaded successfully
        # Probably should use a thread pool executer...
        num_active = len(threads)
        while num_active > 0:
            num_active = [thread.is_alive() for thread in threads].count(True)

        return filenames

    def search(self, term, lang, output="../../addons21/AnkiGenericLanguageHelper/user_files/"):
        all_links = self.get_links(str(term), lang)
        filenames = self.download(str(term), all_links, output)
        return filenames


class BingImages:
    def __init__(self):
        c = Config()
        self.subscription_key = c.bing_api_key()
        self.search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
        self.search_term = "puppies"
        self.market = c.parsed.get('image_market')

    def get_links(self, query_string, lang):
        headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        params = {"q": query_string, "cc": self.market, "count": 100, "safeSearch": "Strict"}

        response = requests.get(self.search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        links = [link['thumbnailUrl'] for link in search_results['value']]
        return links

    def download(self, term, links, directory):
        threads = []

        links = links[:95]
        filenames = []
        for i in range(len(links)):

            file_name = slugify('glt_%s_%s' % (term, i)) + ".jpg"
            filenames.append(file_name)

            thread = threading.Thread(target=silent_urlretrieve, args=(links[i], "./" + directory + "/" + file_name))
            threads.append(thread)

        for thread in threads:
            thread.start()

        # Blocks returning filenames until all but 5 threads have died and or downloaded successfully
        num_active = len(threads)
        while num_active > 5:
            num_active = [thread.is_alive() for thread in threads].count(True)

        return filenames

    def search(self, term, lang, image_text, output="../../addons21/AnkiGenericLanguageHelper/user_files/"):
        search_term = image_text or term
        all_links = self.get_links(query_string=str(search_term).encode(), lang=lang)
        filenames = self.download(str(term), all_links, output)
        return filenames


if __name__ == '__main__':
    import time
    example_term = "美國"
    bi = BingImages()
    start = time.time()
    image_filenames = bi.search(term=example_term, image_text=example_term, lang='zh', output='user_files/')
    end = time.time()
    print(end - start)
    print(len(image_filenames))

    forvo = Forvo()
    audio_filenames = forvo.search(example_term, lang='zh', output='user_files/')
    print(len(audio_filenames))
