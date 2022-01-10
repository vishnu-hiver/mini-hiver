import snowflake.connector
import json

ctx = snowflake.connector.connect(
    user='vanigupta69',
    password='Vanigupta@123',
    account='tw24335.us-central1.gcp',
    database='CREDENTIALS'
)

def insert_creds():
    curr = ctx.cursor()
    client_secret = json.load(open('client_secret.json'))
    user_info = json.dumps(client_secret)
    sql = f"insert into user_info values('{user_info}')"
    curr.execute(sql)
    ctx.commit()

def read_creds():
    curr = ctx.cursor()
    curr.execute("select * from user_info;")
    print(curr.fetchall())