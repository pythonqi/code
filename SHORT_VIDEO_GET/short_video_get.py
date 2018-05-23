# -*- coding:utf-8 -*-
#爬取下载网易云音乐短视频

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlretrieve
from selenium.webdriver.chrome.options import Options

'''获取网页源代码'''
def source_code(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    '''声明浏览器对象'''
    browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        browser.get(url)
        browser.switch_to.frame('g_iframe')
        html = browser.page_source
        browser.close()
        return html
    except Exception as e:
        return None

'''回掉函数，用来显示下载进度'''
def Schedule(a, b, c):
    '''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
    '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    print('%.2f%%'%per)

'''主函数'''
def main():
    print('仅供学习交流,严禁用于商业用途,请于24小时内删除,如有问题请联系作者邮箱pythonqi@outlook.com')
    print('Copyright (c) 2018 派森. All rights reserved.')
    print('')
    url = input('Please enter the website:')
    file_name = input('Please enter the filename:')
    file_name = file_name + '.mp4'
    html = source_code(url)
    if html is None:
        print('网址输入有误')
    else:
        soup = BeautifulSoup(html,'lxml')
        link = soup.find('div', {'class': 'player'}).find('video', {'class': 'media'})
        download = link.attrs['src']
        urlretrieve(download,file_name,Schedule)

main()
