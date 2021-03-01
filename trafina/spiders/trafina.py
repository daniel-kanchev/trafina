import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from trafina.items import Article


class TrafinaSpider(scrapy.Spider):
    name = 'trafina'
    start_urls = ['https://www.trafina.ch/de/']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-item"]')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('.//h4/text()').get()
            if date:
                date = date.strip()
            else:
                date = ''

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()
        else:
            return

        content = response.xpath('//div[@class="column-content image-content f-cols-2 f-order-2"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
