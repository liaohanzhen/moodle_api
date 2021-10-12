# -*- coding: utf-8 -*-

import requests
import json
import datetime

# 需要连接的Moodle环境
KEY = 'xxxxxxxxx'    # moodle中生成的令牌
URL = 'http://127.0.0.1'   # moodle的网址
ENDPOINT='/webservice/rest/server.php'   # 根据连接协议指定，如rest的为："/webservice/rest/server.php"

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict == None:
        out_dict = {}
    if not type(in_args) in (list, dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args) == list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args) == dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """使用函数名称和键值对调用Moodle API函数
    示例:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """

    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    response = requests.post(URL+ENDPOINT, parameters)
    response = response.json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("调用Moodle出错：\n",  response)
    return response


class Cohort():
    """群组的类.

    示例:
    >>> Cohort(categorytype={"type":"system", "value":"ignored"}, idnumber="21020001", name="2102级0001班")"""
    def __init__(self, **data):
        self.__dict__.update(data)
    
    def create(self):
        "Create this cohort on moodle"
        res = call('core_cohort_create_cohorts', cohorts = [self.__dict__])
        if type(res) == list:
            self.id = res[0].get('id')
    
    def get_by_field(self, field='idnumber'):
        "Get cohort whether it's exist" 
        res = call('core_cohort_get_cohorts') # 获得群组
        if (type(res) == list) and len(res) > 0:
            for item in res: 
                if item.get(field) == self.__dict__.get(field):  # 根据idnumber判断群组是否存在
                    self.id  = item.get('id')
                    self.__dict__.update(item)
                    return self     # 返回群组信息
            return None
        else:
            return None
    
    def create_or_get_id(self):
        "Get Moodle id of the corhort or create one if it does not exists."
        if not self.get_by_field():
            self.create()
    
    def add_member(self, user):
        """添加群组成员
        """
        values = {
            'cohorttype':{
                'type': 'id',
                'value': self.id,
            },
            'usertype':{
                'type': 'id',
                'value': user.id,
            }
        }

        res = call('core_cohort_add_cohort_members', members = [values])
        return res

    def delete_member(self, user):
        """删除群组成员
        """
        values = {
                'cohortid': self.id,
                'userid': user.id,
            }
        res = call('core_cohort_delete_cohort_members', members = [values])
        return res

    def add_enrolcohort(self, course, roleid):
        """根据系统群组创建课程群组
        """
        group = Groups(courseid=course.id, name=self.name, description="", descriptionformat=1, idnumber=self.idnumber)
        group.create_or_get_id()
        values = {
                'courseid': course.id,
                'cohortid': self.id,
                'roleid': roleid,
                'groupid': group.id,
                'name': self.name,
                # 'status': '',
        }

        res = call('local_ws_enrolcohort_add_instance', instance = values)
        if 'data' in res:
            for item in res['data']:
                if item.get('object') == 'enrol':
                    return item
            return False            
        return False
    
    def get_enrolcohort(self, course):
        """确定系统群组是否在课程群组已有同步
        """
        values = {
                'id': course.id,
        }
        res = call('local_ws_enrolcohort_get_instances', course = values)
        if 'data' in res:
            res_data = res['data']
            if (type(res_data) == list) and len(res_data) > 0:
                for item in res_data: 
                    if item.get('courseid') == course.id and item.get('cohortid') == self.id:  # 根据字段值判断课程小组是否存在
                        return item     # 返回执行结果
                return False
        else:
            return False

    def add_or_get_enrolcohort(self, course, roleid):
        """如果系统群组在课程群组不存在，则新建
        """
        res = self.get_enrolcohort(course)
        if not res:
            return self.add_enrolcohort(course, roleid)
        return res


class Groups():
    """小组的类.

    示例:
    >>> Groups(courseid=1, name="科莱特2102期-FICO", description="", descriptionformat=1, enrolmentkey="", idnumber="KLT2102-FICO")"""

    def __init__(self, **data):
        self.__dict__.update(data)

    def create(self):
        "Create this group on moodle"
        res = call('core_group_create_groups', groups = [self.__dict__])
        if type(res) == list and len(res)>0:
            self.id = res[0].get('id')

    def get_by_field(self, field='idnumber'):
        "Get group whether it's exist" 
        res = call('core_group_get_course_groups', courseid=self.courseid) # 获得课程小组
        if (type(res) == list) and len(res) > 0:
            for item in res: 
                if item.get(field) == self.__dict__.get(field):  # 根据字段值判断课程小组是否存在
                    self.id  = item.get('id')
                    self.__dict__.update(item)
                    return self     # 返回课程小组信息
            return None
        else:
            return None

    def create_or_get_id(self, field='idnumber'):
        "Get Moodle id of the group or create one if it does not exists."
        if not self.get_by_field(field):
            self.create()


class Course():
    """Class for a single course.

    Example:
    >>> Course(fullname="Example course", shortname="example", categoryid=1, idnumber=123)
    """
    def __init__(self, **data):
        self.__dict__.update(data)

    def create(self):
        "Create this course on moodle"
        res = call('core_course_create_courses', courses = [self.__dict__])
        if type(res) == list:
            self.id = res[0].get('id')

    def update(self):
        "Update course"
        r = call('core_course_update_courses', courses = [self.__dict__])

    def get_by_field(self, field='idnumber'):
        "根据字段获得相应课程"
        res = call('core_course_get_courses_by_field', field = field, value = self.__dict__.get(field))
        if (type(res) == dict) and len(res['courses']) > 0:
            self.__dict__.update(res['courses'][0])
            return self
        else:
            return None
    
    
class User():
    """Class for a single user.
    
    Example:
    >>> User(username="13322221111", password="sila varno geslo", firstname="Martin", lastname="Liao", email="martin@qq.com", idnumber="A0100", institution="深圳", department="采购", phone1="13322221111")
    """              

    def __init__(self, **data):
        self.__dict__.update(data)
    
    def create(self):
        "Create new user on moodle site"
        valid_keys = ['username', 
                      'password',
                      'firstname', 
                      'lastname', 
                      'email', 
                      'maildisplay',
                      'auth',
                      'idnumber',
                      'institution',
                      'department',
                      'phone2'
                      ]
        values = {}
        for key in valid_keys:
            if key in self.__dict__:
                values[key] = self.__dict__[key]
        # values = {key: self.__dict__[key] for key in valid_keys}
        values['firstnamephonetic'] = 'firstnamephonetic'
        values['lastnamephonetic'] = 'lastnamephonetic'
        res = call('core_user_create_users', users = [values])
        if type(res) == list:
            self.id  = res[0].get('id')
            
    def update(self, field=None):
        "Upadte user data on moodle site"
        if field:
            values = {"id": self.id, field: self.__dict__.get(field)}
        else:
            values = self.__dict__
        r = call('core_user_update_users', users = [values])
    
    def get_by_field(self, field='username'):
        "Create new user if it does not exist, otherwise update data"
        res = call('core_user_get_users_by_field', field = field, values = [self.__dict__.get(field)])
        if (type(res) == list) and len(res) > 0:
            self.__dict__.update(res[0])
            return self
        else:
            return None

    def create_or_get_id(self, field='username'):
        "Get Moodle id of the user or create one if it does not exists."
        if not self.get_by_field(field):
            self.create()

    def enroll(self, roleid=5):
        "Enroll users in courses with specific role"
        if len(self.courses)<=0:
            return None
        enrolments = []
        for course in self.courses:
            enrolments.append({'roleid': roleid, 'userid': self.id, 'courseid': course.id})
        r = call('enrol_manual_enrol_users', enrolments = enrolments)
        return r

    def enrolments(self, m_courses):
        "Get moodle courses, the user has to enroll"
        self.courses = []
        for idnumber in self.course_idnumbers:
            course = m_courses.by_idnumber(idnumber)
            if course:
                self.courses.append(course)
        return self.courses


class Attendance():
    """出勤的类.

    示例:
    >>> Attendance(courseid=1, name="上课考勤", intro="上课考勤", groupmode=1)
    groupmode= int(0 - no groups, 1 - separate groups, 2 - visible groups)
    """
    def __init__(self, **data):
        self.__dict__.update(data)

    def create(self):
        "Create this attendance on moodle"
        res = call('mod_attendance_add_attendance', courseid=self.__dict__.get('courseid'), name=self.__dict__.get('name'), intro=self.__dict__.get('intro'), groupmode=self.__dict__.get('groupmode'))
        if type(res) == dict:
            self.id = res.get('attendanceid')
    
    def get_by_field(self, field='name'):
        "Get attendance whether it's exist" 
        res = call('mod_attendance_get_course_attendances', courseid=self.__dict__.get('courseid')) # 获得群组
        if (type(res) == list) and len(res) > 0:
            for item in res: 
                if item.get(field) == self.__dict__.get(field):  # 根据idnumber判断群组是否存在
                    self.id  = item.get('id')
                    self.__dict__.update(item)
                    return self     # 返回群组信息
            return None
        else:
            return None
    
    def create_or_get_id(self, field='name'):
        "Get Moodle id of the attendance or create one if it does not exists."
        if not self.get_by_field(field):
            self.create()
    
    def add_session(self, sessiontime, duration, groupid, description):
        "Add session on this attendance on moodle"
        res = call('mod_attendance_add_session', attendanceid=self.id, sessiontime=sessiontime, duration=duration, groupid=groupid, description=description)
        if type(res) == dict:
            return res['sessionid']
        return None

class CourseList():
    """Class for list of all courses in Moodle and order them by id and idnumber."""
    def __init__(self):
        # TODO fullname atribute is filtered
        # (no <span class="multilang" lang="sl">)
        courses_data = call('core_course_get_courses')
        self.courses = []
        for data in courses_data:
            self.courses.append(Course(**data))
        self.id_dict = {}
        self.idnumber_dict = {}
        for course in self.courses:
            self.id_dict[course.id] = course
            if course.idnumber:
                self.idnumber_dict[course.idnumber] = course
    
    def __getitem__(self, key):
        if 0<= key < len(self.courses):
            return self.courses[key]
        else:
            raise IndexError
                
    def by_id(self, id):
        "Return course with given id."
        return self.id_dict.get(id)
    
    def by_idnumber(self, idnumber):
        "Course with given idnumber"
        return self.idnumber_dict.get(idnumber)
    
    def update_courses(self, courses_to_update, fields):
        "Update a list of courses in one go."
        if not ('id' in fields):
            fields.append('id')
        courses = [{k: c.__dict__[k] for k in fields} for c in courses_to_update]
        return call("core_course_update_courses", 
             courses = courses)


class Cathegory():
    pass

class Enrolments():
    pass