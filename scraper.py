# import dependencies
import requests
from bs4 import BeautifulSoup
import json
import os
import psycopg2
from configparser import ConfigParser

# Article object for saving and viewing articles
class Article:
    def __init__(self,title,shortContent,content,image):
        self.title = title
        self.shortContent = shortContent
        self.content = content
        self.image = image

    #save article as JSON file
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

    # Save article to DB
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

    # Getting article data from DB
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

# Scraper class
class Scraper:
    def __init__(self,url):
        self.url = url

    # get body of the scraped url
    def getBody(self):
        body = requests.get(self.url)
        parse = BeautifulSoup(body.content,'html.parser')
        return parse

# Let's start the scraper 
url = 'https://aliayubi.com/blog/' # Url that we want to scrape
scrape = Scraper(url)
body = scrape.getBody()

articles = body.find_all(class_="et_pb_post") # Select the contents div that you want to scrape

# Function to get the first & only text inside a nested element
def getJustCurrentElText(parent):
    return ''.join(parent.find_all(text=True, recursive=False)).strip()

# Loop through contents divs
for article in articles:
    shortContent = getJustCurrentElText(article)
    title = article.find(class_="entry-title").text
    
    articleLink = content.find(class_="entry-title").find('a')['href']
    articleBody = Scraper(articleLink).getBody()
    content = articleBody.find(class_='entry-content').text
    image = articleBody.find('article').find('img')['data-src']
    article = Article(title, shortContent,content,image)
    # article.save()
    article.view(title)