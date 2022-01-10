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
    id = tokens["client_id"]
    user_info = json.dumps(tokens)

    query = f"update user_info set user_info={user_info} where client_id={id}"

    sql = f"insert into user_info values('{id}','{user_info}');"
    curr.execute(sql)
    ctx.commit()

def read_creds():
    curr = ctx.cursor()
    curr.execute("select * from user_info;")
    return curr.fetchall()