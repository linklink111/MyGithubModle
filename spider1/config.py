# spider essence
# ==================================================================
ACCESS_TOKEN = ''
SPIDER_NAME = 'elwin'


# config the keys
# ==================================================================
# specify skills to append corresponding to the keyword:
# {'kw': 'a', 'sk': ['aaa', 'bbb']},
# no skills specified for the keyword:
# {'kw': 'b'}
paramKeys = [
    {'kw': 'nosql'},
    {'kw': 'b'}
]


# limitation of the number of results returned from github
# ===================================================================
# indicate how many pages of repos to search by the current keyword
# 20
maxRepoPages = 20

# indicate how many repos per page (per run)
# as each run only one page of repos will be requested
# in order to control the rate of requests and simplify the spider
# 50
perPageRepo = 50

# NOTE: maxRepoPages * perPageRepo <= 1000

# up to 100 result per page of contributors retrieval
# 100
perPageContributors = 100

# up to 500 non-anonymouse contributors as per github api
# so the max pages of contributors is 500/perPageContributors
# 5
maxPagesContributors = 5


# ===================================================================
# page = response.url.split("/")[-2]
# filename = 'mingyan-%s.html' % page
# with open(filename, 'wb') as f:
# 	f.write(response.body)
# 	self.log('saved file: %s' % filename)
