# Integration of ThaID with Python Flask Framework
This project shows how to connect **ThaID** to the **Python Flask Framework** using **Open ID Connect & OAuth2 authentication**. It lets you safely log in and give users access through ThaID.

## # 📁🎛️ Settings for connecting to ThaID ##
location: `Python/config.py`

**Variables** for configuration used with ThaID data integration, such as Client ID, Client Secret.
```Python
# เพิ่ม Thaid Client ID
THAID_CLIENT_ID = '{Client_id}'
# เพิ่ม Thaid Client Secret
THAID_CLIENT_SECRET = '{Client_secret}'
```
---
## # 📁📄 Library for integrate to ThaID ##
location: `Python/requirements.txt`

```Python
Flask
Authlib
requests
```
---
## # 📁🚩 Application configuration & Routing ##
location: `Python/app.py`

**THAID_WELL_KNOWN_URL** : Well-Known Configuration Endpoint for OpenID Provider's configuration information. \
**name** : Provider Name. \
**client_kwargs** : Scopes are utilized by an application during the authentication process to grant authorization for accessing a user's information.
```Python
THAID_WELL_KNOWN_URL = 'https://imauth.bora.dopa.go.th/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='thaid',
    server_metadata_url=THAID_WELL_KNOWN_URL,
    client_kwargs={
        'scope': 'openid pid address gender birthdate given_name middle_name family_name name given_name_en middle_name_en family_name_en name_en title title_en ial smartcard_code date_of_expiry date_of_issuance'
    }
)
```
**Home Page** : If the user is not authenticated, redirect them to the authentication page. Conversely, if the user is authenticated, render the home page and display their profile.
```Python
@app.route('/')
def homepage():
    user = session.get('user')
    thaidtoken = session.get('thaidtoken')
    if user is not None:
        return render_template('auth.html', thaidtoken=thaidtoken, datetime=datetime)
    else:
        return render_template('home.html')
```
**Login Page** : Redirect to the ThaID login portal to initiate the authentication process. \
```Python
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.thaid.authorize_redirect(redirect_uri)
```
**Callback Route** : Receive the authorization code from the user, retrieve the token using the library function, and store the user profile in the session. 
```Python
@app.route('/auth')
def auth():
    token = oauth.thaid.authorize_access_token()
    session['user'] = token['userinfo']
    session['thaidtoken'] = token
    return redirect('/')
```
**Logout Route** : Logout and remove user data.
```Python
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
```
**Inspect Route** : Sample code for testing DOPA's inspect API
```Python
@app.route('/inspect')
def inspect():
    INSTROSPECT_URL = "https://imauth.bora.dopa.go.th/api/v2/oauth2/introspect/"
    acess_token = request.headers['authorization'].split(" ")[1]
    secret_string = current_app.config['THAID_CLIENT_ID'] + ":" + current_app.config['THAID_CLIENT_SECRET']
    secret_string_bytes = secret_string.encode("ascii") 
    base64_bytes = base64.b64encode(secret_string_bytes) 
    bearer = base64_bytes.decode("ascii")
    headers = {'Authorization': f'Basic {bearer}'}
    response = requests.post(INSTROSPECT_URL,data={'token': acess_token},headers=headers)
    return response.text
```
**Token Update Event** : Auto refresh token function. 
```Python
@token_update.connect_via(app)
def on_token_update(sender, name, token, refresh_token=None, access_token=None):
    if refresh_token:
        item = OAuth2Token.find(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.find(name=name, access_token=access_token)
    else:
        return

    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()
```
---

## # 📁📄 Home Page Display for the Application ##
location: `Python/templates/home.html`

---

## # 📁📄 Display Page for Showing Information After Authentication ##
location: `Python/templates/auth.html`