# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem

from matching_algorithm import GetMatchPercentage

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class PetharborPipeline(object):
    """
    Pipeline module to filter out only relevent
    matches of the lost pet.
    """
    def open_spider(self, spider):
        """
        Set some objects as soon as the
        spider opens.
        """
        self.lost_pet = spider.lost_pet
        self.gmp = GetMatchPercentage(self.lost_pet)

    def process_item(self, item, spider):
        """
        Process each item, comute the matching score
        with the lost pet details and drop that item
        if the score is lower than the threshold.
        """
        score = self.gmp.get_match_percent(item)
        if score >= spider.matching_score_threshold:
            item['score'] = score
            return item
        else:
            raise DropItem("Score={}".format(score))
