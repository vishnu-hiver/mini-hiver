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
    sql = f"insert into user_info values('{user_info}')"
    curr.execute(sql)
    ctx.commit()

def read_creds():
    curr = ctx.cursor()
    curr.execute("select * from user_info;")
    return curr.fetchall()