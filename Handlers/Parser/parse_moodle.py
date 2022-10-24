import datetime
import math
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests as request

from Database.dbConnection import Sqlite
from Handlers.Login import SignIn
from config import db_name


def calculate(a, divider_time):
    overall_time = a / divider_time
    first_type_of_date = math.floor(overall_time)
    second_type_of_date = math.floor((overall_time - first_type_of_date) * 24)
    return [str(first_type_of_date), str(second_type_of_date)]


class Parser:
    __db = Sqlite(db_name)
    __seconds_in_day = 86400
    __seconds_in_hour = 3600
    __seconds_in_minute = 60
    __base_url = 'https://moodle.astanait.edu.kz/'
    __grade_url = 'https://moodle.astanait.edu.kz/grade/report/user/index.php'
    __schedule_url = 'https://moodle.astanait.edu.kz/calendar/view.php?view=day'
    __schedule_events = ['AS', 'AT']

    def __get_header(self, chat_id):
        log_info = self.__db.get_log_info_by_chat_id(chat_id)
        signIn = SignIn({'barcode': log_info[0], 'password': log_info[1]})
        return signIn.auth_moodle()

    def __get_courses(self, header):
        page_res = request.get(self.__base_url, headers=header)
        page_soup = BeautifulSoup(page_res.text, 'lxml')
        return page_soup.find_all('a', {'data-parent-key': 'mycourses'})

    def __get_grade_table(self, course_id, header):
        grade_res = request.get(self.__grade_url,
                                params={'id': course_id},
                                headers=header)

        return BeautifulSoup(grade_res.text, 'lxml')

    def __get_time_left_for_deadline(self, seconds):
        if seconds >= self.__seconds_in_day:
            time_arr = calculate(seconds, self.__seconds_in_day)
            if int(time_arr[1]) == 0:
                return time_arr[0] + ' days left'
            else:
                return time_arr[0] + ' days ' + time_arr[1] + ' hours left'
        elif seconds >= self.__seconds_in_hour:
            time_arr = calculate(seconds, self.__seconds_in_hour)
            if int(time_arr[1]) == 0:
                return time_arr[0] + ' hours left'
            else:
                return time_arr[0] + ' hours ' + time_arr[1] + ' minutes left'
        else:
            time_arr = calculate(seconds, self.__seconds_in_minute)
            if int(time_arr[1]) == 0:
                return time_arr[0] + ' minutes left'
            else:
                return time_arr[0] + ' minutes ' + time_arr[1] + ' seconds left'

    def parse_overview_grade(self, chat_id):
        header = self.__get_header(chat_id)
        courses = self.__get_courses(header)
        grades_msg = ''
        for course in courses:
            grades_msg += f'\n<b>"{str(course.text).strip()}"</b>\n'
            id_of_course = int(course.get('data-key'))
            grade_soup = self.__get_grade_table(id_of_course, header)
            registers = grade_soup.find_all('th', {'class': 'level3'})
            grades = grade_soup.select("td.level3.column-grade")
            for i in range(len(registers)):
                title = registers[i].find_next('span', {'class': 'gradeitemheader'})
                grade = grades[i]
                grades_msg += str(title.text) + ':<i>' + str(grade.text) + '</i> \n'

        return grades_msg

    def parse_overview_attendance(self, chat_id):
        header = self.__get_header(chat_id)
        courses = self.__get_courses(header)
        attendance_msg = ''
        for course in courses:
            attendance_msg += f'\n<b>"{str(course.text).strip()}"</b>\n'
            id_of_course = int(course.get('data-key'))
            grade_soup = self.__get_grade_table(id_of_course, header)
            lesson_title_items = grade_soup.find_all('th', {'class': 'level2'})
            attendance_grade = grade_soup.select('td.level2.column-grade')[1].text
            attendance_title = lesson_title_items[1].find_next('a', {'class': 'gradeitemheader'}).text

            attendance_msg += attendance_title + ': <u>' + attendance_grade + '</u>\n'

        return attendance_msg

    def parse_overview_deadline(self, days, chat_id):
        current_date = datetime.datetime.today().timestamp()
        msg = '<b>Deadline(Overview): </b>\n'
        for day in range(0, days):
            page_res = request.get(self.__schedule_url,
                                   params={'time': current_date + (day * self.__seconds_in_day)},
                                   headers=self.__get_header(chat_id))
            page_soup = BeautifulSoup(page_res.text, 'lxml')
            assignments = page_soup.find_all('div', {'data-event-component': 'mod_assign'})
            for ass in assignments:
                name = ass.find_next('h3', {'class': 'name'}).text
                dead_info = ass.find_all_next('div', {'class': 'col-11'})

                time_url = str(dead_info[0].find_next('a').get('href'))

                dead_seconds = int(urlparse(time_url).query[-10:])
                if dead_seconds >= current_date:
                    seconds_left = dead_seconds - current_date
                    time_left = self.__get_time_left_for_deadline(seconds_left)
                    dead_time = dead_info[0].text
                    dead_subject = dead_info[len(dead_info) - 1].text

                    msg += str(time_left) + ' | ' + str(dead_time) + ' | ' + str(name) + ' | ' \
                           + str(dead_subject) + '\n\n'

        return msg

    def parse_lessons(self, chat_id):
        courses = []
        for course in self.__get_courses(self.__get_header(chat_id)):
            courses.append([str(course.text).strip(), course.get('data-key')])
        return courses

    def get_detailed_grades(self, chat_id, course_id):
        grade_table = self.__get_grade_table(course_id, self.__get_header(chat_id))
        course_name = grade_table.find_all('div', {'class': 'homelink'})[0].text
        item_names = grade_table.find_all('th', {'class': 'column-itemname'})
        item_names = item_names[3:]
        grades = grade_table.select('td.itemcenter.column-grade')
        msg = '<b>' + str(course_name) + '</b>\n\n'
        for i in range(len(item_names)):
            msg += '<b><i>' + item_names[i].text + '</i></b> : <pre>' + grades[i].text + '</pre>\n\n'

        return msg

    def get_name_of_course_by_id(self, chat_id, course_id):
        grade_table = self.__get_grade_table(course_id, self.__get_header(chat_id))
        course_name = grade_table.find_all('div', {'class': 'homelink'})[0].text
        return course_name
