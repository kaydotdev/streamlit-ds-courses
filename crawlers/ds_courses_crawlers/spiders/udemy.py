import scrapy
from scrapy_splash import SplashRequest


LUA_INFINITE_NAVIGATION_SCROLL_SCRIPT = """
    function main(splash)
        splash:set_user_agent(splash.args.ua)
        assert(splash:go(splash.args.url))

        local scroll_to = splash:jsfunc("window.scrollTo")
        local get_body_height = splash:jsfunc(
            "function() {return document.body.scrollHeight;}"
        )

        assert(splash:wait(1.0))
        scroll_to(0, get_body_height())

        while not splash:select('.course-list--container--3zXPS') do
            splash:wait(0.1)
        end

        return {
            html=splash:html()
        }
    end
"""

LUA_PAGE_SCROLL_SCRIPT = """
    function main(splash)
        splash:set_user_agent(splash.args.ua)
        assert(splash:go(splash.args.url))

        local scroll_to = splash:jsfunc("window.scrollTo")
        local get_body_height = splash:jsfunc(
            "function() {return document.body.scrollHeight;}"
        )

        assert(splash:wait(1.0))
        scroll_to(0, get_body_height())

        while not splash:select('div.what-you-will-learn--what-will-you-learn--mnJ5T') do
            splash:wait(0.1)
        end

        return {
            html=splash:html()
        }
    end
"""

class UdemySpider(scrapy.Spider):
    name = "udemy"
    allowed_domains = ["www.udemy.com"]
    start_urls = ["https://www.udemy.com"]

    def start_requests(self):
        yield SplashRequest(
            args={ 'lua_source': LUA_INFINITE_NAVIGATION_SCROLL_SCRIPT },
            endpoint='execute',
            url='https://www.udemy.com/courses/development/data-science/',
            callback=self.parse
        )

    def parse(self, response):
        self.logger.info('[scrapy.SplashSpider] ' + response.url)

        for course in response.css('.course-list--container--3zXPS .popper--popper--2r2To'):
            cb_kwargs = {
                'level': course.css("div.course-card--course-meta-info--2jTzN > span:nth-child(3)::text").get(),
                'duration': course.css("div.course-card--course-meta-info--2jTzN > span:nth-child(1)::text").get(),
                'free': course.css("div[data-purpose=course-price-text] > span:nth-child(2)::text").get() == "Free"
            }

            self.logger.info('[scrapy.SplashSpider] Posted request https://www.udemy.com' + course.css("a::attr(href)").get())

            yield SplashRequest(
                args={
                    'lua_source': LUA_PAGE_SCROLL_SCRIPT
                },
                endpoint='execute',
                url=f'https://www.udemy.com{course.css("a::attr(href)").get()}',
                callback=self.parse_page,
                cb_kwargs=cb_kwargs
            )

        next_page_is_disabled = response.css("a.pagination--next--164ol::attr(aria-disabled)") == "false"

        if not next_page_is_disabled:
            next_page_url = response.css("a.pagination--next--164ol::attr(href)").get()

            yield SplashRequest(
                args={ 'lua_source': LUA_INFINITE_NAVIGATION_SCROLL_SCRIPT },
                endpoint='execute',
                url=f'https://www.udemy.com{str(next_page_url)}',
                callback=self.parse
            )

    def parse_page(self, response, **kwargs):
        self.logger.info('[scrapy.SplashSpider] ' + response.url)

        yield {
            'title': response.css("h1.udlite-heading-xl::text").get(),
            'description': response.css("div[data-purpose=lead-headline]::text").get(),
            'authors': response.css("a.udlite-instructor-links span::text").getall(),
            'rating': response.css("span[data-purpose=rating-number]::text").get(),
            'votes_count': response.css(".styles--rating-wrapper--5a0Tr > span:nth-child(2)::text").get(),
            'students_count': response.css(".clp-lead__element-item--row > div:nth-child(2) > "
                                            "div:nth-child(1)::text").get(),
            'level': kwargs['level'],
            'duration': kwargs['duration'],
            'platform': 'Udemy',
            'free': kwargs['free']
        }

