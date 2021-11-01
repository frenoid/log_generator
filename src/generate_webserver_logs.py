#! /usr/bin/env python3

from datetime import datetime
import json
import random
import os
import sys
import time
import urllib.parse

SESSION_COUNT=150
SESSION_LENGTH=5
OCTET_START = 223
OCTET_END = 255
QPS = 1.5

class IPGenerator:
    def __init__(self, session_count, session_length):
        self.session_count = session_count
        self.session_length = session_length
        self.sessions = {}

    def get_ip(self):
        self.session_gc()
        self.session_create()
        ip = list(self.sessions)[random.randrange(len(self.sessions))]
        self.sessions[ip] = self.sessions[ip] + 1
        return ip

    def session_create(self):
        while len(self.sessions) < self.session_count:
            self.sessions[self.random_ip()] = 0

    def session_gc(self):
        for (ip, count) in list(self.sessions.items()):
            if count >= self.session_length:
                del self.sessions[ip]

    def random_ip(self):
        octets = []
        octets.append(str(random.randrange(OCTET_START) + 1))
        [octets.append(str(random.randrange(OCTET_END))) for i in range(3)]

        return ".".join(octets)

class LogGenerator:
    PRODUCTS = {}

    REQUESTS = {
        "/departments": 40,
        "/department/*DEPARTMENT*/categories": 20,
        "/department/*DEPARTMENT*/products": 10,
        "/categories/*CATEGORY*/products": 5,
        "/product/*PRODUCT*": 10,
        "/add_to_cart/*PRODUCT*": 5,
        "/login": 5,
        "/logout": 2,
        "/checkout": 3,
        "/support": 1
    }

    EXTENSIONS = {
        'html': 40,
        'php': 30,
        'png': 15,
        'gif': 10,
        'css': 5,
    }

    RESPONSE_CODES = {
        200: 85,
	201: 3,
	400: 5,
	403: 2,
        404: 5,
	502: 4,
        503: 3
    }

    USER_AGENTS = {
        "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0": 1,
	"Mozilla/5.0 (Linux; Android 10; M2006C3LVG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36" : 5,
	"Mozilla/5.0 (Linux; Android 7.0; VIE-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36": 10,
	"Mozilla/5.0 (Linux; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.115 Mobile Safari/537.36 GnotsGcoreWebView/1.1,gzip(gfe)": 3,
	"Mozilla/5.0 (Linux; Android 6.0; Philips Xenium V787) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36": 6,
	"Mozilla/5.0 (Linux; arm; Android 7.0; Micromax Q402+) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 YaBrowser/20.8.2.90.00 SA/1 Mobile Safari/537.36": 4,
	"Mozilla/5.0 (Linux; arm_64; Android 10; M2003J15SC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 YaBrowser/20.9.1.66.00 SA/1 Mobile Safari/537.36": 3,
	"Mozilla/5.0 (Windows NT 10.0; WOW64; APCPMS=^N201912310202384272755A9CAC172D4EE63F_4619^; Trident/7.0; rv:11.0) like Gecko": 7,
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 RuxitSynthetic/1.0 v4973080983966115218 t9071033982482470646": 2,
	"Mozilla/5.0 (Linux; Android 9; Nokia 5.1 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36": 4
    }

    DEPARTMENTS = {
    }

    CATEGORIES = {
    }

    def __init__(self, ipgen):
        self.ipgen = ipgen
        self.set_products()
        self.set_departments()
        self.set_categories()
 
    def set_products(self):
        cwd = os.getcwd()
        json_text = open(cwd + '/supermarket_data/products.json', 'r').read()
        products = json.loads(json_text)
        for p in products:
            self.PRODUCTS[p['product_id']] = int(500/p['product_price'])

    def set_departments(self):
        cwd = os.getcwd()
        json_text = open(cwd + '/supermarket_data/departments.json', 'r').read()
        depts = json.loads(json_text)
        for p in depts:
            self.DEPARTMENTS[p['department_name']] = 100/len(depts)

    def set_categories(self):
        cwd = os.getcwd()
        json_text = open(cwd + '/supermarket_data/categories.json', 'r').read()
        cats = json.loads(json_text)
        for p in cats:
            self.CATEGORIES[p['category_name']] = 100/len(cats)

    def write_qps(self, dest, qps):
        sleep = 1.0 / qps
        while True:
            self.write(dest, 1)
            time.sleep(sleep)

    def write(self, dest, count):
        for i in range(count):
            ip = self.ipgen.get_ip()
            request = self.pick_weighted_key(self.REQUESTS)
            product = self.pick_weighted_key(self.PRODUCTS)
            dept    = self.pick_weighted_key(self.DEPARTMENTS)
            cat     = self.pick_weighted_key(self.CATEGORIES)

            request = urllib.parse.quote(request.replace("*PRODUCT*",str(product)).replace("*DEPARTMENT*",dept).replace("*CATEGORY*",cat).lower())

            ext = self.pick_weighted_key(self.EXTENSIONS)
            resp_code = self.pick_weighted_key(self.RESPONSE_CODES)
            resp_size = random.randrange(2 * 1024) + 192;
            ua = self.pick_weighted_key(self.USER_AGENTS)
            date = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0200") # Hard-coded as Python has no standard timezone implementation
            dest.write("%(ip)s - - [%(date)s] \"GET %(request)s HTTP/1.1\" %(resp_code)s %(resp_size)s \"-\" \"%(ua)s\"\n" %
                {'ip': ip, 'date': date, 'request': request, 'resp_code': resp_code, 'resp_size': resp_size, 'ua': ua})
            dest.flush()

    def pick_weighted_key(self, hash):
        total = 0
        for t in hash.values():
            total = total + t
        rand = random.randrange(int(total))

        running = 0
        for (key, weight) in hash.items():
            if rand >= running and rand < (running + weight):
                return key
            running = running + weight

        return hash.keys()[0]

ipgen = IPGenerator(session_count=SESSION_COUNT, session_length=SESSION_LENGTH)
LogGenerator(ipgen).write_qps(sys.stdout, QPS)
