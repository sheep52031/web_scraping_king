import json

import feedparser

import requests
from lxml import etree
from io import StringIO
import jieba
import pandas as pd
import time
import random


import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


from collections import Counter

# 要爬取的RSS網站
rss_url = "https://money.udn.com/rssfeed/news/"

# 解析RSS
newsFeed = feedparser.parse(rss_url)

# 查看文章數與對應url
# i = 1
# for e in newsFeed['entries']:
#     title = e['title']
#     link_url = e['links'][0]['href']
#     print("%s, %s, %s"%(i, title, link_url))
#     i = i + 1



# 載入繁體字jieba分詞辭典檔
jieba.set_dictionary('jieba_data/dict.txt.big')


#設定 request header
user_agent =  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"

my_headers = {
    'User-Agent': user_agent,
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "accept-encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "cache-control": "no-cache",
    "Accept-Charset": "UTF8,utf-8;q=0.7,*;q=0.7"
}



#連續爬文章
each_article_text_list = []
for e in newsFeed['entries']:
    url = e['links'][0]['href']
    print(url)
    r = requests.get(url, headers = my_headers)
    if r.status_code == 200:
        parse_tree = etree.parse(StringIO(r.text), etree.HTMLParser())
        # 抓下來的HTML轉成
        # XPath就是一种根据"地址"来"找人"的语言 
        article_elements = parse_tree.xpath('//*[@id="article_body"]//p')
        for a_part in article_elements:
            if type(a_part.text) is str:
                each_article_text_list.append(a_part.text.strip())         # 刮下來文字
        sleep_time = random.randint(3,10)
        print("sleep time: %s sec"%(sleep_time))
        time.sleep(sleep_time)                                             # 模擬人休息
    all_article_text = ''.join(each_article_text_list)                     # 匯入全部文章



# save raw_text_data as txt
with open("text_freq.txt",'w') as f:
    seg_words_str = "".join(all_article_text)
    f.write(seg_words_str)


# 讀取raw_text_data
with open("text_freq.txt",'r') as f:
    seg_words_list = f.read()



# 導入Stopwords
with open(file='jieba_data/stop_words.txt', mode='r', encoding='utf-8') as file:
    stop_words = file.read().split('\n')




# # 開始分詞 文字資料清洗 
seg_stop_words_list = []
seg_words_list = jieba.lcut(all_article_text)



with open("text_freq.json",'w') as f:
    f.write(str(seg_words_list))


# 去除禁用字詞
for term in seg_words_list:
    if term not in stop_words:
        seg_stop_words_list.append(term)


# 以空白區隔文字
seg_words = ' '.join(seg_words_list)


# 計數文字頻率
seg_stop_counter = Counter(seg_stop_words_list)


# 文字存成JSON
seg_stop_counter_dict = dict(seg_stop_counter)

# with open("text_freq.json",'w') as f:
#     json.dump(seg_stop_counter_dict, f)

# 畫出文字雲
wordcloud = WordCloud(font_path='fonts/TaipeiSansTCBeta-Regular.ttf',background_color="white").generate_from_frequencies(seg_stop_counter)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()




