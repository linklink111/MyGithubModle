import json
import scrapy
import ast

from items import UserItem

SPIDER_NAME = None # 初始化为 None， 后续从配置文件获取
ACCESS_TOKEN = None #

paramKeys = None #
maxRepoPages = 0
perPageRepo = 0
perPageContributors = 0
maxPagesContributors = 0

execfile("config.py") # 获取配置

@staticmethod
def unicode_value_escape(value):
    return value.encode('raw_unicode_escape').encode('string_escape')\
        .replace('\\x', '%').replace('\\\\u','%u').replace('"','%22')
    pass

@staticmethod
def process_repo_skills(skills, repo):
    if repo['language'] is not None:
        if skills.count(repo['language']) == 0:
            skills.append(RepositorySpider.unicode_value_escape(repo['language']))
    return skills

def read_log(self):
    log = None
    try:
        log = open(logPath,'rb')
        data = log.read()
        print("##### daata in log", data)
    except:
        self.spiderStatus = {
            "currentKeyIndex" : 0,
            "repoPagesPassed" : 0,
            "sort" : "stars"
        }
    finally:
        if log:
            log.close()
            log = None
    pass

