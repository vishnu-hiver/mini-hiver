import snowflake.connector
# from creds import user_cred
ctx = snowflake.connector.connect(
    user='vanigupta69',
    password='Vanigupta@123',
    account='tw24335.us-central1.gcp',
    database='CREDENTIALS'
)
curr = ctx.cursor()
# values = ""
# cols = ""
# print(len(user_cred))
# for keys in user_cred:
#     cols += f"{keys},"
#     values += f"{str(user_cred[keys])},"
# sql = """
# insert into user_info values('ya29.A0ARrdaM9-iVGfqvGPCGA8yIjCsMKC8EAGE0TsKpSEij-F9kRXfvxkMCtxQVK1budbMw5OrDsKa-vbR1wTnb2U4PcNaRtrBfbAseQZTNnALzE-IkdJDk14dXB1fce57Otdt32ovxDwyvqZ6ffZlvv0H3UUfcteAA','None','https://oauth2.googleapis.com/token','1036067471598-mqt6v2j085vve462skcl1pbj80d9055e.apps.googleusercontent.com','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',PARSE_JSON("['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/userinfo.profile', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email', 'openid']"));
# """
curr.execute("select * from user_info")
# ctx.commit()
# print(curr.)
print(curr.fetchall())