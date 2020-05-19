from selectorlib import Extractor
import requests 
import json 
from time import sleep
import ast
import urllib.request

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('./selectors.yml')

def scrapeImagesUrl(url):    
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': user_agent
    }
    try :
        r = requests.get(url, headers=headers, )
        if r.status_code != 200: return None
        data = e.extract(r.text)
        return list(ast.literal_eval(data["images"]).keys())[0]
    except ValueError:
        return None


