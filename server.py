from flask import Flask
import psycopg2
import yaml
import os
import json
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/new_repo/<int:time_type>")
def new_repo(time_type):
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

    cursor = db_conn.cursor()
    try:
        cursor.execute("select list_by_star({})".format(time_type))
    except Exception as e:
        print(e)
    rows = cursor.fetchall()
    print(rows)  # 今天没有，所以print了[]
    return "<p>Increase_Day</p>"



@app.route("/increase_count/<int:time_type>")
def increase_count(time_type):
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

    cursor = db_conn.cursor()
    try:
        cursor.execute("select increase_count({})".format(time_type))
    except Exception as e:
        print(e)
    rows = cursor.fetchall()
    print(rows)  # 有可能是负值，说明仓库数量减少了
    return "<p>Increase Month</p>"

@app.route("/num_days_ago/<int:days>")
def num_days_ago(days):
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

    cursor = db_conn.cursor()
    try:
        cursor.execute("select num_days_ago({})".format(days))
    except Exception as e:
        print(e)
    rows = cursor.fetchall()
    print(rows)  # 有可能是负值，说明仓库数量减少了
    return "<p>Increase Month</p>"
