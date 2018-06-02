import csv
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import mysql.connector


def GetHtmlText(url):
    '''获取网页的源代码'''
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}  # 构造随机请求头，增加一定的反爬能力
        r = requests.get(url, timeout=5, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return None

def GetHtmlText_ip(url, proxy):
    '''获取网页的源代码(代理模式)'''
    try:
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy,
        }
        ua = UserAgent()
        headers = {'User-Agent': ua.random}  # 构造随机请求头，增加一定的反爬能力
        r = requests.get(url, timeout=2, headers=headers, proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return None


def fillJobList(lst,html):
    '''数据以列表字典的形式存储'''
    soup = BeautifulSoup(html,'html.parser')
    dic = {}
    for job in soup.findAll('div',{'class':'info-primary'}):
        try:
            position = job.find('div',{'class':'job-title'}).text
            pay = job.find('span',{'class':'red'}).text
            edu = job.find('p').text
            dic['position'] = position
            dic['pay'] = pay
            dic['edu'] = edu
            next_url = job.find('a').attrs['href']
            next_url = 'https://www.zhipin.com'+ next_url
            next_html = GetHtmlText(next_url)
            next_soup = BeautifulSoup(next_html,'html.parser')
            detail = next_soup.find('div',{'class':'text'}).text
            dic['detail'] = detail
            lst.append(dic.copy())
        except:
            continue


def fillJobList_ip(lst, html, proxy):
    '''数据以列表字典的形式存储（代理模式）'''
    soup = BeautifulSoup(html,'html.parser')
    dic = {}
    for job in soup.findAll('div',{'class':'info-primary'}):
        try:
            position = job.find('div',{'class':'job-title'}).text
            pay = job.find('span',{'class':'red'}).text
            edu = job.find('p').text
            dic['position'] = position
            dic['pay'] = pay
            dic['edu'] = edu
            next_url = job.find('a').attrs['href']
            next_url = 'https://www.zhipin.com'+ next_url
            while True:
                next_html = GetHtmlText_ip(next_url, proxy)
                if next_html is not None:
                    break
            next_soup = BeautifulSoup(next_html,'html.parser')
            detail = next_soup.find('div',{'class':'text'}).text
            dic['detail'] = detail
            lst.append(dic.copy())
        except:
            continue

def storeJobInfo(lst, fpath):
    '''用csv文件存放爬取的数据'''
    keys = lst[0].keys()
    with open(fpath,'w',encoding='utf-8',newline ='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(lst)


def PutInMysql(lst):
    '''用Mysql存放爬取的数据'''
    db = mysql.connector.connect(host='localhost', user='root', password='123456', db='spiders', port=3306)
    cursor = db.cursor()
    sql = 'INSERT INTO bossjobinfo(position, pay, edu, detail) values(%s, %s, %s, %s)'
    i = 0
    for dic in lst:
        i += 1
        try:
            cursor.execute(sql, tuple(dic.values()))
            print('success'+str(i))
            db.commit()
        except:
            print('Failed'+str(i))
            db.rollback()
    db.close()

def PopIp():
    '''从mysql中取出代理ip'''
    db = mysql.connector.connect(host='localhost', user='root', password='123456', port=3306, db='spiders')
    cursor = db.cursor()
    sql = 'SELECT ip_port FROM proxy'
    cursor.execute(sql)
    rows = cursor.fetchall()
    db.close()
    return rows


def main():
    '''主函数'''
    start = time.clock()
    keywords = input('输入职位:')
    pages = int(input('获取页数:'))
    mode = input('代理模式(y/n):')
    #output_file = 'C://Users/35175/Desktop/Job.csv'
    job_list = []

    if mode.lower()=='n':
        for i in range(1,pages+1):
            url ='https://www.zhipin.com/c101210100/h_101210100/?query='+keywords+'&page='+str(i)
            html = GetHtmlText(url)
            if html is None:
                print('无法获取网页源代码，爬虫失败')
                break
            else:
                fillJobList(job_list, html)

    elif mode.lower()=='y':
        rows = PopIp()
        j = 0
        for i in range(1,pages+1):
            url ='https://www.zhipin.com/c101210100/h_101210100/?query='+keywords+'&page='+str(i)
            while True:
                print(j)
                proxy = ''.join(rows[j])
                html = GetHtmlText_ip(url, proxy)
                if html is not None:
                    print(proxy)
                    fillJobList_ip(job_list, html, proxy)
                    break
                elif j >= len(rows)-1: # 循环所有ip无法使用，再次循环
                    j = 0
                else:
                    j += 1


    PutInMysql(job_list) # 存到数据库
    '''storeJobInfo(job_list, output_file)  # 存到csv文件'''
    end = time.clock() - start
    print('爬虫完毕，耗时:', end)


main()






