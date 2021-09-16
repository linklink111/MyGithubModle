# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GithubcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class UserItem(scrapy.Item):
    login = scrapy.Field()
    githubId = scrapy.Field()
    apiUrl = scrapy.Field()
    htmlUrl = scrapy.Field()
    avatarUrl = scrapy.Field()
    name = scrapy.Field()
    company = scrapy.Field()
    blog = scrapy.Field()
    location = scrapy.Field()
    email = scrapy.Field()
    bio = scrapy.Field()
    pubRepos = scrapy.Field()
    followers = scrapy.Field()
    # a redundant url when blog is linkedIn
    linkedInUrl = scrapy.Field()
    # skills are retrieved as the language of repos that the user owns
    # and stored as string separated by comma
    skills = scrapy.Field()


# class RepoOwner(scrapy.Item):
#     id = scrapy.Field()
#     apiUrl = scrapy.Field()
#     htmlUrl = scrapy.Field()
#
#
# class RepositoryItem(scrapy.Item):
#     id = scrapy.Field()
#     nodeId = scrapy.Field()
#     name = scrapy.Field()
#     fullName = scrapy.Field()
#     htmlUrl = scrapy.Field()
#     contributorsUrl = scrapy.Field()
#     devLang = scrapy.Field()
#     stars = scrapy.Field()
#     forks = scrapy.Field()
#     score = scrapy.Field()
#
#     owner = RepoOwner()
#
#     # currently a bug from github: number of watchers always follows the number of stars
#     watchers = scrapy.Field()