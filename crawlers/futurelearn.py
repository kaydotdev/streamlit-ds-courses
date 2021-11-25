import glob
import scrapy


class FutureLearn(scrapy.Spider):
    name = 'future_learn'
    allowed_domains = ['www.futurelearn.com']

    def start_requests(self):
        file_names = [path.replace("static_pages/", "")
                      for path in glob.glob('static_pages/*.html')]

        self.logger.info(file_names)

        for file in file_names:
            yield scrapy.Request(f'static_pages/{file}', callback=self.parse)

    def parse(self, response, **kwargs):
        for node in response.css('.cardGrid-isCompact_jSNJZ .Container-wrapper_1lZbP'):
            yield scrapy.Request(f"https://www.futurelearn.com{node.css('a.index-module_anchor__24Vxj::attr(href)').get()}",
                                 callback=self.parse_page,
                                 cb_kwargs={"author": node.css('span.itemTitle-wrapper_2C5P7::text').get()})

    def parse_page(self, response, **kwargs):
        author = kwargs.get("author", None)

        yield {
            'title': response.css('h1.heading-module_wrapper__2dcxt::text').get(),
            'description': response.css('.text-module_mBreakpointSizemedium__1_OnK::text').get(),
            'authors': [author] if author is not None else None,
            'rating': response.css('div.ReviewStars-text_mSEFD::text').get(),
            'votes_count': response.css('div.ReviewStars-text_mSEFD span').get(),
            "students_count": response.css('#sticky-banner-start > div:nth-child(2) > p:nth-child(1) > '
                                           'strong:nth-child(1)::text').get(),
            "level": "Mixed",
            "duration": f"{response.css('li.keyInfo-module_item__2GNi_:nth-child(1) > div:nth-child(2) > span:nth-child(2)::text').get()};{response.css('li.keyInfo-module_item__2GNi_:nth-child(3) > div:nth-child(2) > span:nth-child(2)::text').get()}",
            "platform": "FutureLearn",
            "free": True
        }
