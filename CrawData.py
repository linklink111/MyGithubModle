# 爬取 github 信息存储到数据库
# group: 林堃 纪宗尧 郭永旭

import psycopg2
import yaml
import os
import json
import requests

# 为了防止本人的数据库密码被传到 github，采用了配置文件= =
cur_dir_path = os.path.abspath(".")
secret_yaml_file_path = os.path.join(cur_dir_path, "secret.yaml")
secret_yaml_file = open(secret_yaml_file_path,'r',encoding='utf8')
secret_fdata = secret_yaml_file.read()
secret_yaml_file.close()
secret_data = yaml.load(secret_fdata)
print(secret_data)

sql_yaml_file_path = os.path.join(cur_dir_path, "sql.yaml")
sql_yaml_file = open(sql_yaml_file_path,'r',encoding='utf8') 
sql_fdata = sql_yaml_file.read()
sql_yaml_file.close()
sql_data = yaml.load(sql_fdata)
print(sql_data)
# 连接数据库

db_name = "giteehub"
user = "postgres"
port = 5432
print(secret_data['password'])
mpassword = secret_data['password']
mtoken = secret_data['token']
db_conn = psycopg2.connect(
    database = "giteehub", 
    user = "postgres", 
    password = mpassword, 
    host = "127.0.0.1", 
    port = port)

# 用游标执行数据库操作

cursor = db_conn.cursor()
# 测试一下有没有连通数据库

# try:
#     cursor.execute(sql_data['testInsert'])
#     db_conn.commit()
#     db_conn.close()
# except Exception as e:
#     print(e)

# 以上部分——连接数据库，已通过单元测试

# 获取用户信息

# 数据样例

# data1 = {
#   "login": "HashLips",
#   "id": 88177839,
#   "node_id": "MDQ6VXNlcjg4MTc3ODM5",
#   "avatar_url": "https://avatars.githubusercontent.com/u/88177839?v=4",
#   "gravatar_id": "",
#   "url": "https://api.github.com/users/HashLips",
#   "html_url": "https://github.com/HashLips",
#   "followers_url": "https://api.github.com/users/HashLips/followers",
#   "following_url": "https://api.github.com/users/HashLips/following{/other_user}",
#   "gists_url": "https://api.github.com/users/HashLips/gists{/gist_id}",
#   "starred_url": "https://api.github.com/users/HashLips/starred{/owner}{/repo}",
#   "subscriptions_url": "https://api.github.com/users/HashLips/subscriptions",
#   "organizations_url": "https://api.github.com/users/HashLips/orgs",
#   "repos_url": "https://api.github.com/users/HashLips/repos",
#   "events_url": "https://api.github.com/users/HashLips/events{/privacy}",
#   "received_events_url": "https://api.github.com/users/HashLips/received_events",
#   "type": "User",
#   "site_admin": false,
#   "name": "HashLips",
#   "company": null,
#   "blog": "https://hashlips.online/HashLips",
#   "location": null,
#   "email": null,
#   "hireable": null,
#   "bio": null,
#   "twitter_username": "de_botha",
#   "public_repos": 15,
#   "public_gists": 0,
#   "followers": 664,
#   "following": 0,
#   "created_at": "2021-07-30T04:54:11Z",
#   "updated_at": "2021-09-19T14:27:02Z"
# }

# url1 = "https://api.github.com/users/HashLips"


# user_list = {'HashLips','authelia','waydroid','robertdavidgraham','qier222','Sairyss','Tencent','VickScarlet','lootproject'}
user_list = {' peng-zhihui',' trailofbits','Snailclimb', 
'louislam','vuejs','babysor',
'facebook',
'fatedier',
'ossrs',
'vinta',
'yt-dlp',
'ihciah',
'sdras',
'Hack-with-Github',
'anncwb',
'Python-World',
'wimpysworld',
'mattiasgustavsson',
'apache',
'donet5',
'raywenderlich',
'herosi',
'alibaba'
'vuejs'
}

insert_users = 0
insert_repo = 0

if insert_users == 1:
    for githubuser in user_list:
        try:
            url1 = "https://api.github.com/users/{}".format(githubuser)
            response = requests.get(url1,timeout = 3)
            if response.content:
                data = response.json()
                print(data)
                cursor.execute("INSERT INTO \"user\" VALUES ({},'{}','{}','{}','{}','{}','{}',{},{},{},{},{},{},{})".format(data["id"],data["login"],data["name"].replace("\'","\'\'"),data["company"],data["email"],data["created_at"],data["type"],'null','null','null','null','null','null','null'))
                db_conn.commit()
                # jsonStr = json.loads(response.content)
                # print(jsonStr)
        except Exception as e:
            print(e)
headers={"Authorization":"token "+mtoken}

if insert_repo == 1:
    for githubuser in user_list:
        try:
            url2 = "https://api.github.com/users/{}/repos".format(githubuser)
            response = requests.get(url2,timeout = 3,headers=headers)
            if response.content:
                data = response.json()
                # break
                # print(data)   # 好吧，api被限制了
                # data = json.load(data)
                # print(data[2])
                # print(data)
                for repo in data:                             # id  url own   name des lan creat fork  del  update
                    # print(type(repo))
                    # print(repo["owner"]["id"])
                    # break
                    # print(repo)
                    # break
                    # for colv in repo.values():
                    #     if type(colv) is str:
                    #         colv = colv.replace("'","''")
                    db_conn = psycopg2.connect(
                    database = "giteehub", 
                    user = "postgres", 
                    password = mpassword, 
                    host = "127.0.0.1", 
                    port = port)

                    des = repo["description"]
                    if repo["description"] is not None:
                        des = repo["description"].replace("\'","\'\'")
                        print(des)
                        # repo["description"].replace("`","\`")
                    try:
                        # repo = json.loads(repo)                  # id  url own   name des lan creat fork  del  update
                        cursor.execute("INSERT INTO project VALUES ({},'{}', {},'{}','{}','{}','{}', {},  {},  '{}'  )".format(repo["id"],repo["url"],repo["owner"]["id"],repo["name"],des,repo["language"],repo["created_at"],'null','null',repo["updated_at"]))
                    except psycopg2.IntegrityError:
                        db_conn.rollback()
                    else:
                        db_conn.commit()
                    db_conn.close()
                    # db_conn.close()
                    # break
                # break
                # jsonStr = json.loads(response.content)
                # print(jsonStr)
        except Exception as e:
            print(e)


# data1_ = json.loads(data1)
# print(data1_)

from github import Github
# using an access token
# g = Github("access_token")
# using an access token
g = Github(mtoken)  # token




