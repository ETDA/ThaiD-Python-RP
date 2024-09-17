from flask import Flask, url_for, session, render_template, redirect, request, current_app
import base64, requests
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_client import token_update

app = Flask(__name__)
app.secret_key = '!secret'
app.config.from_object('config')

#ThaID Well Known URL ตามาตรฐาน OpenID Conect 
THAID_WELL_KNOWN_URL = 'https://imauth.bora.dopa.go.th/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='thaid',
    server_metadata_url=THAID_WELL_KNOWN_URL,
    client_kwargs={
        #Scope ที่ทาง ThaID รองรับ
        'scope': 'openid pid address gender birthdate given_name middle_name family_name name given_name_en middle_name_en family_name_en name_en title title_en ial smartcard_code date_of_expiry date_of_issuance'
    }
)

# Route หน้า Home Page
@app.route('/')
def homepage():
    user = session.get('user')
    thaidtoken = session.get('thaidtoken')
    if user is not None:
        return render_template('auth.html', thaidtoken=thaidtoken, datetime=datetime)
    else:
        return render_template('home.html')

# Route สำหรับลงชื่อเข้าใช้งานระบบด้วย ThaID
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    # Redirect ไปที่ ThaID
    return oauth.thaid.authorize_redirect(redirect_uri)

# Route สำหรับได้รับรหัสยืนยันเพื่อรับชุด Token
@app.route('/auth')
def auth():
    # ส่งรหัสยืนยัน และรับชุด Token
    token = oauth.thaid.authorize_access_token()
    session['user'] = token['userinfo']
    session['thaidtoken'] = token
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

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