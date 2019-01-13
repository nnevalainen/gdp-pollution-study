
from hashlib import md5
import io
import logging
import logging.config
import os
import pickle
import sys
from zipfile import ZipFile

from bs4 import BeautifulSoup
import requests

class GDPCralwer:

    def __init__(self, dest=None):

        self.base_url = "https://data.worldbank.org"
        self.config_file = "gdp-crawler.ini"

        self.dest = dest if dest else 'dest'
        if not os.path.exists(self.dest):
            os.makedirs(self.dest)

        self.logger = self._get_logger()
        self.logger.info('Crawler created')
    

    def run(self):

        content = self._get_cached(self.base_url + "/country")
        soup = BeautifulSoup(content, features="html.parser") 
        
        sections = soup.find_all('section')
        
        for section in sections:
            links = section.find_all('a', href=True)
            for link in links:
                self.get_single_country(link['href'])

    def get_single_country(self, url):
        """

        """
        country = url.split('?')[0].split('/')[-1]
        
        content = self._get_cached(self.base_url + url)
        soup = BeautifulSoup(content, features='html.parser')
        dl = soup.find("div", {"class": "btn-item download"})

        hrefs = dl.find_all('a', href=True)
        href = [e['href'] for e in hrefs if e['href'][-3:] == "csv"][0]

        
        r = self._get(href)

        destdir = os.path.join(self.dest, country)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        z = ZipFile(io.BytesIO(r.content))
        z.extractall(destdir)

    def _get_logger(self):
        """
        Read logging config file and return a configured logger

        Configured logger contains following handlers:
            FileHandler: level=DEBUG
            StreamHandler: level=ERROR

        Returns:
            logging.logger
        """
        fname = os.path.join(os.path.dirname(__file__), self.config_file)
        logging.config.fileConfig(fname)
        return logging.getLogger(__name__)

    def _get_cached(self, url, params={}):
        """
        Perform GET or load old file from cache
        """
        url_to_get = url + "?"
        for key in sorted(params.keys()):
            url_to_get += "{}={}&".format(key, params[key])
        url_to_get = url_to_get[:-1]

        print(url_to_get)

        url_hash = md5(url_to_get.encode('ascii')).hexdigest()
        cache_fn = "cached-url-{}.pkl".format(url_hash)

        try:
            with open(os.path.join('cached',cache_fn), 'rb') as f:
                content = f.read()
                print("Return cached")
        except:
            r = self._get(url, params)
            content = r.content
            with open(os.path.join('cached', cache_fn), 'wb') as f:
                f.write(content)

        return content

    def _get(self, url, params=None):
        """
        Wrap requests.get with additional logging

        Params:
            url (string)
            params (dir):   Python directory object containing additional url params
                            e.g. {season: '2018', id: '8'} might render to
                            "https://statsapi.web.nhl.com/api/v1/url?season=2018&id=8"

        Returns:
            (requests.response) response
        """
        r = requests.get(url, params=params)

        if r.status_code == 200:
            self.logger.info(
                '{status} - GET {url}'.format(status=r.status_code, url=r.url))
        else:
            self.logger.warning(
                '{status} - GET {url}'.format(status=r.status_code, url=r.url))

        return r

    


if __name__ == "__main__":
    
    crawler = GDPCralwer()
    crawler.run()


