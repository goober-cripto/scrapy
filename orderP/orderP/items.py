# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
import scrapy

class Product(scrapy.Item):

    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    characteristics = scrapy.Field()


