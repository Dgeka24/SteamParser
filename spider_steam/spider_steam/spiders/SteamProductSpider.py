import scrapy
import re
from lxml import etree
from bs4 import BeautifulSoup
# from spider_steam.items import SpiderSteamItem
from spider_steam.items import SpiderSteamItem
from urllib.parse import urlencode

queries = ['indie', 'strategy', 'survival']

class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/search']


    def start_requests(self):
        for query in queries:
            for page in range(10):
                query_url = 'https://store.steampowered.com/search?term=' + query + "&page=" + str(page)
                yield scrapy.Request(url=query_url, callback=self.parse_search)

    def parse_search(self, response):
        all_blocks = response.xpath('//*[@id="search_resultsRows"]/a')
        for block in response.xpath('//*[@id="search_resultsRows"]/a'):
            link = block.xpath('@href').extract()[0]
            price_1 = ''.join(block.xpath('.//div[contains(@class, "search_price")]//text()').extract()).strip()
            price_1 = re.sub('[\n\r\t]', '', price_1)
            if 'app' in link:
                yield scrapy.Request(url=link, cookies={'birthtime': '470682001', 'lastagecheckage': '1-0-1985'}, callback=self.parse, meta={'price' : price_1})
        """
        all_links = response.xpath('//a[contains(@class, "search_result_row")]/@href').extract()
        for link in all_links:
            if 'app' in link:
                yield scrapy.Request(url=link, cookies={'birthtime':'470682001', 'lastagecheckage':'1-0-1985'}, callback=self.parse)
        """

    def parse(self, response):
        item = SpiderSteamItem()
        name = response.xpath('//div[@class="apphub_AppName" and @id="appHubAppName"]/text()').extract()
        categories = response.xpath('//div[@class="blockbg"]//text()').extract()
        categories = [x.strip() for x in categories]
        reviews_mark = ''.join(response.xpath('//*[@id="userReviews"]/div[2]/div[2]/span[1]/text()').extract())
        reviews_overall = ''.join(response.xpath('//*[@id="userReviews"]/div[2]/div[2]/span[3]/text()').extract())
        reviews_overall = re.sub('[\n\r\t]', '', reviews_overall)
        release_date = response.xpath('//*[@id="game_highlights"]/div[1]/div/div[3]/div[2]/div[2]//text()').extract()
        developers = response.xpath('//*[@id="developers_list"]/a//text()').extract()
        tags = response.xpath('//*[@id="glanceCtnResponsiveRight"]/div[2]/div[2]//text()').extract()
        tags = [x for x in tags if x != '+']
        tags = '; '.join(tags).strip().strip('; ')
        tags = re.sub('[\n\r\t]', '', tags)
        platforms = response.xpath('//div[@class="game_area_purchase_platform"]/span/@class').extract()
        platforms = set(platforms)

        #platforms = response.xpath('//*[@id="game_area_purchase_section_add_to_cart_59321"]/div[1]/@class').extract()
        item['name'] = ''.join(name).strip()
        item['category'] = ''.join(categories).strip()
        item['reviews'] = (reviews_mark + reviews_overall).strip()
        item['release_date'] = ''.join(release_date).strip()
        item['developer'] = '; '.join(developers).strip()
        item['tags'] = tags
        item['price'] = response.meta.get('price')
        item['platforms'] = ' '.join(platforms).replace('platform_img', '').strip()
        yield item




