# -*- coding: utf-8 -*-
import sys
import locale
import codecs
import scrapy
from scrapy.http.request import Request

from petharbor.items import PetharborItem


class PetHarborSpider(scrapy.Spider):
    """
    Scraper to scrape the pet listings for
    a given lost pet description.
    """
    name = "pharbor"
    allowed_domains = ["petharbor.com"]
    miles_values = ['10', '20', '50', '100', '200']
    num_rows = 100

    def __init__(self):
        sys.stdout = codecs.getwriter(
            locale.getpreferredencoding())(sys.stdout)
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.zipcode = '60613'
        self.atype = 'cat'
        self.where = "type_" + self.atype.upper()
        self.miles = self.miles_values[0]

    def start_requests(self):
        # construct the results url from zipcode and search radius
        url = self.get_shelter_search_url()
        yield Request(url, self.parse)

    def parse(self, response):
        """
        Parse the content.
        """
        # Find the Lost and Found Pets title element
        title = response.xpath(
            "//p[@class='shelterListTitle'][contains("
            "text(), 'Adoptable, Lost and Found Pets')]"
        )
        # Get the list of result rows
        shelter_rows = title.xpath(
            "following-sibling::div[@class='resultsContainer']")[0].xpath(
            "./table[@class='searchResultRow']"
        )
        print("Miles = {}".format(self.miles))
        if len(shelter_rows) < 2:
            # Expand the search
            current_index = self.miles_values.index(self.miles)
            print("Less than 2 results for miles={}".format(self.miles))
            try:
                self.miles = self.miles_values[current_index + 1]
            except:
                # All search radius values exhausted
                print("All search radius values exhausted")
                return
            search_url = self.get_shelter_search_url()
            yield scrapy.Request(
                search_url, self.parse,
                dont_filter=True
            )
        else:
            print("Found {} shelters".format(len(shelter_rows)))
            self.shelter_list = ""
            for shelter in shelter_rows:
                shelter_name = shelter.xpath(
                    ".//input[@type='CHECKBOX']/@name").extract_first()
                if shelter_name.startswith("chk"):
                    shelter_name = shelter_name.replace("chk", "")
                if self.shelter_list:
                    self.shelter_list += ','
                self.shelter_list += "%27" + shelter_name + "%27"
                # %27AWLI%27,%27CHGO%27
            print("shelter_list={}".format(self.shelter_list))

            # Get results url
            results_url = self.get_results_url()
            yield scrapy.Request(
                results_url, self.parse_results,
                dont_filter=True
            )

    def parse_results(self, response):
        """
        Parse the results.
        """
        results = response.xpath(
            "//table[@class='ResultsTable'][@align='center']"
            "[@border='0']//tr"
        )
        print("Num results = {}".format(len(results)))
        for count, result in enumerate(results):
            if not count:
                # get the order of the data columns
                continue
            tds = result.xpath("./td")
            # detail link of the pet
            detail_link = tds[0].xpath('./a/@href').extract_first()
            # join the relative detail link with base url
            detail_link = response.urljoin(detail_link)

            item = PetharborItem()
            item["name"] = tds[1].xpath("./text()").extract_first()
            item["gender"] = tds[2].xpath("./text()").extract_first()
            item["main_color"] = tds[3].xpath("./text()").extract_first()
            item["breed"] = tds[4].xpath("./text()").extract_first()
            item["age"] = tds[5].xpath("./text()").extract_first()
            item["brought_to_shelter"] = tds[6].xpath(
                "./text()").extract_first()
            item["located_at"] = tds[7].xpath("./text()").extract_first()
            item["animal_type"] = self.atype
            yield scrapy.Request(
                detail_link, self.parse_detail_link,
                dont_filter=True, meta={'item': item}
            )

        # parse the next page
        next_page = response.xpath(
            "//a[contains(text(), 'Next Page')]/@href"
        ).extract_first()
        # parse if next page link is present
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(
                next_page, self.parse_results,
                dont_filter=True
            )

    def parse_detail_link(self, response):
        """
        Parse the detail page of the pet
        """
        item = response.meta['item']
        # Parse the short link to the detail page
        detail_link = response.xpath(
            "//a[@target='_new'][contains(text(), 'here')]/@href"
        ).extract_first()
        # assign the detail link to item
        item['detail_link'] = response.urljoin(detail_link)

        # parse the link to the pet image
        pet_image = response.xpath(
            "//table[@class='DetailTable'][@align='top']//img/@src"
        ).extract_first()
        item['pet_image'] = response.urljoin(pet_image)

        yield item

    def get_shelter_search_url(self):
        """
        Prepare and return the shelter search url
        """
        return (
            'http://petharbor.com/pick_shelter.asp?frontdoor=1&'
            'ZIP={}&searchtype=PRE&MILES={}&stylesheet=include/default.css'
        ).format(self.zipcode, self.miles)

    def get_results_url(self):
        """
        Get the url that displays the search results.
        100 results in a page.
        """
        return (
            "http://petharbor.com/results.asp?searchtype=LOST&stylesheet="
            "include/default.css&frontdoor=1&friends=1&samaritans=1&"
            "nosuccess=0"
            "&rows={}&imght=120&imgres=thumb&tWidth=200&view=sysadm.v_animal&"
            "fontface=arial&fontsize=10&zip={}&miles={}&shelterlist={}&"
            "atype={}&ADDR=undefined&grid=0&nav=1&start=4&nomax=1&page=1&"
            "where={}"
        ).format(
            self.num_rows, self.zipcode, self.miles,
            self.shelter_list, self.atype, self.where
        )
