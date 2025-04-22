import random
from scrapy import signals

class RotateUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        ua_list = crawler.settings.getlist("USER_AGENT_LIST")
        mw = cls(ua_list)
        crawler.signals.connect(mw.spider_opened, signal=signals.spider_opened)
        return mw

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(self.user_agents)

    def spider_opened(self, spider):
        spider.logger.info(f"RotateUserAgentMiddleware activé ({len(self.user_agents)} UA)")

