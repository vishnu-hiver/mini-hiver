import os
import flask
from flask import render_template
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/userinfo.profile", "https://mail.google.com/", "https://www.googleapis.com/auth/userinfo.email", "openid"]
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

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

emails = ["sathvik.s@grexit.com", "vani.g@grexit.com","vishnuerapalli01@gmail.com","sathviksaya@gmail.com"]

sath_token={'client_id': '1036067471598-mqt6v2j085vve462skcl1pbj80d9055e.apps.googleusercontent.com', 'client_secret': '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', 'refresh_token': None, 'scopes': ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/userinfo.profile', 'https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email', 'openid'], 'token': 'ya29.A0ARrdaM87nzO4Lv2FLjNY8QHe842lOIaHfgyoZxfeUxuC7PvMz2CZpVq3eVEKYBA9A3UzK44wMAfvnIsUlrlMTUO2lp2UP6V9vrWaDirjpg_lwuObgN8Th7Q4IFrfn00wL0UW7uQZ7lRRG_ZdhZ099rc6_2IshA', 'token_uri': 'https://oauth2.googleapis.com/token'}
@app.route('/')
def index():
  return render_template("login.html")


@app.route('/test')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
  gmail = googleapiclient.discovery.build(
      "gmail", "v1", credentials=credentials)
  
  credentials1 = google.oauth2.credentials.Credentials(**sath_token)
  gmail1 = googleapiclient.discovery.build("gmail", "v1", credentials=credentials1)

  files = gmail.users().threads().list(userId='me').execute()
  # files1 = gmail1.users().threads().list(userId='me').execute()
  

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)
  # print(flask.session['credentials'])


  # labelVar = gmail.users().labels().create(userId="me", body={"name": "Training Exercise"}).execute()
  # print(labelVar)

  resMails = dict(**files)
  for mail in resMails["threads"]:
    content = mail["snippet"]
    if "training" in content:

      # puts a label to that particular mail
      # gmail.users().threads().modify(userId="me", id=mail["id"], body={"addLabelIds": ["Label_1"]}).execute()

      # gets raw message from the selected threads
      rawData = gmail.users().threads().get(userId="me", id=mail["id"]).execute()
      
      for mId in rawData["messages"]:
        rawMessage = gmail.users().messages().get(userId="me", id=mId["id"], format="raw").execute()
        resInsert = gmail1.users().messages().insert(
          userId="me", 
          body={
            "id":mId["id"],
            "labelIds":["INBOX"],
            "raw":rawMessage["raw"]
          }).execute()

  return flask.jsonify(**files)
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

  return flask.redirect(authorization_url)


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