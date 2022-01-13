import snowflake.connector
import json

ctx = snowflake.connector.connect(
    user='vanigupta69',
    password='Vanigupta@123',
    account='tw24335.us-central1.gcp',
    database='CREDENTIALS'
)

historyId = "12345"

def insert_creds(tokens, id):
    curr = ctx.cursor()
    user_info = json.dumps(tokens)
    # finding if the id exists in db table
    pk_bool = f"select * from user_info where client_id='{id}';"
    curr.execute(pk_bool)
    pk_bool = curr.fetchall()
    if len(pk_bool) == 0:
        sql = f"insert into user_info values('{id}','{user_info}', '{historyId}');"
    else:
        sql = f"update user_info set user_cred='{user_info}', history_id='{historyId}' where client_id='{id}';"
    curr.execute(sql)
    ctx.commit()

def read_creds():
    curr = ctx.cursor()
    curr.execute("select * from user_info;")
    return curr.fetchall()

def insert_history_id(id):
    curr = ctx.cursor()
    sql = f"update user_info set history_id='{historyId}' where client_id='{id}';"
    curr.execute(sql)
    ctx.commit()

def read_history_id(id):
    curr = ctx.cursor()
    curr.execute("select * from user_info where client_id='{id}';")
    return curr.fetchall()