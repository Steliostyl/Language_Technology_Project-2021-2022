import scrapy
from html_text import extract_text
from datetime import datetime

def readDateTimeFromString(datetimeString):
    return datetime.fromisoformat(datetimeString[:-2] + ":" + datetimeString[len(datetimeString)-2:])

class CnbcSpider(scrapy.Spider):
    name = 'cnbc_spider'
    start_urls = [
        'https://www.cnbc.com/world',
        'https://www.cnbc.com/business',
        'https://www.cnbc.com/technology',
        'https://www.cnbc.com/politics'
    ]

    def parse(self, response):
        # Get article URLs
        for link in response.xpath('//div[@class="Card-titleContainer"]/a/@href'):
            yield response.follow(link.get(), callback=self.parse_article)
    
    def parse_article(self, response):
        # Extract article paragraphs
        par = response.xpath('//div[@class="ArticleBody-articleBody"]/div[@class="group"]/p').extract()
        # Ignore articles with empty paragraphs
        if par == []:
            return
        paragraphs = ''
        # Extract only the text of the paragraphs and add it to paragraphs string
        for paragraph in par:
            paragraphs += ' ' + extract_text(paragraph)

        # Create article dictionary by extracting required information
        article = { 
            'url': response.url,
            'title': response.xpath('//h1/text()').extract_first(),
            'paragraphs': paragraphs
        }

        return article


class CnnSpider(scrapy.Spider):
    name = 'cnn_spider'
    start_urls = ['https://edition.cnn.com/']
    allowed_domains = ['cnn.com']

    def parse(self, response):
        # Get the top level article categories from footer (World, Politics etc.)
        categories = response.xpath('//footer//nav/ul[@type="expanded"]/li/a/@href')
        for category in categories:
            # Ignore categories more and videos (continue to next loop iteration)
            if category.get() == '/more' or category.get() == '/videos':
                continue
            yield response.follow(category.get(), callback=self.parse_category)
    
    def parse_category(self, response):
        # Get the section containers
        containers = response.xpath('//section/div[starts-with(@class, "l-container")]')
        for container in containers:
            # Get section title (Around the world, Latest Headlines, Editor's Pick etc.)
            section = container.xpath('./div[@class="zn-header"]/h2[@class="zn-header__text"]/text()').extract_first()

            # Ignore empty and paid sections (ads)
            if section == None:
                continue
            section = section.lower()
            if "partner content" in section:
                continue
            
            # Get article URLs from filtered sections
            for link in container.xpath('//*[starts-with(@class, "column zn__column")]//@href'):
                # Ignore links to videos and gallery style articles
                if 'video' in link.get() or 'gallery' in link.get():
                    continue
                yield response.follow(link.get(), callback=self.parse_article, meta={'section': section})


    def parse_article(self, response):
        # Extract article paragraphs
        par = response.xpath('//*[starts-with(@class, "zn-body__paragraph")]/text()').extract()
        if par == []:
            return
        paragraphs = ''
        for paragraph in par:
            paragraphs += ' ' + extract_text(paragraph)

        # Create article dictionary by extracting required information
        article = { 
            'url': response.url,
            'title': response.xpath('//h1/text()').extract_first(),
            'paragraphs': paragraphs
        }

        return article