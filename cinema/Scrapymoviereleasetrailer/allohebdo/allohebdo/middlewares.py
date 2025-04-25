import random

class RandomUserAgentMiddleware:
    """ Injecte un User-Agent aléatoire issu de USER_AGENT_LIST """
    def __init__(self, ua_list):
        self.ua_list = ua_list

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist("USER_AGENT_LIST"))

    def process_request(self, request, spider):
        if self.ua_list:
            request.headers["User-Agent"] = random.choice(self.ua_list)


