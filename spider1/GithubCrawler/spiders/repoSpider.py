# -*- coding: utf-8 -*-

import json
import scrapy
import ast

from GithubCrawler.items import UserItem

'''
this spider will request the user information with the keywords of SKILLS
and depending on github data, it probably will not get the information relating
with the repositories and the user, such as the user's contribution rate to a repo, etc.

api: GET /search/users
q		query keywords
sort	stars, forks, or updated. Default: results are sorted by best match.
order	asc or desc. Default: desc

'''

keywords = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g',
    'h', 'i', 'j', 'k', 'l', 'm', 'n',
    'o', 'p', 'q', 'r', 's', 't', 'u',
    'v', 'w', 'x', 'y', 'z'
]

logPath = 'log.dat'


# define the variables for string conversion to object (eval)
# false = False
# true = True
# null = None


class RepositorySpider(scrapy.Spider):
    name = "GithubRepoSpider"
    allowed_domains = ["api.github.com"]

    # limitation of the number of results returned from github
    maxRepoPages = 20  # indicate how many pages of repos to search by the current keyword
    perPageRepo = 50  # indicate how many repos per page (per run)
    perPageContributors = 100  # up to 100 result per page
    maxPagesContributors = 5  # up to 5 with person info as per github api

    # spider status default
    spiderStatus = {
        "currentKeyword": 0,
        "repoPagesPassed": 0
    }
    currentKeyword = ''

    baseUrl = "https://api.github.com/search/repositories?q=%s&sort=stars&per_page=%s&page=%s"
    access_token = "bearer 6d5f97e0df17e6faa87abbdaeb77fcb835ffa955"

    headers = {'Authorization': access_token}

    def start_requests(self):
        self.read_log()

        if self.spiderStatus["currentKeyword"] < 0:
            return

        # keyword = keywords[self.spiderStatus["currentKeyword"]]
        page = self.spiderStatus["repoPagesPassed"] + 1
        print ('###### current keyword: %s, current page of repo: %d' % (self.currentKeyword, page))

        # 1 request to get 1 page of 5 repos each run
        yield scrapy.Request(url=self.baseUrl % (self.currentKeyword, self.perPageRepo, page),
                             headers=self.headers,
                             callback=self.parse_repos)

        self.write_log(self.spiderStatus["currentKeyword"], page)
        pass

    def parse_repos(self, response):
        # parse 1 page of perPageRepo repos

        repos = json.loads(response.body)["items"]

        # this plays a same role as start_request and parse data in a deeper level in its callback
        # number of requests here is up to 5 repos
        for repo in repos:
            contributors_url = repo["contributors_url"]

            # paging for contributors
            # number of requests here might be up to
            # maxPagesContributors (pages of contributors, *WITH* person info)
            for page in range(1, self.maxPagesContributors + 1):
                url = (contributors_url + "?per_page=%d&page=%d") % (self.perPageContributors, page)
                yield scrapy.Request(url=url, headers=self.headers,
                                     callback=self.parse_contributors)

        pass

    def parse_contributors(self, response):
        # one request for up to perPageContributors contributors

        contributors = json.loads(response.body)
        # contributors = ast.literal_eval(response.body)
        if len(contributors) == 0:
            return

        # up to perPageContributors contributors
        # total contributors drilling down: totalContributors = perPageContributors * maxPagesContributors * perPageRepo
        # total requests drilling down here: 2 * totalContributors
        for contributor in contributors:
            user_url = contributor["url"]
            # user_url = "https://api.github.com/users/PW486" #for test
            yield scrapy.Request(url=user_url, headers=self.headers,
                                 callback=self.parse_user_info)

        pass

    def parse_user_info(self, response):
        # user = eval(response.body)
        user = json.loads(response.body)

        # filter the response without email
        if user['email'] is None:
            # print('<<<<<<<email null, login: %s' % user["login"])
            return

        # print json.loads(response.body)
        # print user
        # print response.body

        item = UserItem()

        # fields inevitably with value as per github api
        item["login"] = user["login"].encode('raw_unicode_escape')
        item["githubId"] = user["id"]
        item['htmlUrl'] = user['html_url'].encode('raw_unicode_escape')
        item['email'] = user['email'].encode('raw_unicode_escape')
        item['pubRepos'] = user['public_repos']
        item['followers'] = user['followers']

        item['avatarUrl'] = user['avatar_url'].encode('raw_unicode_escape')
        item['apiUrl'] = user['url'].encode('raw_unicode_escape')
        blog = item['blog'] = user['blog'].encode('raw_unicode_escape')
        if blog.count('www.linkedin.com') > 0:
            item['linkedInUrl'] = blog

        # fields might be without value
        if user['name'] is not None:
            item['name'] = RepositorySpider.unicode_value_escape(user['name'])
        else:
            # name is required field for api, use login when empty
            item['name'] = item["login"]
        if user['company'] is not None:
            item['company'] = RepositorySpider.unicode_value_escape(user['company'])
        if user['location'] is not None:
            item['location'] = RepositorySpider.unicode_value_escape(user['location'])
        if user['bio'] is not None:
            item['bio'] = RepositorySpider.unicode_value_escape(user['bio'])

        repo_url = user['repos_url']  # = 'https://api.github.com/users/mgaitan/repos'
        yield scrapy.Request(url=repo_url, headers=self.headers,
                             callback=self.parse_skills(item))

        pass

    def parse_skills(self, user):
        def f(response):
            user_repos = json.loads(response.body)
            # print (user_repos)

            skills = reduce(RepositorySpider.process_repo_skills, user_repos, [])
            # if skills.count(self.currentKeyword) == 0:
            #     if self.currentKeyword == 'C++':
            #         skills.append(self.currentKeyword)
            #     elif self.currentKeyword == 'C%23':
            #         skills.append("C#")
            #     else:
            #         skills.append(self.currentKeyword.replace('+', ' '))

            user["skills"] = str(skills)
            # print user['skills']

            yield user
            pass

        return f
        pass

    @staticmethod
    def unicode_value_escape(value):
        # '''
        # escape the unicode values in the returned value in order to send request
        # to api. save the value as escaped, and in front-end (js code) use
        # unescape to decode the saved value for display the original string
        # unescape('hao%u597dd%use%e0de').replace('%u', '\\u')  --> "hao好d\useàde"
        # replace('%u', '\\u') for orginal "\\u" string.

        # # below for emoji
        # re = /(\\U[0-9a-fA-F]{8})/g
        # s.match(re).map(k= > {s = s.replace(k, String.fromCodePoint(k.replace("\\U", "0x")))});
        # '''

        return value.encode('raw_unicode_escape').encode('string_escape') \
            .replace('\\x', '%').replace('\\\\u', '%u')
        pass

    @staticmethod
    def process_repo_skills(skills, repo):
        # print repo['language']

        if repo['language'] is not None:
            if skills.count(repo['language']) == 0:
                skills.append(RepositorySpider.unicode_value_escape(repo['language']))

        return skills
        pass

    def read_log(self):
        log = None
        try:
            log = open(logPath, 'rb')
            data = log.read()
            print ("###### data in log", data)

            self.spiderStatus = ast.literal_eval(data)
        except:
            self.spiderStatus = {
                "currentKeyword": 0,
                "repoPagesPassed": 0
            }
        finally:
            if log:
                log.close()
                log = None

        self.currentKeyword = keywords[self.spiderStatus["currentKeyword"]]

        pass

    def write_log(self, keyword, repo_page):
        if repo_page >= self.maxRepoPages:
            keyword += 1
            repo_page = 0

        if keyword >= len(keywords):
            # indicate that all keywords has been searched
            keyword = -1

        with open(logPath, 'wb') as log:
            status = {
                "currentKeyword": keyword,
                "repoPagesPassed": repo_page
            }
            log.write(str(status))

        pass

    pass

# page = response.url.split("/")[-2]
# filename = 'mingyan-%s.html' % page
# with open(filename, 'wb') as f:
# 	f.write(response.body)
# 	self.log('saved file: %s' % filename)
