# -*- coding: utf-8 -*-

import json
import scrapy
import ast

from GithubCrawler.items import UserItem

'''
this spider will request the repository information with the keywords
and then extract the contributors on the repository. depending on github rules,
it will only provide up to 500 non-anonymouse contributors for each repo.
request the user details of those contributors and save to db.

api:
GET /search/repositories
q		query keywords
sort	stars, forks, or updated. Default: results are sorted by best match.
order	asc or desc. Default: desc
'''


# values to get from settings
# ==================================================
SPIDER_NAME = None
ACCESS_TOKEN = None

paramKeys = None
maxRepoPages = 0
perPageRepo = 0
perPageContributors = 0
maxPagesContributors = 0

# get settings
# execfile("config.py")
exec(open("config.py").read())
# ==================================================
logPath = 'log.dat'


class RepositorySpider(scrapy.Spider):
    name = SPIDER_NAME
    allowed_domains = ["api.github.com"]

    # spider status default
    spiderStatus = {
        "currentKeyIndex": 0,
        "repoPagesPassed": 0,
        "sort": "stars"
    }
    current_key = None

    baseUrl = "https://api.github.com/search/repositories?q=%s&per_page=%s&page=%s%s"
    access_token = "bearer %s" % ACCESS_TOKEN
    headers = {'Authorization': access_token}

    def start_requests(self):
        self.read_log()

        # skip if all keys have been iterated
        # if self.spiderStatus["currentKeyIndex"] < 0:
        #    return

        # keyword as query param q
        self.current_key = paramKeys[self.spiderStatus["currentKeyIndex"]]
        keyword = self.current_key['kw']

        page = self.spiderStatus["repoPagesPassed"] + 1
        print ('###### current keyword: %s, current page of repo: %d' % (keyword, page))

        # 1 request to get 1 page of 5 repos each run
        url_params = (keyword, perPageRepo, page,
                     "&sort=stars" if self.spiderStatus["sort"] == "stars" else "")
        yield scrapy.Request(url=self.baseUrl % url_params,
                             headers=self.headers,
                             callback=self.parse_repos)

        # the log writing will not wait for the requests to end
        # since scrapy schedules a requests queue
        self.write_log(self.spiderStatus["currentKeyIndex"],
                       page, self.spiderStatus["sort"])
        pass

    def parse_repos(self, response):
        # parse 1 page of perPageRepo repos

        repos = json.loads(response.body)["items"]

        # this plays a same role as start_request and parse data in a deeper level in its callback
        # number of requests here is up to perPageRepo repos
        for repo in repos:
            contributors_url = repo["contributors_url"]

            # paging for contributors
            # number of requests here might be up to
            # maxPagesContributors (pages of contributors, *WITH* person info)
            for page in range(1, maxPagesContributors + 1):
                url = (contributors_url + "?per_page=%d&page=%d") % (perPageContributors, page)
                yield scrapy.Request(url=url, headers=self.headers,
                                     callback=self.parse_contributors)

        pass

    def parse_contributors(self, response):
        # one request for up to perPageContributors contributors

        try:
            contributors = json.loads(response.body)

            # contributors = ast.literal_eval(response.body)
            if len(contributors) == 0:
                return

            # up to perPageContributors contributors
            # total contributors drilling down: totalContributors = perPageContributors * maxPagesContributors * perPageRepo
            # total requests drilling down here: 2 * totalContributors
            for contributor in contributors:
                user_url = contributor["url"]
                # user_url = "https://api.github.com/users/gabrielschulhof" #for test
                yield scrapy.Request(url=user_url, headers=self.headers,
                                     callback=self.parse_user_info)
        except:
            filename = 'error.txt'
            with open(filename, 'ab') as f:
                f.write(response.request.url)
                f.write('\r\n parse_contributors')
                f.write('\r\n--------------------------------------------\r\n')

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
        item['email'] = RepositorySpider.unicode_value_escape(user['email'])
        item['pubRepos'] = user['public_repos']
        item['followers'] = user['followers']

        item['avatarUrl'] = user['avatar_url'].encode('raw_unicode_escape')
        item['apiUrl'] = user['url'].encode('raw_unicode_escape')
        blog = item['blog'] = RepositorySpider.unicode_value_escape(user['blog'])
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

        repo_url = user['repos_url']  # 'https://api.github.com/users/mgaitan/repos'
        yield scrapy.Request(url=repo_url, headers=self.headers,
                             callback=self.parse_skills(item))

        pass

    def parse_skills(self, user):
        def f(response):
            user_repos = json.loads(response.body)
            # print (user_repos)

            skills = reduce(RepositorySpider.process_repo_skills, user_repos, [])
            # append skills as keywords specified
            if 'sk' in self.current_key:
                sk_specified = self.current_key['sk']
                map(lambda sk: skills.append(sk) if skills.count(sk) == 0 else None, sk_specified)

            # escape the double-quote in the result string
            user["skills"] = str(skills).replace('"', '%22')
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
        # s.match(re).map(k=> {s = s.replace(k, String.fromCodePoint(k.replace("\\U", "0x")))});

        # # replace('"', '%22') to escape the double-quote for the api to handle the string as json
        # and also use unescape to restore the " in js, together with above call
        # '''

        return value.encode('raw_unicode_escape').encode('string_escape') \
            .replace('\\x', '%').replace('\\\\u', '%u').replace('"', '%22')
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
            # give default value when exception occurs
            self.spiderStatus = {
                "currentKeyIndex": 0,
                "repoPagesPassed": 0,
                "sort": "stars"
            }
        finally:
            if log:
                log.close()
                log = None

        pass

    def write_log(self, key_index, repo_page, sort):
        if repo_page >= maxRepoPages:
            key_index += 1
            repo_page = 0

        if key_index >= len(paramKeys):
            # indicate that all keys have been searched
            # re-iterate from first key
            key_index = 0

            # each iteration of all keys will toggle the sort of search
            sort = "stars" if sort == "" else ""

        with open(logPath, 'wb') as log:
            status = {
                "currentKeyIndex": key_index,
                "repoPagesPassed": repo_page,
                "sort": sort
            }
            log.write(str(status))

        pass


    pass