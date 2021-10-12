# -*- coding: utf-8 -*-

from utils import get_cohort_by_idnumber, get_course_by_idnumber, moodle_user


if __name__ == "__main__":
    # ======示例使用======
    # 1, 根据教务系统的班级信息建立Moodle群组
    classnumber = '21030001' # 从教务系统获得班级编号名称并赋值
    classname = '信息学院软件工程2103级0001班'
    class_cohort = get_cohort_by_idnumber(classnumber, classname)

    # 2, 根据教务系统的班级参加的课程获得Moodle课程
    course_idnumber = 'A0010' # 可以在教务系统记录班级参加的课程及对应Moodle中的idnumber，并在此获得
    class_course = get_course_by_idnumber(course_idnumber) 

    # 3, 如果没有或得到课程，则提示错误
    if not hasattr(class_course, 'id'):
        raise SystemError('没有找到班级课程对应IDNUMBER的课程, \n请检查教务系统和Moodle课程信息')

    # 4, 根据步骤1-Moodle群组和步骤2-Moodle课程，建立同步课程小组
    roleid = 5 # 学员角色id为5
    class_enrolcohort = class_cohort.add_or_get_enrolcohort(class_course, roleid)

    # 5, 根据教务系统中学员的信息建立Moodle用户
    user = moodle_user({   # 此示例是对单个学生进行处理，可以遍历班级学生进行处理
            'mobile_phone':'13312345678',  
            'email':'zhangfeng@domain.com', 
            'name':'张峰', 
            'studentid':'2102000100011', 
            'institution':'信息学院', 
            'department':'软件工程系', 
        })
    user.create_or_get_id()

    # 6, 将建立的Moodle用户加入到步骤1-Moodle群组
    class_cohort.add_member(user)

    # 7, 输出执行结果
    print("==================================")
    print("学员：{}{}已在Moodle系统中建立，\n可以使用账号：{}，密码：{}".format(
        user.lastname, user.firstname, user.username, user.password
        ))
    print("学员已加入群组：{}，及课程：{}".format(
        class_cohort.name, class_course.fullname))
    print("可以到系统中的群组、课程、用户检查是否成功。")
    print("==================================")
