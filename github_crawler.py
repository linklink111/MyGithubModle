# 爬取 github 信息存储到数据库
# group: 林堃 纪宗尧 郭永旭

import psycopg2
import yaml
import os

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
print(secret_data['password'])
mpassword = secret_data['password']
db_conn = psycopg2.connect(
    database = "giteehub", 
    user = "postgres", 
    password = mpassword, 
    host = "127.0.0.1", 
    port = "1062")

# 用游标执行数据库操作

cursor = db_conn.cursor()
# 测试一下有没有连通数据库

try:
    cursor.execute(sql_data['testInsert'])
    db_conn.commit()
    db_conn.close()
except Exception:
    print(Exception)

