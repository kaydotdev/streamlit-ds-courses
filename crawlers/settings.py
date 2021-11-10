BOT_NAME = 'scrapcourses'

LOG_LEVEL = 'DEBUG'
SPIDER_MODULES = ['scrapcourses.spiders']
NEWSPIDER_MODULE = 'scrapcourses.spiders'

USER_AGENT = 'scrapcourses'
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1.0
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

SPLASH_URL = 'http://0.0.0.0:8050'


SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}


DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

