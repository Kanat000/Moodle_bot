import re

import requests


class SignIn:
    __url_domain = "https://moodle.astanait.edu.kz/login/index.php"

    def __init__(self, data):
        self.__login = data['barcode']
        self.__password = data['password']

    def auth_moodle(self) -> requests.Session():
        s = requests.Session()
        r_1 = s.get(url=self.__url_domain)
        pattern_auth = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(pattern_auth, r_1.text)
        token = re.findall("\w{32}", token[0])[0]
        payload = {'anchor': '', 'logintoken': token, 'username': self.__login,
                   'password': self.__password, 'rememberusername': 1}
        r_2 = s.post(url=self.__url_domain, data=payload)
        if r_2.url != self.__url_domain:
            return r_2.request.headers
        else:
            return None
