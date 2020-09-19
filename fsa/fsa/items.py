# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class FsaItem(scrapy.Item):
    # define the fields for your item here like:
    id = Field()
    nameStatus = Field()
    regNumber = Field()
    applicantInn = Field()
    applicantFullName = Field()
    nameType = Field()
    fullName = Field()
    address = Field()
    # НЧЕР
    nameTypeActivity = Field()
    oaDescription = Field()
    one = Field()
    two = Field()
    extend = Field()
    pass
