from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.item import Item, Field
from orderP.items import Product

class GetProductSpider(CrawlSpider):
    name = "getProduct"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    ajax_url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php"
    
    rules = (
        Rule(LinkExtractor(allow=('5974','9460','5999')), callback='parse_item', follow=True),
    )


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
            item = Product()
            for characteristic_row in response.xpath('//table//tr'):
                key = characteristic_row.xpath('.//td[@class="table-character-text"]/text()').get()
                value = characteristic_row.xpath('.//td[@class="table-character-value"]/text()').get()
                if key and value:
                    characteristics[key.strip()] = value.strip()

            item['name'] = response.meta['name']
            item['price'] = response.meta['price']
            item['description'] = response.meta['description']
            item['characteristics'] = characteristics
            yield item
            
        else:
            self.logger.error(f"Ошибка при выполнении запроса: {response.status}")


