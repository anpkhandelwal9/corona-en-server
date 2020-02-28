import requests
from collections import deque
from datetime import datetime
import re
import json
from time import sleep
import pytz
from functools import cmp_to_key
from copy import deepcopy

class NaverNewsPoller(object):
    def __init__(self):

        self.regexp_lists = {
            "overall": [re.compile("^.*확진자.*$")],
            "suwon": [re.compile("^.*수원.*$")],
            "gyeonggi": [re.compile("^.*경기.*$")],
            "travel": [re.compile("^.*입국.*$")],
            "samsung": [re.compile("^.*삼성.*$")],
            "chungju": [re.compile(".*충주.*$")],
            "india": [re.compile(".*인도.*$")]
        }

        self.threads = list(self.regexp_lists.keys())

        self.news_lists = {}
        self.files = {}
        for thread in self.threads:
            self.news_lists[thread] = []
            self.files[thread] = thread+"-news.txt" 
            

        self.time_format = "%a, %d %b %Y %H:%M:%S %z"
        self.last_polled_time = datetime.strptime("2020-02-27 00:00:00 +0900", "%Y-%m-%d %H:%M:%S %z")
        self.new_polled_time = None

        self.refresh_interval = 2*60
        self.news_url = "https://openapi.naver.com/v1/search/news.json"
        self.translate_url = "https://openapi.naver.com/v1/papago/n2mt"

        self.client_id = "CDIP1v_JfG9jMGOngC6i"
        self.client_secret = "22y9ZSK1LY"
        self.translate_client_id = "CDIP1v_JfG9jMGOngC6i"
        self.translate_client_secret = "22y9ZSK1LY"
        self.time_polled_file = "time.txt"

        self.tz = pytz.timezone('Asia/Seoul')

    def __load_last_polled_time(self):
        try:
            with open(self.time_polled_file, 'r') as infile:
                self.last_polled_time =  datetime.strptime(infile.read(), self.time_format)
        except Exception as e:
            return
    
    def __make_files(self):
        for thread in self.threads:
            try:
                with open(self.files[thread], 'r', encoding="utf-8") as infile:
                    continue
            except Exception as e:
                with open(self.files[thread], 'w', encoding="utf-8") as infile:
                    continue

    def __save_last_polled_time(self):
        with open(self.time_polled_file, 'w') as outfile:
            outfile.write(self.last_polled_time.strftime(self.time_format))

    def __send_request(self, method, url, headers=None, params=None, data=None, files=None, proxies=None, json=True):
        req = requests.Request(method=method, url=url, headers=headers, files=files, data=data, params=params)
        try:
            req_prep = req.prepare()
            with requests.Session() as sess:
                resp = sess.send(req_prep, verify=False)
                return resp
        except Exception as e:
            print(e)
            return None

    def __check_if_include(self, headline, time_string, regexp_list):
        if datetime.strptime(time_string, self.time_format) <= self.last_polled_time:
            return False
        for regexp in regexp_list:
            if not(re.match(regexp, headline)):
                return False
        return True

    def cmp_items(self, a, b):
        if datetime.strptime(a["pubDate"], self.time_format) > datetime.strptime(b["pubDate"], self.time_format):
            return 1
        return 0

    def __parse_news_response(self, response_content):
        try:
            response_content["items"] = sorted(response_content["items"],key=cmp_to_key(self.cmp_items))
            for item in response_content["items"]:
                if self.new_polled_time == None:
                    self.new_polled_time = datetime.strptime(item["pubDate"], self.time_format)
                self.new_polled_time = max(datetime.strptime(item["pubDate"], self.time_format), self.new_polled_time)
                translated_string  = ""
                for thread in self.threads:
                    if self.__check_if_include(item["title"], item["pubDate"], self.regexp_lists[thread]):
                        if translated_string == "":
                            translated_string = self.__translate(item["title"])
                        if translated_string == "":
                            self.news_lists[thread].append(item["title"] + "\t" + item["title"] + "\t"+item["pubDate"]+"\t"+ item["link"])
                        else:
                            self.news_lists[thread].append(translated_string + "\t" + item["title"] +  "\t" + item["pubDate"]+"\t"+ item["link"])
        except Exception as e:
            return
                
                
    def __add_to_file(self, filename, list_obj):
        if len(list_obj) == 0:
            return
        with open(filename, 'r+', encoding="utf-8") as f:
            content = f.read()
            f.seek(0, 0)
            f.write('\n'.join(list_obj) + '\n' + content)

    def __limit_file_size(self, filename, limit=100):
        list_read  = []
        with open(filename, 'r', encoding="utf-8") as infile:
            list_read = infile.read().splitlines()
        if len(list_read) > limit:
            list_read = list_read[0:limit]
        if '' in list_read:
            list_read.remove('')
        if len(list_read) == 0:
            return
        with open(filename, 'w', encoding="utf-8") as outfile:
            outfile.write('\n'.join(list_read) + "\n")

    def __parse_translate_response(self, response_content):
        try:
            return response_content["message"]["result"]["translatedText"]
        except Exception as e:
            return ""
    
    def __translate(self, src_str, src_lang="ko", tar_lang="en"):
        headers = {
            "X-Naver-Client-Id": self.translate_client_id,
            "X-Naver-Client-Secret": self.translate_client_secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "source": src_lang,
            "target": tar_lang,
            "text": src_str
        }
        resp = self.__send_request("POST", self.translate_url, headers=headers, data=data)
        return self.__parse_translate_response(json.loads(resp.text))

    def __search_news_and_update(self, query_str="코로나 바이러스", sort="date", start=1, display=100):
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        params = {
            "query": query_str,
            "sort": sort,
            "start": start,
            "display": display
        }
        resp = self.__send_request("GET", self.news_url, headers=headers, params=params)
        response_text = resp.text
        response_text = response_text.replace('<b>', '')
        response_text = response_text.replace('</b>', '')
        self.__parse_news_response(json.loads(response_text))
    
    def __poll_once(self, limit=200, start=1, display=100):
        self.__load_last_polled_time()
        for thread in self.threads:
            self.news_lists[thread].clear()
        while start <= limit:
            self.__search_news_and_update(start=start)
            start += display
        for thread in self.threads:
            self.__add_to_file(self.files[thread], self.news_lists[thread])
            self.__limit_file_size(self.files[thread])
        self.last_polled_time = self.new_polled_time
        self.__save_last_polled_time()

    def repeated_poll(self):
        self.__make_files()
        while True:
            print("Polling.....")
            self.__poll_once()
            sleep(self.refresh_interval)

N = NaverNewsPoller()
N.repeated_poll()




    




            
        
        
