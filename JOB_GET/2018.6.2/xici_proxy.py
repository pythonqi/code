import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import mysql.connector

'''获取网页的源代码'''
def GetHtmlText(url):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return None


'''列表存放速度较快的代理ip'''
def FillIpList(lst,html):
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find('table',{'id':'ip_list'}).tr.next_siblings:
        try:
            speed = tr.find('div',{'class': 'bar'}).attrs['title']
            match = re.search(r'\d.\d{3}',speed)
            if float(match.group(0)) < 1:
                ip = tr.find('td', {'class': 'country'}).next_sibling.next_sibling
                port = ip.next_sibling.next_sibling
                ip_port = ip.text + ':' + port.text
                lst.append(ip_port)
        except:
            continue

'''保存可用的代理ip至txt文件'''
def StoreIpContent(lst,fpath):
    with open(fpath,'w') as file:
        for i in range(len(lst)):
            file.write(lst[i]+'\n')

'''存到数据库'''
def PutInMysql(lst):
    db = mysql.connector.connect(host='localhost', user='root', password='123456', port=3306, db='spiders')
    cursor = db.cursor()
    score = 10
    sql = 'REPLACE INTO proxy(ip_port, score) values(%s, %s)'
    for i in lst:
        try:
            cursor.execute(sql, (i, score))
            print((i))
            db.commit()
        except:
            db.rollback()
    db.close()

def main():
    pages = int(input('输入爬取ip页数:'))
    #fpath = 'C://Users/35175/Desktop/ip.txt'
    ip_list = []
    for i in range(1,pages+1):
        url = 'http://www.xicidaili.com/nn/'+str(i)
        html = GetHtmlText(url)
        FillIpList(ip_list,html)
    #StoreIpContent(ip_list,fpath)
    PutInMysql(ip_list)


main()



'''
def IpTest(proxy):
    proxies = {
        'http':'http://' + proxy,
        'https':'https://' + proxy,
    }
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        r = requests.get('https://www.zhipin.com/',headers=headers,proxies=proxies,timeout=2)
        r.raise_for_status()
        return True
    except:
        return False
'''