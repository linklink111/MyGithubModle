import json
import scrapy
import re
import ast

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
	'python', 'java', 'c++', 'javascript', 'react', 'algorithm', 'html', 'css', 'redis',
	'c%23', 'oracle', 'webapi', 'nodejs', 'bash', 'shell', 'php', 'typescript', 'elasticsearch',
	'ruby', 'swift', 'assembly', 'go', 'objective-c', 'vb.net', 'matlab', 'vba', 'scala',
	'groovy', 'perl', 'angular', '.net+core', 'dotnet', 'spring', 'django', 'cordova', 'tensorflow',
	'xamarin', 'spark', 'hadoop', 'mysql', 'sql+server', 'postgresql', 'mongodb', 'sqlite',
	'mariadb', 'azure', 'google+cloud', 'amazon', 'db2', 'bigquery', 'hbase', 'wordpress',
	'ios', 'nosql', 'apache', 'sharepoint', 'linux', 'andriod', 'artificial+intelligence', 'ai',
	'mobile', 'front-end', 'back-end', 'agile', 'block+chain'
]

userSN = {}
logPath = 'log.dat'


class UserSpider(scrapy.Spider):
	name = "GithubUserSpiderv2"
	allowed_domains = ["api.github.com"]

	maxPages = 10  # this value * perPage is up to 1000
	perPage = 100  # this value * maxPages is up to 1000
	skillPassed = 0

	baseUrl = "https://api.github.com/search/users?q=%s&sort=followers&per_page=%s&page=%s"
	access_token = "bearer 15b78086732e996d63a3ced1804fe9d42ce77c77"
	# access_token = "bearer d30ca3ac48f774a7650552101e20963b06110c12"
	headers = {'Authorization': access_token}

	def start_requests(self):
		self.read_log()

		x = len(topXSkills)
		start_skill = self.skillPassed if self.skillPassed < x else 0
		end_skill = (start_skill + 4) if (start_skill + 4) < x else x
		print ('###### start skill: %d, end skill: %d' % (start_skill, end_skill))

		for skillIndex in range(start_skill, end_skill):
			skill = topXSkills[skillIndex]
			userSN[skill] = 1

			for page in range(1, self.maxPages + 1):
				yield scrapy.Request(url=self.baseUrl % (skill, self.perPage, page),
									 headers=self.headers,
									 callback=self.parse)

			self.skillPassed += 1

		self.write_log(self.skillPassed if self.skillPassed < x else 0)
		pass

	def parse(self, response):
		users = json.loads(response.body)["items"]
		# print(len(users))				# per_page
		# print(type(response))			# scrapy.http.response.text.TextResponse'
		# print(type(response.body))	# str
		# print(type(users))			#list

		# get skill and current page as per the request
		# https://api.github.com/search/users?q=python&sort=followers&per_page=2&page=1
		# replace %23 to s for csharp(c#)
		param_q = re.search('q\=(.*?)&', response.url).group(0)[2:-1].replace('%23', 's')
		page = re.search('&page\=(.*)', response.url).group(0)[6:]
		print('######', param_q, page, len(users))

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

	def read_log(self):
		log = None
		try:
			log = open(logPath, 'rb')
			data = log.read()
			o = ast.literal_eval(data)
			print ("###### data in log", data)

			self.skillPassed = o["skillPassed"]
		except:
			self.skillPassed = 0
		finally:
			if log:
				log.close()

		pass

	def write_log(self, skillsPassed):
		with open(logPath, 'wb') as log:
			status = {"skillPassed": skillsPassed}
			log.write(str(status))

		pass

	pass

# page = response.url.split("/")[-2]
# filename = 'mingyan-%s.html' % page
# with open(filename, 'wb') as f:
# 	f.write(response.body)
# 	self.log('saved file: %s' % filename)
