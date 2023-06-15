import requests
from bs4 import BeautifulSoup
import os
import time
import pymysql
import random
conn    = pymysql.connect("localhost", "root", "root", "tutu1", charset='utf8')
cursor  = conn.cursor()


# 当前路径
BASE_PATH = '.'
quit()
# input = input('请输入爬取页数：')

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Referer": "https://www.meitulu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
}


def getDetailImage(post_id, fromId, pageNumber, __i) :
    post_id = int(post_id)
    page = int((pageNumber / 5)) + 1
    for index in range(page):
        if index > 0:
            if index > 1:
                url = 'https://www.meitulu.com/item/' + str(fromId) + '_' + str(index) + '.html'
            else:
                url = 'https://www.meitulu.com/item/' + str(fromId) + '.html'
            # 生成IP
            ip1 = str(random.randint(100, 249))
            ip2 = str(random.randint(100, 249))
            ip3 = str(random.randint(100, 249))
            ip4 = str(random.randint(100, 249))

            proxies = {'http://': 'http:' + ip1 + '.' + ip2 + '.' + ip3 + '.' + ip4}
            html = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            if html.status_code == 200:
                soup = BeautifulSoup(html.content, 'lxml')
                imgBoxList = soup.select('.content img')

                for key, value in enumerate(imgBoxList):
                    src = value['src']
                    alt = value['alt']
                    # 下载详情页
                    res = requests.get(src, headers=headers, proxies=proxies, timeout=None)

                    # 保存的路径
                    saveRelaName = '/images/' + str(fromId) + '/'
                    # 文件名
                    fileName = str(int(time.time())) + '_' + str(random.randint(100000, 999999)) + '.png'
                    # 保存的完整路径
                    savePath = BASE_PATH + '/images/' + str(fromId) + '/'
                    # 数据库要存储的文件名称
                    saveName = saveRelaName + fileName
                    # 真是路径
                    realSavePath = savePath + fileName
                    if not os.path.exists(savePath):
                        os.makedirs(savePath, 0o777)
                    _key = key + 1
                    with open(realSavePath, 'wb') as f:
                        f.write(res.content)
                        print('正在抓取第' + str(__i + 1) + '条' + str(index + 1) + '页，第' + str(_key) + '张')

                    # 向数据库写入图片数据
                    postImagesSql = 'insert into zcl_article_image(post_id,image,title,alt) values(%s,%s,%s,%s)'
                    insertData = [post_id, saveName, saveName, alt]
                    cursor.execute(postImagesSql, insertData)
                    conn.commit()
    time.sleep(1)
    print(post_id)
    # 更新文章表中的状态
    sql = "UPDATE zcl_portal_article SET is_del = 1 WHERE id = %d" % (post_id)
    cursor.execute(sql)
    conn.commit()


# 查询要
getRangeSql = 'select id,from_id,image_num from zcl_portal_article where is_del = 0  order by id asc limit 20';
cursor.execute(getRangeSql)
results = cursor.fetchall()

for i,fromId in enumerate(results) :
    getDetailImage(fromId[0], fromId[1], fromId[2], i)
    time.sleep(2)
