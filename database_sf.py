import snowflake.connector
import json

ctx = snowflake.connector.connect(
    user='vanigupta69',
    password='Vanigupta@123',
    account='tw24335.us-central1.gcp',
    database='CREDENTIALS'
)

def insert_creds(tokens):
    curr = ctx.cursor()
    id = tokens["token"]
    user_info = json.dumps(tokens)

    # finding if the id exists in db table
    pk_bool = f"select * from user_info where client_id='{id}';"
    curr.execute(pk_bool)
    pk_bool = curr.fetchall()
    # print(len(pk_bool))
    if len(pk_bool) == 0:
    # print('id', id, type(id))÷
        sql = f"insert into user_info values('{id}','{user_info}');"
    else:
        sql = f"update user_info set user_cred='{user_info}' where client_id='{id}';"
    curr.execute(sql)
    ctx.commit()

def read_creds():
    curr = ctx.cursor()
    curr.execute("select * from user_info;")
    return curr.fetchall()

# token = open('client_secret.json')
# token = json.load(token)
# insert_creds(token['web'])
# ctx.close()