# 爬取 github 信息存储到数据库
# group: 林堃 纪宗尧 郭永旭

import psycopg2
import yaml
import os

# 为了防止本人的数据库密码被传到 github，采用了配置文件= =
cur_dir_path = os.path.abspath(".")
secret_yaml_file_path = os.path.join(cur_dir_path, "secret")
secret_yaml_file = open(secret_yaml_file_path,'r',encoding='utf8')
secret_data = secret_yaml_file.read()
secret_yaml_file.close()

# 连接数据库
secret_data = yaml.load()
db_name = "giteehub"
user = "postgres"
mpassword = secret_data['password']
db_conn = psycopg2.connect(
    database = "giteehub", 
    user = "postgres", 
    password = mpassword, 
    host = "127.0.0.1", 
    port = "1062")