# -*- coding: utf-8 -*-
import time
import os
import requests


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class GithubcrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


perPage = 100
folder = time.strftime('%m%d%Y %H%M%S', time.localtime())


# if not os.path.exists("res\\%s" % folder):
# 	os.makedirs("res\\%s" % folder)


class GithubUserPipeline(object):
    def process_item(self, item, spider):
        sn = item['sn']
        page = ((sn - 1) // perPage) + 1
        q = item['q']

        filename = 'res\\%s\\%s_%s.dat' % (folder, q, page)
        with open(filename, 'ab') as f:
            f.write(str(item))
            f.write(',')

        return item


class GithubUserPipeline_o(object):
    def process_item(self, item, spider):
        sn = item['sn']
        page = ((sn - 1) // perPage) + 1
        q = item['q']

        filename = 'res\\user info-github-%s_%s.dat' % (q, page)
        with open(filename, 'ab') as f:
            if sn % perPage == 1:
                f.write('[')

            f.write(str(item))
            f.write(',')

            if sn % perPage == 0:
                f.write(']')

        return item


apiUrl = "http://staging.api.hitalent.us/api/v1/github-talents"
# apiUrl = "http://192.168.0.246:8080/api/v1/github-talents"


# class GithubRepoPipeline(object):
# 	def process_item(self, item, spider):
# 		response = requests.post(apiUrl, data=str(item), headers={'Content-Type': 'application/json'})
# 		# print (">>>>>>>>>>>>>>>>>>>>>>status: %s, reason: %s" % (response.status_code, response.reason))
# 		return item

class GithubRepoPipeline(object):
    def process_item(self, item, spider):

        try:
            response = requests.post(apiUrl, data=str(item), headers={'Content-Type': 'application/json'})
            if 'id' not in response.json():
                filename = 'error.txt'
                with open(filename, 'ab') as f:
                    f.write(str(item))
                    f.write('\r\n Server Error at: ' + time.strftime('%m-%d-%Y %H:%M:%S', time.localtime()))
                    f.write('\r\n--------------------------------------------\r\n')
        except:
            filename = 'error.txt'
            with open(filename, 'ab') as f:
                f.write(str(item))
                f.write('\r\n Api Error at: ' + time.strftime('%m-%d-%Y %H:%M:%S', time.localtime()))
                f.write('\r\n--------------------------------------------\r\n')

        # print (">>>>>>>>>>>>>>>>>>>>>>status: %s, reason: %s" % (response.status_code, response.reason))
        return item
