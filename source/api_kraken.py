import time
import hmac
import hashlib
import base64
import urllib.parse
from time import sleep
from source.currencies import *

class KrakenApi:
    def __init__(self, api_key, api_secret):
        self.__key = api_key
        self.__secret = api_secret

    def kraken_api_call(self, uri_path, data=None, retries=3):
        url = "https://api.kraken.com"
        api_nonce = str(int(time.time() * 1000))
        data = data or {}
        data['nonce'] = api_nonce
        post_data = urllib.parse.urlencode(data)
        message = (api_nonce + post_data).encode()
        sha256 = hashlib.sha256(message).digest()
        api_path = (uri_path).encode()
        secret = base64.b64decode(self.__secret)
        hmac_key = hmac.new(secret, api_path + sha256, hashlib.sha512)
        headers = {
            'API-Key': self.__key,
            'API-Sign': base64.b64encode(hmac_key.digest()),
        }

        for attempt in range(retries):
            try:
                response = requests.post(url + uri_path, headers=headers, data=data)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    sleep(2)
                    return None
                else:
                    raise
        return None
