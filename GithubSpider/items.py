# 爬取对象的接收模具

import scrapy

class GithubcrawlerItem(scrapy.Item):
    # 这是一个模板
    pass

# 先爬用户
class UserItem(scrapy.Item):
    login = scrapy.Field()
    githubId = scrapy.Field()
    apiUrl = scrapy.Field()
    htmlUrl = scrapy.Field()
    name = scrapy.Field()
    company = scrapy.Field()
    blog = scrapy.Field()
    location = scrapy.Field()
    email = scrapy.Field()
    bio = scrapy.Field()
    pubRepo = scrapy.Field()
    followers = scrapy.Field()
    linkedInUrl = scrapy.Field()  # 如果用户有 blog 的话
    skills = scrapy.Field() # 用户所有仓库覆盖的 语言

