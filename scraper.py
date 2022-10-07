import requests
from bs4 import BeautifulSoup
import json
import os
import psycopg2
from configparser import ConfigParser

class Article:
    def __init__(self,title,shortContent,content,image):
        self.title = title
        self.shortContent = shortContent
        self.content = content
        self.image = image

    def saveToJson(self):
        data = {'title': self.title, 'shortContent': self.shortContent, 'content': self.content, 'image': self.image}
        fileName = 'data.json'
        if os.path.exists(fileName):
            with open(fileName,'r') as file:
                loadJson = json.load(file)
                loadJson.append(data)

            with open(fileName,'w') as file:
                json.dump(loadJson,file)
        else:
            with open(fileName, 'w') as file:
                json.dump([data],file)

    def save(self):
        parser = ConfigParser()
        parser.read('database.ini')
        section = 'postgresql'
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        connectToDB = psycopg2.connect(**db)
        cursor = connectToDB.cursor()
        insert_data = """ INSERT INTO data (title, shortcontent, content, image) VALUES (%s,%s,%s,%s)"""
        record_to_insert = (self.title, self.shortContent, self.content, self.image)
        cursor.execute(insert_data,record_to_insert)
        connectToDB.commit()
        cursor.close()
        connectToDB.close()
        print(cursor)

    def view(self, title = ''):
        parser = ConfigParser()
        parser.read('database.ini')
        section = 'postgresql'
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        connectToDB = psycopg2.connect(**db)
        cursor = connectToDB.cursor()
        if title:
            query = 'select title from data'
        else:
            query = 'select * from data'
        cursor.execute(query)
        fetchDatas = cursor.fetchall()
        print(fetchDatas)

class Scraper:
    def __init__(self,url):
        self.url = url

    def getBody(self):
        body = requests.get(self.url)
        parse = BeautifulSoup(body.content,'html.parser')
        return parse

scraper = Scraper('https://aliayubi.com/blog/')
body = scraper.getBody()

articles = body.find_all(class_="et_pb_post")

def getJustCurrentElText(parent):
    return ''.join(parent.find_all(text=True, recursive=False)).strip()

for content in articles:
    title = content.find(class_="entry-title").text
    shortContent = getJustCurrentElText(content)

    articleLink = content.find(class_="entry-title").find('a')['href']
    articleBody = Scraper(articleLink).getBody()
    content = articleBody.find(class_='entry-content').text
    image = articleBody.find('article').find('img')['data-src']
    article = Article(title, shortContent,content,image)
    # article.save()
    article.view(title)