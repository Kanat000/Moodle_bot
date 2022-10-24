import requests
import re
from bs4 import BeautifulSoup


if __name__ == '__main__':
    new_res = requests.get('https://moodle.astanait.edu.kz/', headers={'User-Agent': 'python-requests/2.27.1', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'Cookie': 'MOODLEID1_=%250D%25DC%25B0%257FX%25AD; MoodleSession=qhsibekhrgjdcch5acps3u2tvu'})
    soup = BeautifulSoup(new_res.text, 'lxml')
    for course in soup.find_all('a', {'data-parent-key': 'mycourses'}):
        print(course.text, course.get('href'))
