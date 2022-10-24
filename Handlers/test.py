import datetime
import json
import math
import os
import urllib.request

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from Handlers.Login import SignIn
import urllib

if __name__ == '__main__':
    sign_in = SignIn({'barcode': '201209', 'password': 'Attbpdc030513!'})
    a = sign_in.auth_moodle()

    new_res = requests.get('https://moodle.astanait.edu.kz/course/view.php?id=2326',
                           headers=a)
    soup = BeautifulSoup(new_res.text, 'lxml')
    course_links = soup.find(class_="course-content").find(class_="weeks").find_all('a')

    for link in course_links:
        current_dir = ""
        href = link.get('href')

        # Checking only resources... Ignoring forum and folders, etc
        if "resource" in href:
            webFile = urllib.request.urlopen(href)
            url = current_dir + webFile.geturl().split('/')[-1].split('?')[0]
            file_name = urllib.parse.unquote(url).decode('utf8')
            if os.path.isfile(file_name):
                print("File found : ", file_name)
                continue
            print(
                "Creating file : ", file_name)
            pdfFile = open(file_name, 'wb')
            pdfFile.write(webFile.read())
            webFile.close()
            pdfFile.close()

    # #     print(course.text, course.get('href'))
    # print(new_res.url)
    # def calculate(divider_time):
    #     overall_time = a / divider_time
    #     first_type_of_date = math.floor(overall_time)
    #     second_type_of_date = math.floor((overall_time - first_type_of_date) * 24)
    #     return [str(first_type_of_date),str(second_type_of_date)]
