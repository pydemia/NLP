#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 14:41:23 2017

@author: Young Ju Kim
"""


import re
import json
import os
import pickle
import datetime as dt
import multiprocessing as mpr
from pprint import pprint

import pandas as pd
import feedparser
import urllib
from bs4 import BeautifulSoup as bs


# %% Definition

def rss_crawler(url, press_key):
    parsed_dict = feedparser.parse(url)
    print(parsed_dict.feed['title'])
    links = [{'press': press_key.split('_')[0],
              'title': entry.title,
              'link': entry.link,
              'datetime': entry.published} for entry in parsed_dict['entries']]
    return links


def news_scrapper(url, source):
    
    src_dict = {'chosun': None,
                'hani': None,
                'mk': None,
                'hk': None}

    try:
        page = urllib.request.urlopen(url)
        soup = bs(page, "html5lib")

        if source == 'chosun':
            raw_html = str(soup.find_all('div', attrs={'par'}))[1:-1]
            
            if raw_html != '[]':

                # Extraction
                pattern = re.compile(r'<[^<>]*>')
                extracted = ''.join(re.split(pattern, raw_html))

                # Substitution
                pattern = re.compile(r'^\[|google[^;]+;|\n|\t|$]')
                substituted = re.sub(pattern, '', extracted)

                # End of Article
                sliced = substituted

            elif raw_html == '[]':
                raw_html = str(soup.find_all('div', attrs='article'))[1:-1]

                # Extraction
                pattern = re.compile(r'<[^<>]*>')
                extracted = ''.join(re.split(pattern, raw_html))

                # Substitution
                pattern = re.compile(r'^\[|google[^;]+;|\n|\t|$]')
                substituted = re.sub(pattern, '', extracted)

                # End of Article
                pattern = re.compile(r'^\s*\S+ : \d+\.\d+\.\d+ \d+:\d+ \s* (.+)]')
                sliced = ''.join(re.findall(pattern, substituted))

        elif source == 'hani':
            raw_html = str(soup.find_all('div', attrs='text'))[1:-1]

            # Extraction
            pattern = re.compile(r'<[^<>]*>')
            extracted = ''.join(re.split(pattern, raw_html))

            # Substitution
            pattern = re.compile(r'^\[|google[^;]+;|\n|\t|$]')
            substituted = re.sub(pattern, '', extracted)

            # End of Article
            pattern = re.compile(r"^[\s,]*(.+[.,']+) .+ [\S]*기자 [\w]+@hani\.co\.kr")
            sliced = ''.join(re.findall(pattern, substituted))
            
        elif source == 'mk':
            raw_html = str(soup.find_all('div', attrs='art_txt'))

            # Extraction
            pattern = re.compile(r'<[^<>]*>')
            extracted = ''.join(re.split(pattern, raw_html))

            # Substitution
            pattern = re.compile(r'^\[|google[^;]+;|\n|\t|$\]')
            substituted = re.sub(pattern, '', extracted)

            # End of Article
            pattern = re.compile(r'^[\s,]*(.+)\[.+\]\[ⓒ 매일경제 &amp; mk.co.kr\.*')
            sliced = ''.join(re.findall(pattern, substituted))

        elif source == 'hk':
            #raw_html = str(soup.find_all('div', attrs={'news_article', 'wrap_article'}))[1:-1]
            raw_html = str(soup.find_all('div', attrs={'wrap_article'}))[1:-1]

            if raw_html == '[]':
                raw_html = str(soup.find_all('div', attrs={'news_article'}))[1:-1]

            # Extraction
            pattern = re.compile(r'<[^<>]*>')
            extracted = ''.join(re.split(pattern, raw_html))

            # Substitution
            pattern = re.compile(r'^\[|google[^;]+;|\n|\t|$]')
            substituted = re.sub(pattern, '', extracted)

            # End of Article
            pattern = re.compile(r"(.+[\.\']+).+ \S+ [\w]+@hankyung\.com")
            sliced = ''.join(re.findall(pattern, substituted))

    except urllib.error.HTTPError as e:
        print(url, str(e))
        sliced = ''
    
    print('%s (%s)' % (source, url))
    
    return sliced


def scrap_from_rss(feed_list):
    res = [dict(feed, **{'body': news_scrapper(feed['link'], feed['press'])})\
           for feed in feed_list]
    return res


def rss_dumper(rss_dict, dirname, worker=1):

    # Get the RSS Feeds
    print('Listing...')
    feed_list = [rss_crawler(rss_url, press) for press, rss_url in rss_dict.items()]
    
    # Print Lengths of each Feeds
    pprint({press: len(feed) for press, feed in zip(rss_dict, feed_list)})

    print('Scrapping...')
    # Get the Full article of the Feeds
    pool = mpr.pool.Pool(processes=worker)
    response = pool.map(scrap_from_rss, feed_list)
    
    news_list = sum(response, [])
    data = pd.DataFrame.from_dict(news_list)
        
    print('\rScrapping...Done')

    os.makedirs(dirname, exist_ok=True)
    date_str = dt.datetime.now().strftime('%Y%m%d')
    filename = '/'.join([dirname, date_str])

    print("Dumping to '%s.*' ..." % filename)
    
    # Dump the result
    with open('%s.json' % filename, "w") as json_file:
        json_file.write(json.dumps(news_list))


    full_txt = '\n'.join(data['body'])
    with open('%s.txt' % filename, 'w') as text_file:
        text_file.write(full_txt)
        
    full_body_list = data['body'].tolist()
    with open('%s.dump' % filename, 'wb') as byte_file:
        pickle.dump(full_body_list, byte_file)

    print("Dumping to '%s /' ...Done" % filename)

    return news_list


press_rss_dict = {'chosun_politics': 'http://www.chosun.com/site/data/rss/politics.xml',
                  'chosun_national': 'http://www.chosun.com/site/data/rss/national.xml',
                  'chosun_international': 'http://www.chosun.com/site/data/rss/international.xml',
                  'chosun_culture': 'http://www.chosun.com/site/data/rss/culture.xml',
                  'hani_politics': 'http://www.hani.co.kr/rss/politics/',
                  'hani_economy': 'http://www.hani.co.kr/rss/economy/',
                  'hani_society': 'http://www.hani.co.kr/rss/society/',
                  'hani_international': 'http://www.hani.co.kr/rss/international/',
                  'hani_culture': 'http://www.hani.co.kr/rss/culture/',
                  'hani_science': 'http://www.hani.co.kr/rss/science/',
                  'mk_economy': 'http://file.mk.co.kr/news/rss/rss_30100041.xml',
                  'mk_politics': 'http://file.mk.co.kr/news/rss/rss_30200030.xml',
                  'mk_society': 'http://file.mk.co.kr/news/rss/rss_50400012.xml',
                  'mk_international': 'http://file.mk.co.kr/news/rss/rss_30300018.xml',
                  'mk_corp': 'http://file.mk.co.kr/news/rss/rss_50100032.xml',
                  'mk_stock': 'http://file.mk.co.kr/news/rss/rss_50200011.xml',
                  'mk_realestate': 'http://file.mk.co.kr/news/rss/rss_50300009.xml',
                  'mk_culture': 'http://file.mk.co.kr/news/rss/rss_30000023.xml',
                  'hk_stock': 'http://rss.hankyung.com/new/news_stock.xml',
                  'hk_economy': 'http://rss.hankyung.com/new/news_economy.xml',
                  'hk_industry': 'http://rss.hankyung.com/new/news_industry.xml',
                  'hk_realestate': 'http://rss.hankyung.com/new/news_estate.xml',
                  'hk_politics': 'http://rss.hankyung.com/new/news_politics.xml',
                  'hk_society': 'http://rss.hankyung.com/new/news_society.xml',
                 }


# %% Save the data

if __name__ == '__main__':

    rss_dumper(press_rss_dict, 'news_20171129', worker=4)

# %% Load the data

if __name__ == '__main__':

    # `DataFrame` from `json`
    fname = 'news_20171129/20171129.json'
    data = pd.read_json(fname)
    data['datetime'] = pd.to_datetime(data['datetime'])
    print(data)

    # `text`
    fname = 'news_20171129/20171129.txt'
    with open(fname, 'r') as f:
        full_txt = f.read()
    print(full_txt)

    # `byte` Object
    fname = 'news_20171129/20171129.dump'
    with open(fname, 'rb') as f:
        full_list = pickle.load(f)
    print(full_list)

