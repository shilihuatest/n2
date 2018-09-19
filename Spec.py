# -*- coding: utf-8 -*-
import sys,os

##console监控相关配置
#测试床ID
Test_Bad_Id ='112'
#测试设备ID
DUT_Id ='1'
#测试PC的ID
Terminal_Id = '112'
##是否保存测试数据到数据库,1表示保存，0表示不保存
setsql = 0
##软件版本
version = 'V22.1.1.7'
##硬件版本
model = 'N2'
##测试内容:开关机测试(区别soak和压力测试)
case = u'开关机'
##板子SN号
SN_1 = 'J00141'
##测试责任人
tester = u'张腾'
#数据库地址
host = '10.5.51.200'
#定义数据提交方式:'1'代表HTTP方式提交;'0'代表直接打开数据库方式提交（传统提交方式）
write_to_sql_flag = 1
#
SN =''
URL = 'http://13.0.0.1:3000/'
DUTIP = '13.0.0.1'
userName = 'admin'
userPwd ='admin'
PS_Check =['wisnuc-bootstra','minidlnad','smbd','appif']#########SSH进程检查
SSH_Ip='13.0.0.1'
SSH_Port='22'
SSH_Loginname='admin'
SSH_Password='admin'
SSH_until_tag='$'
basic_log_path = 'D:\\03TestResoultLOG\\RIDERun\\CurrentResoultLog\\'
loop_times={'Reboot':300,'cycle_shutdown':300,'suiji_shutdown':300,'MixShutDownButtonOn':3,'ButtonDownUp':600}
TEST_stage='DV'
test_mode=''
stop_when_neterr = 'True'#True or False
mkDirName='xiaoye'
adminName='admin' 
adminPwd='admin'
localdirPath_up=r'E:\\NAS_UP\\'
localdirPath_down=r'E:\\NAS_DOWN\\'
up_time = int(120)
#继电器信息
chacao = '3'
console_com = 'com3'
console_bound = '9600'
console = '1'
#机械手信息
AutoHand_com = 'com10'
AutoHand_bound = '9600'
#统计
stop_when_neterr = 'True'#False or True
