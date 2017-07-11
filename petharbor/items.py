# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PetharborItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    gender = scrapy.Field()
    main_color = scrapy.Field()
    breed = scrapy.Field()
    age = scrapy.Field()
    brought_to_shelter = scrapy.Field()
    located_at = scrapy.Field()
    detail_link = scrapy.Field()
    pet_image = scrapy.Field()
    animal_type = scrapy.Field()
