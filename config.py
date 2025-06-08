import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CAPTCHA_API_KEY')
EMAIL = os.getenv('BLS_EMAIL')
PASSWORD = os.getenv('BLS_PASSWORD')
SITE_KEY = '6LcVdzUqAAAAAPGbSct68gBCV0Rh3QWAVJdYlMh0'

BASE_URL = "https://blsitalypakistan.com"
LOGIN_URL = f"{BASE_URL}/account/login"
APPOINTMENT_URL = f"{BASE_URL}/bls_appmnt/bls-italy-appointment"
LOGOUT_URL = BASE_URL
CHECK_INTERVAL = 300