import os
import random
import string
import atexit
import pandas as pd

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

class GetProductSpider(CrawlSpider):
    name = "getProduct"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    ajax_url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php"

    rules = (
        Rule(LinkExtractor(allow=('5974')), callback='parse_item', follow=True),
    )

    def __init__(self, **kwargs):
        self.df = pd.DataFrame(columns=['name', 'price', 'description', 'characteristics'])
        atexit.register(self.close_parse)
        super(GetProductSpider, self).__init__(**kwargs)

    def parse_item(self, response):
        product_links = response.xpath('//a[@itemprop="url"]/@href').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_product_details)

    def parse_product_details(self, response):
        name = response.xpath('//div[@class="block-1"]/div[@class="block-1-0"]/h1[@itemprop="name"]/text()').get()
        price = response.xpath('//div[@class="block-3-row element-current-price"]//span/text()').getall() or "Нет в наличии"
        description = response.xpath('//div[@id="block-description"]//text()').getall()
        cleaned_description = ' '.join(desc.strip() for desc in description if desc.strip())

        items = response.url.split('/')[-1]
        
        yield Request(
            url=self.ajax_url,
            method='POST',
            body=f'type=character&style=element&items={items}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            callback=self.add_characteristic,
            meta={
                'name': name,
                'price': price,
                'description': cleaned_description
            }
        )

    def add_characteristic(self, response):
        if response.status == 200:
            characteristics = {}
            for characteristic_row in response.xpath('//table//tr'):
                key = characteristic_row.xpath('.//td[@class="table-character-text"]/text()').get()
                value = characteristic_row.xpath('.//td[@class="table-character-value"]/text()').get()
                if key and value:
                    characteristics[key.strip()] = value.strip()

            self.df = self.df._append({'name': response.meta['name'], 'price': response.meta['price'],
                                      'description': response.meta['description'], 'characteristics': characteristics},
                                     ignore_index=True)
        else:
            self.logger.error(f"Ошибка при выполнении запроса: {response.status}")

    def close_parse(self):
        random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)) + ".csv"
        os.makedirs('data', exist_ok=True)
        self.df.to_csv(os.path.join('data', random_filename), index=False)
        self.logger.info(f"Имя файла с данными: {random_filename}")
