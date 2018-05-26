import csv
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



'''获取网页的源代码'''
def GetHtmlText(url):
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random} #构造随机请求头，增加一定的反爬能力
        r = requests.get(url, timeout=5, headers=headers)
        r.raise_for_status() #判断r若果不是200，产生异常requests.HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text #http响应内容的字符串形式，即URL返回的页面内容
    except:
        return None


'''数据以列表字典的形式存储'''
def fillJobList(lst,html):
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

'''用csv文件存放爬取的数据'''
def storeJobInfo(lst, fpath):
    keys = lst[0].keys()
    with open(fpath,'w',encoding='utf-8',newline ='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(lst)

'''主函数'''
def main():
    keywords = input('输入职位:')
    pages = int(input('获取页数:'))
    output_file = 'C://Users/35175/Desktop/Job.csv'
    job_list = []
    for i in range(1,pages+1):
        url ='https://www.zhipin.com/c101210100/h_101210100/?query='+keywords+'&page='+str(i)
        html = GetHtmlText(url)
        fillJobList(job_list, html)
    storeJobInfo(job_list, output_file)



start = time.clock()
main()
end = time.clock() - start
print('爬虫完毕，耗时:',end)