# -*- coding: utf-8 -*-

from moodle_api import User, Cohort, Course

def moodle_user(dict):
    """Moodle用户属性，返回Moodle User实例
    """
    return User(username=dict['mobile_phone'], # 使用电话作为用户名
            password=dict['email'],    # 使用邮箱当做密码
            firstname=dict['name'][1:], 
            lastname=dict['name'][0:1], 
            email=dict['email'], 
            maildisplay=0, 
            idnumber=dict['studentid'], 
            institution=dict['institution'], 
            department=dict['department'], 
            phone2=dict['mobile_phone'])

def get_cohort_by_idnumber(idnumber, name):
    """根据idnumber建立或获得群组
    """
    cohort = Cohort(categorytype={"type":"system", "value":"ignored"}, 
                idnumber=idnumber, 
                name=name)
    cohort.create_or_get_id()
    return cohort

def get_course_by_idnumber(idnumber):
    """根据课程ID获得Moodle课程
    """
    course = Course(idnumber=idnumber)
    course.get_by_field()
    return course