#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jason F
# @Time :2019/10/11 21:01

import os
import re
import requests
from bs4 import BeautifulSoup

os.makedirs('D:/py_crawler_res/', exist_ok=True)
main_ul = r'http://ssdut.dlut.edu.cn'
page_ul = 'http://ssdut.dlut.edu.cn/index/'
start_ul = r'http://ssdut.dlut.edu.cn/index/bkstz.htm'
f_path = 'D:/py_crawler_res/'


def filter_href(v_str):  # 过滤链接中的../
    v_str = re.split(r"(\.\./)", v_str.rstrip())[-1]
    return v_str


def filter_p(str_p): # 在直接对标签使用Tag.text获取内容时，中可能存在的<span></span>等会作为text返回，所以要过滤
    str_p = re.split(r'<.*?>', str_p)
    str_p = [''.join(x.split()) for x in str_p]
    str_p = list(filter(lambda x: len(x) != 0,str_p))
    return str_p


def split_d(str_d):  # 分割一下附件文本
    str_d = str_d.split(r'【')[1].split(r'】')
    return str_d[0]


def get_content(ul):
    req = requests.get(ul).content
    soup = BeautifulSoup(req, 'lxml')
    article_list = []
    x = 0
    while True:
        x += 1
        os.makedirs(f_path + '第' + str(x) + '页/', exist_ok=True)
        catalog_list = soup.find_all('div', {'class': 'c_hzjl_list1'})
        for log in catalog_list:
            article_list = log.find_all('li')
        for article in article_list:
            article_name = article.a.text
            article_href = filter_href(article.a['href'])
            article_href = main_ul + '/' + article_href
            get_article(article_href, article_name, x)
        page_down = soup.find('div', {'class': 'page_down'})
        p_next = page_down.find_all('a')
        if p_next[-1].text == '尾页':
            if x == 1:
                ul = r'http://ssdut.dlut.edu.cn/index/' + str(p_next[-2]['href'])
            else:
                ul = r'http://ssdut.dlut.edu.cn/index/bkstz/' + str(p_next[-2]['href'])
            req = requests.get(ul).content
            soup = BeautifulSoup(req, 'lxml')
        else:
            print('---End---')
            return


def get_article(art_ul, art_name, x):
    with open(f_path + '第' + str(x) + '页/' + str(art_name) + '.txt', 'w') as f:
        req = requests.get(str(art_ul)).content
        soup = BeautifulSoup(req, 'lxml')
        art_head = soup.find('h1').text
        art_time_ = soup.find('div', {'align': 'center'})
        art_time_ = filter_p(art_time_.text)
        art_time = '时间： ' + art_time_[0].split('点')[0]
        div_p = soup.find('div', {'class': 'v_news_content'})
        p_list = div_p.find_all('p')
        f.write(art_head + '\n')  # 写入文章标题
        f.write(art_time + '\n')  # 写入文章时间
        for p in p_list: # 写入正文
            con_p = filter_p(p.text)
            for ev_p in con_p:
                ev_p = ev_p.replace('\u2022', ' ')
                f.write(ev_p + '\n')
        form_down = soup.find('form', {'name': '_newscontent_fromname'})
        down_ul = form_down.find_all('ul')
        for ev_ul in down_ul:
            down_list = ev_ul.find_all('a')
            for down in down_list:  # 写入附件
                down_w = '附件： ' + down.text + ' 链接： ' + main_ul + str(down['href'])
                f.write(down_w + '\n')


if __name__ == '__main__':
    get_content(start_ul)
