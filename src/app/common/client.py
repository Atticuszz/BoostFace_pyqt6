# coding=utf-8
import os
from functools import wraps

import requests
from cryptography.fernet import Fernet


def error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            # HTTP状态错误
            print(
                f"HTTP 状态错误: 状态码 {e.response.status_code}, 详情: {e.response.text}")
        except httpx.HTTPError as e:
            # 其他HTTP错误，如网络连接问题
            print(f"HTTP 错误: {e}")
        except Exception as e:
            # 其他未预料的错误
            print(f"发生错误: {e}")
        return None

    return wrapper


class TokenEncryptor:
    def __init__(self):
        self.key = self.load_or_create_key()

    def load_or_create_key(self):
        key_path = 'secret.key'
        if os.path.exists(key_path):
            with open(key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    def encrypt_data(self, data):
        f = Fernet(self.key)
        return f.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        f = Fernet(self.key)
        return f.decrypt(encrypted_data).decode()


class AuthClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token_encryptor = TokenEncryptor()

    @error_handler
    def login(self, email, password) -> dict | None:
        url = f"{self.base_url}/auth/login"
        # print(url)
        response = requests.post(
            url,
            json={
                "email": email,
                "password": password})

        if response.status_code == 200:
            data = response.json()
            self.save_tokens(
                data.get("access_token"),
                data.get("refresh_token"))
            return data
        else:
            return None

    def save_tokens(self, access_token, refresh_token):
        encrypted_access_token = self.token_encryptor.encrypt_data(
            access_token)
        encrypted_refresh_token = self.token_encryptor.encrypt_data(
            refresh_token)
        with open("tokens.enc", "wb") as file:
            file.write(
                encrypted_access_token +
                b'\n' +
                encrypted_refresh_token)


client = AuthClient("http://127.0.0.1:5000")

if __name__ == "__main__":
    # 使用示例

    response = client.login("zhouge1831@gmail.com", "Zz030327#")
    if response:
        print("登录成功")
    else:
        print("登录失败")
