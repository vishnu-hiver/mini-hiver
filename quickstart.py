import os
import flask
from flask import render_template
import requests
import snowflake.connector
import json

import database_sf as db
import pandas as pd

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

gmailTokens = dict()
gmailIds = set()

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/userinfo.profile", "https://mail.google.com/", "https://www.googleapis.com/auth/userinfo.email", "openid"]
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

# ------- Snowflake credentials -------- #
ctx = snowflake.connector.connect(
    user='vanigupta69',
    password='Vanigupta@123',
    account='tw24335.us-central1.gcp',
    database='CREDENTIALS'
)


app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'Thisisasecret'

def refreshToken(client_id, client_secret, refresh_token):
  params = {
    "grant_type": "refresh_token",
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token
  }
  authorization_url = "https://www.googleapis.com/oauth2/v4/token"
  r = requests.post(authorization_url, data=params)
  if r.ok:
    return r.json()['access_token']
  else:
    return None


# Home route to login
@app.route('/')
def index():
  return render_template("login.html")


@app.route('/listen')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  creds = flask.session['credentials']
  credentials = google.oauth2.credentials.Credentials(
      **creds)
  # db.insert_creds(creds)
  gmail = googleapiclient.discovery.build(
      "gmail", "v1", credentials=credentials)

  # for token in db.read_creds():
  #   tk = json.loads(token[1])
  #   identifier = tk["client_id"]
  #   gmailIds.add(identifier)
  #   gmailTokens[identifier] = googleapiclient.discovery.build("gmail", "v1", credentials=google.oauth2.credentials.Credentials(**tk))
  
  # print(gmailIds, gmailTokens)

  # for id in gmailIds:
  #   pMails = gmailTokens[id].users().threads().list(userId="me").execute()
    



  files = gmail.users().threads().list(userId='me').execute()
  # files1 = gmail1.users().threads().list(userId='me').execute()
  

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)
  # print(flask.session['credentials'])

  # print("Labels---------", gmail.users().labels().list(userId="me").execute())

  # labelVar = gmail.users().labels().create(userId="me", body={"name": "Training Exercise"}).execute()
  # print(labelVar)

  resMails = dict(**files)
  for mail in resMails["threads"]:
    content = (mail["snippet"]).lower()
    if "training" in content:
      # print(content)
      # puts a label to that particular mail
      # gmail.users().threads().modify(userId="me", id=mail["id"], body={"addLabelIds": ["Label_1"]}).execute()

      # gets raw message from the selected threads
      rawData = gmail.users().threads().get(userId="me", id=mail["id"]).execute()
      
      for mId in rawData["messages"]:
        # rawMessage = gmail.users().messages().get(userId="me", id=mId["id"], format="raw").execute()
        rawMessage = gmail.users().messages().get(userId="me", id=mId["id"], format="metadata").execute()
        # for i in rawMessage["payload"]["headers"]:
        #   if i["name"] == "Message-ID":
        #     print(i["value"])
        # gmail1.users().messages().insert(
        #   userId="me", 
        #   body={
        #     "id":mId["id"],
        #     # "labelIds":["INBOX"],
        #     "raw":rawMessage["raw"]
        #   }).execute()

  return render_template("listen.html")
  '''
  for message in resDictionary["messages"]:
    print(message.id)'''
  
  return resDictionary
  
  #flask.jsonify(**files) -->json
  




@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state
  # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
  #     'client_secret.json',
  #     scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/userinfo.profile", "https://mail.google.com/", "https://www.googleapis.com/auth/userinfo.email", "openid"],
  #     state=state)
  # flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # authorization_response = flask.request.url
  # flow.fetch_token(authorization_response=authorization_response)

  # # _id : str("tokens")

  # # # we need to fect from db and dict(_id)

  # credentials = flow.credentials
  # flask.session['credentials'] = {
  #     'token': credentials.token,
  #     'refresh_token': credentials.refresh_token,
  #     'token_uri': credentials.token_uri,
  #     'client_id': credentials.client_id,
  #     'client_secret': credentials.client_secret,
  #     'scopes': credentials.scopes}
  

  return flask.redirect(authorization_url)


# state = flask.session['state']
# flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#     'client_secret.json',
#     scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
#     state=state)
# flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

# authorization_response = flask.request.url
# flow.fetch_token(authorization_response=authorization_response)

# # Store the credentials in the session.
# # ACTION ITEM for developers:
# #     Store user's access and refresh tokens in your data store if
# #     incorporating this code into your real app.
# credentials = flow.credentials
# flask.session['credentials'] = {
#     'token': credentials.token,
#     'refresh_token': credentials.refresh_token,
#     'token_uri': credentials.token_uri,
#     'client_id': credentials.client_id,
#     'client_secret': credentials.client_secret,
#     'scopes': credentials.scopes}


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
      return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.')
  else:
    return('An error occurred.')


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>')


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)