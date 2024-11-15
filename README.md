# 1. คำแนะนำเพื่อใช้งานแอปพลิเคชัน ThaIDAuthenExample เพื่อทดสอบการเชื่อมต่อระบบ ThaID ด้วยภาษา Python 3.12 + Flask

แอปพลิเคชันเป็นตัวอย่างเพื่อแสดงวิธีการเชื่อมต่อ **ThaID** โดยใช้ภาษา **Python 3.12** ร่วมกับเฟรมเวิร์ก **Flask** โดยใช้การยืนยันตัวตนด้วยมาตรฐาน **OpenID Connect & OAuth2**

## # 📁 library ในโปรเจกต์

location: `ThaIDAuthenExample/requirements.txt`

1. **Authlib** เป็น library สำหรับจัดการ การเรียกใช้งาน OAuth2 และ OpenID Connect
2. **Flask** เป็น library สำหรับการสร้างเว็บไซต์
3. **requests** เป็น library สำหรับการเชื่อมต่อไปยังเครื่องแม่ข่ายเว็บอื่นผ่านมาตรฐาน HTTP RESTAPI

## # 📁 Runtime

1. **Python 3.12** (ติดตั้งตามขั้นตอนด้านล่าง)

## # 🎛️ การติดตั้ง และตั้งค่าโปรแกรม Python 3.12 สำหรับใช้งานแอปพลิเคชัน

1. ไปที่ เว็บไซต์ [Python 3.12.7](https://www.python.org/downloads/release/python-3127/) เพื่อทำการดาวน์โหลด Python
2. เลือกดาวน์โหลด **Windows installer (64-bit)** หรือตัวเลือกอื่นตามระบบปฏิบัติการที่ใช้
3. ติดตั้ง **Python** และตั้งค่าตามที่ใช้งานหรือใช้ค่าเริ่มต้นที่โปรแกรมแนะนำ
4. ตั้งค่าสำหรับการเชื่อมต่อ **ThaID** ตามรายละเอียดดังนี้

---

location: `ThaIDAuthenExample/config.py`
แก่ไขค่าในตัวแปรสำหรับการเชื่อมโยงข้อมูล **ThaID** ได้แก่ **client id, client secret** ตามตัวอย่างในไฟล์

```Python
# เพิ่ม Thaid Client ID
THAID_CLIENT_ID = '{Client_id}'
# เพิ่ม Thaid Client Secret
THAID_CLIENT_SECRET = '{Client_secret}'
```

---

5. เปิด CLI และเปลี่ยนไดเรกเทอรี่ ไปที่ `ThaIDAuthenExample/`
6. รันคำสั่ง `pip install -r requirements.txt` เพื่อติดตั้ง library **Flask**, **Authlib** และ **requests**
7. รันคำสั่ง `flask run` เพื่อเริ่มการทำงานเว็บไซต์
8. เปิด **Browser** และไปที่ **URL** `http://localhost:5000/`

---

<br/><br/><br/>

# 2. องค์ประกอบของแอปพลิเคชันภายในโซลูชัน

## 📁 ThaIDAuthenExample

## # 📁🚩 การตั้งค่าสำหรับการเชื่อมต่อกับ ThaID และการกำหนดเส้นทางเข้าสู่เว็บ

location: `ThaIDAuthenExample/app.py`
ตัวแปรที่สำหรับสำหรับการตั้งค่ามีดังนี้
**THAID_WELL_KNOWN_URL** : Well-Known Configuration Endpoint สำหรับตั้งค่าผู้ให้บริการ OpenID Connect ซึ่งในที่นี่ผู้ให้บริการคือ DOPA \
**name** : ชื่อผู้ให้บริการ \
**client_kwargs** : สโคป(Scope) การขอข้อมูลจากผู้ใช้งานที่ยืนยันตัวตนผ่านระบบ ThaID โดยได้รับข้อมูลจาก DOPA

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

**Home Page** : ถ้าผู้ใช้งานยังไม่ได้ยืนยันตัวตน จะผู้ใช้งานจะถูกพาไปยังหน้าเว็บสำหรับการยืนยันตัวตน ถ้าผู้ใช้งานได้ยืนยันตัวตนหน้าเว็บไซต์จะสร้างข้อมูลขอผู้ใช้งาน

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

**Login Page** : Route สำหรับการพาผู้ใช้งานไปยังหน้ายืนยันตัวผ่านระบบ ThaID \

```Python
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.thaid.authorize_redirect(redirect_uri)
```

**Callback Route** : รับ authorization code จากผู้ใช้งานที่ได้รับจากผู้ให้บริการ DOPA และทำการส่ง authorization code ไปยังเครื่องแม่ข่าย DOPA และรับ Token ที่จัดเก็บข้อมูลผู้ใช้งานเพื่อสร้าง Session จัดเก็บข้อมูลผู้ใช้งาน

```Python
@app.route('/auth')
def auth():
    token = oauth.thaid.authorize_access_token()
    session['user'] = token['userinfo']
    session['thaidtoken'] = token
    return redirect('/')
```

**Logout Route** : ลงชื่อออกและลบข้อมูลผู้ใช้งาน

```Python
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
```

**Inspect Route** : ตัวอย่าง code สำหรับการทดสอบ DOPA's inspect API

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

**Token Update Event** : ฟังก์ชันเพื่ออัปเดทค่า Token อัตโนมัติ

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

## # 📁📄 แสดงผลหน้าแรกของแอปพลิเคชัน

location: `ThaIDAuthenExample/templates/home.html`

---

## # 📁📄 หน้าจอสำหรับแสดงข้อมูลหลังจากยืนยันตัวตน

location: `ThaIDAuthenExample/templates/auth.html`
