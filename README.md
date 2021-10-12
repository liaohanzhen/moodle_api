# moodle_api
外部系统调用Moodle接口同步建立群组、用户等

使用开发语言为Python，本项目链接：
>https://github.com/liaohanzhen/moodle_api_

# 使用说明
## 一、Moodle中的设置
### 1，安装支持课程群同步小组接口函数调用的插件
此插件可通过此链接下载：
>https://github.com/liaohanzhen/moodle-local_ws_enrolcohort

按Moodle的插件安装步骤，下载插件后安装，安装后可以支持课程群同步小组接口函数的调用

### 2，启用网络服务
要在外部系统调用Moodle完成如课程、群组、用户等的建立，则需要启用网络服务，其步骤可以通过Moodle菜单查看：
>系统管理：网站管理->服务器->网络服务->概览

主要的工作有：
1. 启用网络服务
2. 启用协议
3. 建立专用用户
4. 添加对外服务及函数
5. 为用户指定服务和创建令牌

### 2.1，启用网络服务
通过菜单：
>系统管理：网站管理->服务器->网络服务->概览

点击启用网络服务，勾选复选框，保存更改。

### 2.2，启用REST协议
通过菜单：
>系统管理：网站管理->服务器->网络服务->管理协议

确定REST协议是否启用，如果没有启用点击显示图标

### 2.3，添加用于实现网络服务的用户
通过菜单：
>系统管理：网站管理->用户->帐号->添加用户

添加用户，设置用户名称密码


### 2.4，添加对外服务及函数
>系统管理：网站管理->服务器->网络服务->对外服务

点击添加，并输入服务名称如：rest，并勾选启用，此服务名称确定了moodle api调用时的endpoint（如下代码中的rest则是服务名称）：

`ENDPOINT='/webservice/rest/server.php'`

在建立好的服务中，点击“函数”，在界面中点击“添加函数”，可以根据需要添加函数，如下为参考使用的函数（考勤需要安装考勤插件mod_attendance）：
-	core_cohort_add_cohort_members	增加成员到群组
-	core_cohort_create_cohorts	创建群组
-	core_cohort_delete_cohort_members	删除群组成员
-	core_cohort_get_cohorts	返回群组信息
-	core_cohort_get_cohort_members	返回群组成员
-	core_course_get_courses_by_field	根据字段值获得课程
-	core_group_create_groups	创建小组
-	core_group_get_course_groups	返回课程小组信息
-	core_user_create_users	创建用户
-	core_user_get_users_by_field	根据字段值获得用户
-	local_ws_enrolcohort_add_instance	创建课程群同步小组
-	local_ws_enrolcohort_get_instances	返回课程群同步小组
-	mod_attendance_add_attendance	创建考勤
-	mod_attendance_add_session	创建考勤安排
-	mod_attendance_get_course_attendances	获得课程的考勤


### 2.5，为用户指定服务和创建令牌
>系统管理：网站管理->服务器->网络服务->管理令牌

点击“创建令牌”，选择用户、服务，点击保存更改，将会生成相应的令牌，此令牌用于moodle_api中指定：

`KEY='xxxxxxxxx'`

## 二、开发调用
可将moodle_api.py、utils.py 放在教务系统中源代码指定位置
参考示例文件：main.py 进行业务处理

在正式环境中应用，代码实现考虑：
1. KEY、URL、ENDPOINT在教务系统中作为配置项目进行指定
2. 在Moodle中，维护好课程的IDNUMBER
3. 在教务系统中，维护好班级参加的课程IDNUMBER

实务应用场景及代码流程如下：
1. 在教务系统，选择班级, 执行学生同步到Moodle
2. 集成接口，获得班级基本信息和课程信息
3. 调用接口创建班级对应的群组，并在对应课程中创建群同步小组
4. 从教务系统，遍历学生信息，并逐个在Moodle建立对应用户及加入小组


