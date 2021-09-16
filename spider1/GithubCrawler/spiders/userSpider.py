# -*- coding: utf-8 -*-

import json
import scrapy
import re

from GithubCrawler.items import UserItem

'''
this spider will request the user information with the keywords of SKILLS
and depending on github data, it probably will not get the information relating
with the repositories and the user, such as the user's contribution rate to a repo, etc.

api: GET /search/users
q		query keywords
sort	followers, repositories, or joined. Default: results are sorted by best match.
order	asc or desc. Default: desc
'''

topXSkills = [
	# 'python', 'java', 'c++', 'javascript', 'react', 'algorithm', 'html', 'css', 'redis',
	# 'c#', 'oracle', 'webapi', 'nodejs', 'bash', 'shell', 'php', 'typescript', 'elasticsearch',
	# 'ruby', 'swift', 'assembly', 'go', 'objective-c', 'vb.net', 'matlab', 'vba', 'scala',
	# 'groovy', 'perl', 'angular', '.net+core', 'dotnet', 'spring', 'django', 'cordova', 'tensorflow',
	# 'xamarin', 'spark', 'hadoop', 'mysql', 'sql+server', 'postgresql', 'mongodb', 'sqlite',
	# 'mariadb', 'azure', 'google+cloud', 'amazon', 'db2', 'bigquery', 'hbase', 'wordpress',
	# 'ios', 'nosql', 'apache', 'sharepoint', 'linux', 'andriod', 'artificial+intelligence', 'ai',
	# 'mobile', 'front-end', 'back-end', 'agile', 'block+chain'
	'python', 'java'
]

userSN = {}
logPath = '../log.dat'


class UserSpider(scrapy.Spider):
	name = "GithubUserSpider"
	allowed_domains = ["api.github.com"]

	maxPages = 5
	perPage = 30

	baseUrl = "https://api.github.com/search/users?q=%s&sort=followers&per_page=%s&page=%s"
	# access_token = "bearer 15b78086732e996d63a3ced1804fe9d42ce77c77"
	access_token = "bearer d30ca3ac48f774a7650552101e20963b06110c12"
	headers = {'Authorization': access_token}

	def start_requests(self):
		for skill in topXSkills:
			userSN[skill] = 1
			for page in range(1, self.maxPages + 1):
				yield scrapy.Request(url=self.baseUrl % (skill, self.perPage, page),
									 headers=self.headers,
									 callback=self.parse)

	def parse(self, response):
		users = json.loads(response.body)["items"]
		# print(len(users))				# per_page
		# print(type(response))			# scrapy.http.response.text.TextResponse'
		# print(type(response.body))	# str
		# print(type(users))			#list

		# get skills as per the request
		# https://api.github.com/search/users?q=python&sort=followers&per_page=2&page=1
		param_q = re.search('q\=(.*?)&', response.url).group(0)[2:-1]

		page = re.search('&page\=(.*)', response.url).group(0)[6:]
		print('########################', param_q, page, len(users))

		# yield a request for each user
		# this plays a same role as start_request and parse data in a deeper level in its callback
		for user in users:
			yield scrapy.Request(url=user['url'], headers=self.headers,
								 callback=self.parse_user_details(param_q, response.url))

		pass

	def parse_user_details(self, q, reqUrl):
		def f(response):
			user = json.loads(response.body)
			item = UserItem()
			item["login"] = user["login"]
			item["id"] = user["id"]
			item['apiUrl'] = user['url']
			item['htmlUrl'] = user['html_url']
			item['avatarUrl'] = user['avatar_url']
			item['name'] = user['name']
			item['company'] = user['company']
			item['blog'] = user['blog']
			item['location'] = user['location']
			item['email'] = user['email']
			item['bio'] = user['bio']
			item['pubRepos'] = user['public_repos']
			item['followers'] = user['followers']
			item['q'] = q
			item['reqUrl'] = reqUrl

			# get the user sn of current skill from the dictionary
			# and meanwhile update the value
			item['sn'] = userSN[q]
			userSN[q] += 1

			yield item
			pass

		return f
		pass

	pass

# page = response.url.split("/")[-2]
# filename = 'mingyan-%s.html' % page
# with open(filename, 'wb') as f:
# 	f.write(response.body)
# 	self.log('saved file: %s' % filename)
