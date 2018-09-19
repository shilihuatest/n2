#coding=utf-8
import requests
import base64
import json
import os
from requests_toolbelt import MultipartEncoder
import hashlib
import paramiko
import Spec
import logging
from time import ctime,sleep
import time
import Public_Library
import threading
import random
##import paramiko
from threading import Thread

class NAS_Switch_case:
    def __init__(self):        
        #定义log输出格式,此log在robot控制台输出
        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',datefmt='%d %b %Y %H:%M:%S')
        #导入配置文件数据,配置文件根据测试环境,测试项目和测试任务手动变更
        self.basic_log_path = Spec.basic_log_path
        self.model = Spec.model
        self.version = Spec.version
        self.TEST_stage = str(Spec.TEST_stage)
        self.loop_times = Spec.loop_times
        self.test_mode = Spec.test_mode
        os.chdir(self.basic_log_path)
        self.stop_when_neterr = str(Spec.stop_when_neterr)
        self.publicObj = Public_Library.Public_Library()
        self.URL = Spec.URL
        self.userName = Spec.userName
        self.userPwd = Spec.userPwd
        self.adminName=Spec.adminName
        self.adminPwd=Spec.adminPwd
        self.mkDirName=Spec.mkDirName
        self.localdirPath_up=Spec.localdirPath_up
        self.localdirPath_down=Spec.localdirPath_down
        self.model = Spec.model
        self.version = Spec.version
        self.chacao = Spec.chacao
        self.console_com= Spec.console_com
        self.console_bound = Spec.console_bound
        self.console = Spec.console
        self.DUTIP = Spec.DUTIP
        self.up_time = Spec.up_time
        self.SSH_Ip = Spec.SSH_Ip
        self.SSH_Port = Spec.SSH_Port
        self.SSH_Loginname = Spec.SSH_Loginname
        self.SSH_Password = Spec.SSH_Password
        self.PS_Check = Spec.PS_Check
        self.SSH_until_tag = Spec.SSH_until_tag
        self.AutoHand_com = Spec.AutoHand_com
        self.AutoHand_bound = Spec.AutoHand_bound
        self.stop_when_neterr = str(Spec.stop_when_neterr)
        self.sn = Spec.SN
        
#****************************************  Case  ************************************************************
    def Reboot(self):
        """
        软件重启
        """
        log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        log_file = self.basic_log_path + "%s_Reboot_" % self.model + self.version + "_" + log_time + ".txt"
        logging.info(log_file)
        f = open(log_file, 'w')
        user_uuid = self.publicObj.getUserUuid(self.URL,self.userName,f)
        if user_uuid =='':
            msg = u'用户%s的user_uuid获取失败,测试暂停' % self.userName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            msg = u'用户%s的【user_uuid:%s】' % (self.userName,user_uuid)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            try:
                loop_index = 1
                Pass_times = 0
                Fail_times = 0
                case_start_time = int(time.time())
                linkStatus = ''
                shutdown_status = ''
                SSH_Check = ''
                yewu = ''                
                while(loop_index <= int(Spec.loop_times['Reboot'])):
                    
                    msg = u'####################这是第 %s次(%s,%s)轮询基本业务并过程中重启#####################' % (loop_index, self.model, self.version)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    msg = u'####################  重启前检查链路是否通畅  #####################'
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    linkStatus = self.publicObj.linkStatus_Check(self.DUTIP,f)
                    if linkStatus == 'FAIL':
                        msg = u'####################重启前的服务器链路不通，fail#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'####################重启前的服务器链路已检查为通畅，现在执行【业务中-重启】测试#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        threads = []
                        t1 = threading.Thread(target=self.Reboot_Button,args=(loop_index,f))
                        threads.append(t1)
                        t2 = threading.Thread(target=self.Services,args=(user_uuid,loop_index,f))
                        threads.append(t2)
                        t2.setDaemon(True)
                        for t in [t1,t2]:
                            t.start()
                        t1.join()
                        msg = u'the【 %s th 】script is over(%s), but the operation may still be in progress\n\n\n' %(loop_index,ctime())
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        #检查reboot动作状态
                        time.sleep(10)
                        msg = u'####################检查reboot动作后系统链路是否断开#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        shutdown_status = self.publicObj.check_shutdown(Spec.DUTIP)
                        #检查重启后系统状态
                        self.publicObj.show_log(u'..............系统正在重启中.................')
                        time.sleep(self.up_time)
                        msg = u'####################检查up_%s(s)后系统链路是否恢复连接#####################'%self.up_time
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        linkStatus1 = self.publicObj.linkStatus_Check(self.DUTIP,f)
                        if linkStatus1 == 'FAIL':
                            msg = u'####################设备up后系统链路仍然不通，fail#####################' 
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'####################设备up后系统链路恢复，success#####################' 
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        #检查系统重启后的SSH
                        msg =u'准备检查系统进程状态'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        SSH_Check=self.publicObj.SSH_Check(self.SSH_Ip,self.SSH_Port,self.SSH_Loginname,self.SSH_Password,self.ps_check1,self.ps_check2,self.ps_check3,self.ps_check4,self.SSH_until_tag,f)
                        msg = u'####################这是第 %s次【Reboot后】检查基本业务#####################' % loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        yewu=self.Services(user_uuid,loop_index,f)
                        print yewu
                        if yewu!='SUCCESS':
                            msg = u'系统第%s 【Reboot后基本业务检查】【失败!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'系统第%s 【Reboot后基本业务检查】【成功!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        print [linkStatus,shutdown_status,SSH_Check,yewu]
                    if linkStatus == 'FAIL' or shutdown_status == 'FAIL' or SSH_Check == 'FAIL' or yewu == 'FAIL':
                        msg =u'以上测试步骤中存在【部分业务出现异常，需要故障排查,可参考以下错误模块报错信息！！！！！！！！！！】\n '
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'FAIL'#######FAIL标记位
                        if linkStatus == 'FAIL':
                            msg =u'参考：重启前的链路检测fail---ping DUT_IP 不通\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if shutdown_status == 'FAIL':
                            msg =u'参考：检测到reboot后系统并没有重新启动，请检查----ping DUT_IP 通(应该为ping 不通)!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if SSH_Check == 'FAIL':
                            msg =u'参考：有进程检查失败，请检查前面最近历史ssh进程检查LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if yewu == 'FAIL':
                            msg =u'参考：有基本业务操作失败，请检查前面最近历史业务操作LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg =u'第%s次Reboot 成功，且重启后各业务检查都OK \n '%loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'PASS'######PASS标记位
                    result = self.publicObj.conn_status_statics(f,self.sn, loop_index, Pass_times, Fail_times, self.stop_when_neterr,\
                                                                'Reboot','PASS', self.console,self.console_com,\
                                                                self.console_bound,self.up_time,matchobj,self.AutoHand_com,self.AutoHand_bound)
                    Pass_times = result[0]
                    Fail_times = result[1]
                    finish_tag = result[2]
                    if finish_tag == 'end':
                        return 'FAIL'
                    else:
                        print Pass_times
                        print Fail_times
    ##                    runtime_s=int(time.time()-case_start_time)                
                    loop_index = loop_index + 1
                self.publicObj.show_log(u'统计结果')
                self.publicObj.statics_result(self.model, self.version, loop_index - 1, f, self.sn, Pass_times, Fail_times,'Reboot')
            finally:
                f.close()
        
    def cycle_shutdown(self):
        """
        周期断电(配合机械手开机)
        """
        log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        log_file=self.basic_log_path + "%s_CycleShutdown_" % self.model + self.version + "_" + log_time + ".txt"
        logging.info(log_file)
        f = open(log_file, 'w')
        user_uuid = self.publicObj.getUserUuid(self.URL,self.userName,f)
        if user_uuid =='':
            msg = u'用户%s的user_uuid获取失败' % self.userName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            msg = u'用户%s的【user_uuid:%s】' % (self.userName,user_uuid)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            try:
                loop_index = 1
                Pass_times = 0
                Fail_times = 0
                case_start_time = int(time.time())
                linkStatus = ''
                shutdown_status = ''
                SSH_Check = ''
                yewu = ''   
                while (loop_index <= int(self.loop_times['cycle_shutdown'])):
                    msg = u'####################这是第 %s次(%s,%s)轮询基本业务并过程中重启#####################' % (loop_index, self.model, self.version)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    linkStatus = self.publicObj.linkStatus_Check(self.DUTIP,f)
                    if linkStatus == 'FAIL':
                        msg = u'####################服务器链路检查不通，fail#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'####################正在执行【业务中-断电】测试#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        threads = []
                        t1 = threading.Thread(target=self.publicObj.zhouqi,args=(self.console,self.console_com,self.console_bound))
                        threads.append(t1)
                        t2 = threading.Thread(target=self.Services,args=(user_uuid,loop_index,f))
                        t2.setDaemon(True)
                        threads.append(t2)
                        for t in [t1,t2]:
                            t.start()
                        for t in [t1,t2]:
                            t.join()
                        msg = u'the【 %s th 】script is over(%s), but the operation may still be in progress\n\n\n' %(loop_index,ctime())
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        #检查继电器断电动作状态
                        shutdown_status = self.publicObj.check_shutdown(Spec.DUTIP)
                        #机械手开机
                        self.publicObj.AutoHand_DownUp(self.AutoHand_com, self.AutoHand_bound)
                        #检查重启后系统状态
                        self.publicObj.show_log(u'..............机械手已操作开机，系统正在重启中.................')
                        time.sleep(self.up_time)
                        #检查系统重启后的SSH
                        msg =u'准备检查系统进程状态'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        SSH_Check=self.publicObj.SSH_Check(self.SSH_Ip,self.SSH_Port,self.SSH_Loginname,self.SSH_Password,self.SSH_until_tag,self.PS_Check,f)
                        msg = u'####################这是第 %s次【cycle_shutdown后】检查基本业务#####################' % loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        yewu=self.Services(user_uuid,loop_index,f)
                        if yewu!='SUCCESS':
                            msg = u'系统第%s 【cycle_shutdown后基本业务检查】【失败!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'系统第%s 【cycle_shutdown后基本业务检查】【成功!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    msg =u'第%s次测试结果如下：linkStatus：%s,shutdown_status:%s,SSH_Check:%s,yewu:%s'%(loop_index,linkStatus,shutdown_status,SSH_Check,yewu)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    if linkStatus == 'FAIL' or shutdown_status == 'FAIL' or SSH_Check == 'FAIL' or yewu == 'FAIL':
                        msg =u'以上测试步骤中存在【部分业务出现异常，需要故障排查,可参考以下错误模块报错信息！！！！！！！！！！】\n '
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'FAIL'#######FAIL标记位
                        if linkStatus == 'FAIL':
                            msg =u'参考：重启前的链路检测fail---ping DUT_IP 不通\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if shutdown_status == 'FAIL':
                            msg =u'参考：检测到cycle_shutdown后系统并没有重新启动，请检查----ping DUT_IP 通(应该为ping 不通)!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if SSH_Check == 'FAIL':
                            msg =u'参考：有进程检查失败，请检查前面最近历史ssh进程检查LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if yewu == 'FAIL':
                            msg =u'参考：有基本业务操作失败，请检查前面最近历史业务操作LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg =u'第%s次cycle_shutdown 成功，且重启后各业务检查都OK \n '%loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'PASS'######PASS标记位
                    result = self.publicObj.conn_status_statics(f,self.sn, loop_index, Pass_times, Fail_times, self.stop_when_neterr,\
                                                                'cycle_shutdown','PASS', self.console,self.console_com,\
                                                                self.console_bound,self.up_time,matchobj,self.AutoHand_com,self.AutoHand_bound)
                    Pass_times = result[0]
                    Fail_times = result[1]
                    finish_tag = result[2]
                    if finish_tag == 'end':
                        return 'FAIL'
                    else:
                        print Pass_times
                        print Fail_times
##                    runtime_s=int(time.time()-case_start_time)                
                    loop_index = loop_index + 1
                self.publicObj.show_log(u'统计结果')
                self.publicObj.statics_result(self.model, self.version, loop_index - 1, f, self.sn, Pass_times, Fail_times,'cycle_shutdown')
            finally:
                f.close()

    def suiji_shutdown(self):
        """
        随机断电
        """
        log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        log_file=self.basic_log_path + "%s_suiji_shutdown_" % self.model + self.version + "_" + log_time + ".txt"
        logging.info(log_file)
        f = open(log_file, 'w')
        user_uuid = self.publicObj.getUserUuid(self.URL,self.userName,f)
        if user_uuid =='':
            msg = u'用户%s的user_uuid获取失败' % self.userName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            msg = u'用户%s的【user_uuid:%s】' % (self.userName,user_uuid)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            try:
                loop_index = 1
                Pass_times = 0
                Fail_times = 0
                case_start_time = int(time.time())
                linkStatus = ''
                shutdown_status = ''
                SSH_Check = ''
                yewu = ''   
                while (loop_index <= int(self.loop_times['suiji_shutdown'])):
                    msg = u'####################这是第 %s次(%s,%s)轮询基本业务并过程中重启#####################' % (loop_index, self.model, self.version)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    linkStatus = self.publicObj.linkStatus_Check(self.DUTIP,f)
                    if linkStatus == 'FAIL':
                        msg = u'####################服务器链路检查不通，fail#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'####################正在执行【业务中-断电】测试#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        threads = []
                        t1 = threading.Thread(target=self.publicObj.suiji,args=(self.console,self.console_com,self.console_bound))
                        threads.append(t1)
                        t2 = threading.Thread(target=self.Services,args=(user_uuid,loop_index,f))
                        t2.setDaemon(True)
                        threads.append(t2)
                        for t in [t1,t2]:
                            t.start()
                        for t in [t1,t2]:
                            t.join()
                        msg = u'the【 %s th 】script is over(%s), but the operation may still be in progress\n\n\n' %(loop_index,ctime())
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        #检查继电器断电动作状态
                        shutdown_status = self.publicObj.check_shutdown(Spec.DUTIP)
                        #机械手开机
                        self.publicObj.AutoHand_DownUp(self.AutoHand_com, self.AutoHand_bound)
                        #检查重启后系统状态
                        self.publicObj.show_log(u'..............机械手已操作开机，系统正在重启中.................')
                        time.sleep(self.up_time)
                        #检查系统重启后的SSH
                        msg =u'准备检查系统进程状态'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        SSH_Check=self.publicObj.SSH_Check(self.SSH_Ip,self.SSH_Port,self.SSH_Loginname,self.SSH_Password,self.ps_check1,self.ps_check2,self.ps_check3,self.SSH_until_tag,f)
                        msg = u'####################这是第 %s次【suiji_shutdown后】检查基本业务#####################' % loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        yewu=self.Services(user_uuid,loop_index,f)
                        if yewu!='SUCCESS':
                            msg = u'系统第%s 【suiji_shutdown后基本业务检查】【失败!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'系统第%s 【suiji_shutdown后基本业务检查】【成功!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    print [linkStatus,shutdown_status,SSH_Check,yewu]
                    if linkStatus == 'FAIL' or shutdown_status == 'FAIL' or SSH_Check == 'FAIL' or yewu == 'FAIL':
                        msg =u'以上测试步骤中存在【部分业务出现异常，需要故障排查,可参考以下错误模块报错信息！！！！！！！！！！】\n '
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'FAIL'#######FAIL标记位
                        if linkStatus == 'FAIL':
                            msg =u'参考：重启前的链路检测fail---ping DUT_IP 不通\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if shutdown_status == 'FAIL':
                            msg =u'参考：检测到suiji_shutdown后系统并没有重新启动，请检查----ping DUT_IP 通(应该为ping 不通)!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if SSH_Check == 'FAIL':
                            msg =u'参考：有进程检查失败，请检查前面最近历史ssh进程检查LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if yewu == 'FAIL':
                            msg =u'参考：有基本业务操作失败，请检查前面最近历史业务操作LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg =u'第%s次suiji_shutdown 成功，且重启后各业务检查都OK \n '%loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'PASS'######PASS标记位
                    result = self.publicObj.conn_status_statics(f,self.sn, loop_index, Pass_times, Fail_times, self.stop_when_neterr,\
                                                                'cycle_shutdown','PASS', self.console,self.console_com,\
                                                                self.console_bound,self.up_time,matchobj,self.AutoHand_com,self.AutoHand_bound)
                    Pass_times = result[0]
                    Fail_times = result[1]
                    finish_tag = result[2]
                    if finish_tag == 'end':
                        return 'FAIL'
                    else:
                        print Pass_times
                        print Fail_times
##                    runtime_s=int(time.time()-case_start_time)                
                    loop_index = loop_index + 1
                self.publicObj.show_log(u'统计结果')
                self.publicObj.statics_result(self.model, self.version, loop_index - 1, f, self.sn, Pass_times, Fail_times,'suiji_shutdown')
            finally:
                f.close()

            
    def MixShutDownButtonOn(self):
        """
        软件Shutdown +机械手On
        """
        log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        log_file=self.basic_log_path + "%s_MixShutDownButtonOn_" % self.model + self.version + "_" + log_time + ".txt"
        logging.info(log_file)
        f = open(log_file, 'w')
        user_uuid = self.publicObj.getUserUuid(self.URL,self.userName,f)
        if user_uuid =='':
            msg = u'用户%s的user_uuid获取失败' % self.userName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            msg = u'用户%s的【user_uuid:%s】' % (self.userName,user_uuid)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            try:
                loop_index = 1
                Pass_times = 0
                Fail_times = 0
                case_start_time = int(time.time())
                linkStatus = ''
                shutdown_status = ''
                SSH_Check = ''
                yewu = ''    
                while (loop_index <= int(self.loop_times['MixShutDownButtonOn'])):
                    msg = u'####################这是第 %s次(%s,%s)轮询基本业务并过程中重启#####################' % (loop_index, self.model, self.version)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    linkStatus = self.publicObj.linkStatus_Check(self.DUTIP,f)
                    if linkStatus == 'FAIL':
                        msg = u'####################服务器链路检查不通，fail#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'####################正在执行【业务中shutdown】测试#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        threads = []
                        t1 = threading.Thread(target=self.Reboot_Button,args=(loop_index,f))
                        threads.append(t1)
                        t2 = threading.Thread(target=self.Services,args=(user_uuid,loop_index,f))
                        t2.setDaemon(True)
                        threads.append(t2)
                        for t in [t1,t2]:
                            t.start()
                        for t in [t1,t2]:
                            t.join()
                        msg = u'the【 %s th 】script is over(%s), but the operation may still be in progress\n\n\n' %(loop_index,ctime())
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        time.sleep(10)
                       #检查shutdown动作状态
                        shutdown_status = self.publicObj.check_shutdown(Spec.DUTIP)
                        self.publicObj.show_log(u'调用机械手按键启动【Button_ON】')
                        #机械手开机
                        self.publicObj.AutoHand_DownUp(self.AutoHand_com,self.AutoHand_bound)
                        self.publicObj.show_log(u'系统正在启动中....')
                        time.sleep(self.up_time)
                        #检查系统重启后的SSH
                        #检查系统重启后的SSH
                        msg =u'准备检查系统进程状态'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        SSH_Check=self.publicObj.SSH_Check(self.SSH_Ip,self.SSH_Port,self.SSH_Loginname,self.SSH_Password,self.ps_check1,self.ps_check2,self.ps_check3,self.SSH_until_tag,f)
                        msg = u'####################这是第 %s次【ShutDown+ButtonOn后】检查基本业务#####################' % loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        yewu=self.Services(user_uuid,loop_index,f)
                        print yewu
                        if yewu!='SUCCESS':
                            msg = u'系统第%s 【ShutDown+ButtonOn后基本业务检查】【失败!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'系统第%s 【ShutDown+ButtonOn后基本业务检查】【成功!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        print [linkStatus,shutdown_status,SSH_Check,yewu]
                    if linkStatus == 'FAIL' or shutdown_status == 'FAIL' or SSH_Check == 'FAIL' or yewu == 'FAIL':
                        msg =u'以上测试步骤中存在【部分业务出现异常，需要故障排查,可参考以下错误模块报错信息！！！！！！！！！！】\n '
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'FAIL'#######FAIL标记位
                        if linkStatus == 'FAIL':
                            msg =u'参考：shutdown前的链路检测fail---ping DUT_IP 不通\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if shutdown_status == 'FAIL':
                            msg =u'参考：检测到reboot后系统并没有重新启动，请检查----ping DUT_IP 通(应该为ping 不通)!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if SSH_Check == 'FAIL':
                            msg =u'参考：有进程检查失败，请检查前面最近历史ssh进程检查LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if yewu == 'FAIL':
                            msg =u'参考：有基本业务操作失败，请检查前面最近历史业务操作LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg =u'第%s次MixShutDownButtonOn 成功，且重启后各业务检查都OK \n '%loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'PASS'######PASS标记位
                    result = self.publicObj.conn_status_statics(f,self.sn, loop_index, Pass_times, Fail_times, self.stop_when_neterr,\
                                                                'MixShutDownButtonOn','PASS', self.console,self.console_com,\
                                                                self.console_bound,self.up_time,matchobj,self.AutoHand_com,self.AutoHand_bound)
                    Pass_times = result[0]
                    Fail_times = result[1]
                    finish_tag = result[2]
                    if finish_tag == 'end':
                        return 'FAIL'
                    else:
                        print Pass_times
                        print Fail_times
    ##                    runtime_s=int(time.time()-case_start_time)                
                    loop_index = loop_index + 1
                self.publicObj.show_log(u'统计结果')
                self.publicObj.statics_result(self.model, self.version, loop_index - 1, f, self.sn, Pass_times, Fail_times,'MixShutDownButtonOn')
            finally:
                f.close()

    def ButtonDownUp(self):
        """
        机械手DownUp
        """
        log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        log_file=self.basic_log_path + "%s_CycleShutdown_" % self.model + self.version + "_" + log_time + ".txt"
        logging.info(log_file)
        f = open(log_file, 'w')
        user_uuid = '0909'#self.publicObj.GetUserUuid(self.URL,self.userName)
        if user_uuid =='':
            msg = u'用户%s的user_uuid获取失败' % self.userName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            msg = u'用户%s的【user_uuid:%s】' % (self.userName,user_uuid)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            try:
                loop_index = 1
                Pass_times = 0
                Fail_times = 0
                case_start_time = int(time.time())
                linkStatus = ''
                shutdown_status = ''
                SSH_Check = ''
                yewu = ''       
                while (loop_index <= int(self.loop_times['Reboot'])):
                    msg = u'####################这是第 %s次(%s,%s)轮询基本业务过程中按键关机和开机#####################' % (loop_index, self.model, self.version)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    linkStatus = self.publicObj.linkStatus_Check(self.DUTIP,f)
                    if linkStatus == 'FAIL':
                        msg = u'####################服务器链路检查不通，fail#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'####################正在执行【业务中ButtonOff】测试#####################' 
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        threads = []
                        t1 = threading.Thread(target=self.publicObj.AutoHand_DownUp,args=(self.AutoHand_com,self.AutoHand_bound))
                        threads.append(t1)
                        t2 = threading.Thread(target=self.Services,args=(user_uuid,loop_index,f))
                        t2.setDaemon(True)
                        threads.append(t2)
                        for t in [t1,t2]:
                            t.start()
                        for t in [t1,t2]:
                            t.join()
                        msg = u'the【 %s th 】script is over(%s), but the operation may still be in progress\n\n\n' %(loop_index,ctime())
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        #检查shutdown动作状态
                        shutdown_status = self.publicObj.check_shutdown(Spec.DUTIP)
                        self.publicObj.show_log(u'调用机械手按键开机')
                        self.publicObj.AutoHand_DownUp(self.AutoHand_com,self.AutoHand_bound)
                        self.publicObj.show_log(u'系统正在启动中....')
                        time.sleep(self.up_time)
                        #检查系统重启后的SSH
                        msg =u'准备检查系统进程状态'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        SSH_Check=self.publicObj.SSH_Check(self.SSH_Ip,self.SSH_Port,self.SSH_Loginname,self.SSH_Password,self.ps_check1,self.ps_check2,self.ps_check3,self.SSH_until_tag,f)
                        msg = u'####################这是第 %s次【ButtonOff+ButtonOn后】检查基本业务#####################' % loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        yewu=self.Services(user_uuid,loop_index,f)
                        print yewu
                        if yewu!='SUCCESS':
                            msg = u'系统第%s 【ButtonOff+ButtonOn后基本业务检查】【失败!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        else:
                            msg = u'系统第%s 【ButtonOff+ButtonOn后基本业务检查】【成功!!】'%loop_index
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        print [linkStatus,shutdown_status,SSH_Check,yewu]
                    if linkStatus == 'FAIL' or shutdown_status == 'FAIL' or SSH_Check == 'FAIL' or yewu == 'FAIL':
                        msg =u'以上测试步骤中存在【部分业务出现异常，需要故障排查,可参考以下错误模块报错信息！！！！！！！！！！】\n '
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'FAIL'#######FAIL标记位
                        if linkStatus == 'FAIL':
                            msg =u'参考：shutdown前的链路检测fail---ping DUT_IP 不通\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if shutdown_status == 'FAIL':
                            msg =u'参考：检测到【ButtonOn】后系统并没有重新启动，请检查----ping DUT_IP 通(应该为ping 不通)!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if SSH_Check == 'FAIL':
                            msg =u'参考：有进程检查失败，请检查前面最近历史ssh进程检查LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                        if yewu == 'FAIL':
                            msg =u'参考：有基本业务操作失败，请检查前面最近历史业务操作LOG!!!\n '
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg =u'第%s次ButtonDownUp 成功，且重启后各业务检查都OK \n '%loop_index
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        matchobj = 'PASS'######PASS标记位
                    result = self.publicObj.conn_status_statics(f,self.sn, loop_index, Pass_times, Fail_times, self.stop_when_neterr,\
                                                                'ButtonDownUp','PASS', self.console,self.console_com,\
                                                                self.console_bound,self.up_time,matchobj,self.AutoHand_com,self.AutoHand_bound)
                    Pass_times = result[0]
                    Fail_times = result[1]
                    finish_tag = result[2]
                    if finish_tag == 'end':
                        return 'FAIL'
                    else:
                        print Pass_times
                        print Fail_times
    ##                    runtime_s=int(time.time()-case_start_time)                
                    loop_index = loop_index + 1
                self.publicObj.show_log(u'统计结果')
                self.publicObj.statics_result(self.model, self.version, loop_index - 1, f, self.sn, Pass_times, Fail_times,'ButtonDownUp')
            finally:
                f.close()
            
#*************************************************基础业务*************************************************************************
    def Reboot_Button(self,loop_index,f):
        t= random.randint(2,6)
        msg =u'随机等待业务运行时间是%s'%t
        self.publicObj.show_log(msg)
        self.publicObj.log_write(msg.encode("gbk"), f)
        timedate=requests.get(self.URL+'control/timedate')
        time.status_code = timedate.status_code
        User_Info = timedate.json()
        msg = u'reboot_时间管理接口get成功:%s'%User_Info
        self.publicObj.show_log(msg)
        self.publicObj.log_write(msg.encode("gbk"), f)
        if time.status_code==200:
            headers = {'Accept': 'application/json','Content-Type': 'application/json','Connection': 'close'}
            data1 = json.dumps({"state":"reboot"})######将字典转化为json格式
            reboot=requests.patch(self.URL+'boot',headers=headers,data=data1)
            status_code_reboot = reboot.status_code
            msg=u'reboot_status_code:%s'%status_code_reboot
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            if status_code_reboot==200:
                msg =u'第 %s次【重启Button】操作success'%loop_index
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
            else:
                logging.info(status_code_reboot)
                msg =u'第 %s次【重启Button】操作FAIL,status_code:%s'%(loop_index,status_code_reboot)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                return 'FAIL'            
        else:
            print u'时间管理接口get失败%s'%status_code
            msg=u'reboot前的时间管理接口get失败%s'%time.status_code
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
            
    def shutdown(self,f):
        loop_index = 1
        Pass_times = 0
        FAIL_times = 0
        timedate=requests.get(self.URL+'control/timedate')        
        status_code = timedate.status_code
        User_Info = timedate.json()
        print User_Info
        msg=u'时间管理接口get成功%s'%status_code
        self.publicObj.show_log(msg)
        self.publicObj.log_write(msg.encode("gbk"), f)
        if status_code==200:
            headers = {'Accept': 'application/json','Content-Type': 'application/json','Connection': 'close'}
            data1 = json.dumps({"state":"poweroff"})######将字典转化为json格式
            shutdown=requests.patch(self.URL+'boot',headers=headers,data=data1)
            status_code_shutdown = shutdown.status_code
            logging.info(status_code_shutdown)
            if status_code_shutdown==200:
                print "shutdown success"
                msg=u'shutdown success:%s'%(status_code_shutdown)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                return 'SUCCESS'            
            else:
                msg=u'shutdown FAIL:%s'%(status_code_shutdown)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                return 'FAIL'           
        else:
            print u'时间管理接口get失败%s'%(status_code)
            msg=u'时间管理接口get失败:%s'%(status_code)
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        
    def creatUser(self,f):
        #用管理员admin账户创建普通账户user，user运行基本业务（包括创建文件夹、重命名文件夹、上传下载整个文件夹）
        admin_uuid=self.publicObj.GetUserUuid(self.URL,self.adminName)
        if admin_uuid == '':
            msg = u'用户%s不存在，请检查网络是否连接及用户是否存在' %self.adminName
            self.publicObj.show_log(msg)
            self.publicObj.log_write(msg.encode("gbk"), f)
            return 'FAIL'
        else:
            admin_tokenInfo = self.publicObj.getToken(admin_uuid,self.adminPwd,self.URL)#return [statusCode,token,tokenType]
            admin_tokenStatus = admin_tokenInfo[0]
            if admin_tokenStatus != 200:
                msg = u'用户%s鉴权失败，请检查密码%s是否正确' %(self.adminName,self.adminPwd)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                return 'FAIL'
            else:
                admin_Token_headers = self.publicObj.Token_headers(admin_tokenInfo[2],admin_tokenInfo[1])
                msg = u'管理员%s的Token_headers：%s' %(self.adminName,admin_Token_headers)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                creatUserInfo=self.publicObj.CreatUser(self.userName,self.userPwd,admin_Token_headers,self.URL)#return [creat_user.status_code,creat_user.json()]
                creat_user_status_code=creatUserInfo[0]
                if creat_user_status_code!=200:
                    msg=u'创建新用户失败,creat_userStatus_code:%s 服务器回应信息:%s'%(creatUserInfo[0],creatUserInfo[1])
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    return 'FAIL'                    
                else:
                    msg=u'创建新用户成功，用户名:%s 密码:%s'%(self.userName,self.userPwd)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    user_uuid=self.publicObj.GetUserUuid(self.URL,self.userName)
                    if user_uuid=='':
                        msg = u'用户%s不存在，请检查网络是否连接及用户是否存在' %self.userName
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        return 'FAIL'
                    else:
                        msg=u'新用户%s的user_uuid:%s'%(self.userName,user_uuid)
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        return user_uuid
    def Services(self,user_uuid,loop_index,f):
        try:
##            user_uuid = self.publicObj.getUserUuid(self.URL,self.userName,f)
##            print 'user_uuid=%s'%user_uuid
            user_tokenInfo = self.publicObj.getToken(user_uuid,self.userPwd,self.URL,f)#return [statusCode,token,tokenType]
            user_tokenStatus = user_tokenInfo[0]
            if user_tokenStatus != 200:
                msg = u'用户%s鉴权失败，请检查密码%s是否正确' %(self.userName,self.userPwd)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                return 'FAIL'
            else:
                msg = u'用户%s鉴权成功' %self.userName
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                user_Token_headers = self.publicObj.tokenHeaders(user_tokenInfo[2],user_tokenInfo[1])
                msg = u'用户%s访问服务器时的user_Token_headers：%s' %(self.userName,user_Token_headers)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                driveUuid = self.publicObj.getDrives(self.URL,user_Token_headers,'private',f)
                if driveUuid == '':
                    msg = u'用户%s【没有private drive】，请确认！' %self.userName
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    return 'FAIL'
                else:
                    msg = u'用户%s【private】对应的【driveUUid】是：%s' %(self.userName,driveUuid)
                    self.publicObj.show_log(msg)
                    self.publicObj.log_write(msg.encode("gbk"), f)
                    isExist=self.publicObj.queryFileByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory')#查询并删除上一轮中断操作后未删除文件夹
                    if isExist == 'Y':
                        msg = u'我的文件夹里面存在待创建文件夹，准备删除'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        dirInfo = self.publicObj.getFileInfoByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory',f)
                        dirUuid = dirInfo[1]['uuid']
                        removeInfo= self.publicObj.removeFileByHttp(self.URL,driveUuid,driveUuid,dirUuid,self.mkDirName,user_Token_headers,f)
                        if removeInfo[0] != 200:
                            msg = u'【删除】系统遗留文件夹%s【失败】,服务器返回%s！' %(self.mkDirName,removeInfo[0])
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                            return 'FAIL'
                        else:
                            msg = u'【删除】系统遗留文件夹%s【成功】！\n\n ' %(self.mkDirName)
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                    else:
                        msg = u'【原我的文件】里面不存在待创建文件夹，准备新创建'
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                    dirInfo = self.publicObj.mkDirByHttp(self.URL,driveUuid,driveUuid,self.mkDirName,user_Token_headers,f)
                    if dirInfo[0] != 200:
                        msg = u'在【我的文件】目录下【创建文件夹】%s【失败】！' %self.mkDirName
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        return 'FAIL'
                    else:
                        msg = u'在【我的文件】目录下【创建文件夹】%s【成功】！' %self.mkDirName
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg.encode("gbk"), f)
                        dirInfo = self.publicObj.getFileInfoByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory',f)
                        dirUuid = dirInfo[1]['uuid']
                        print 'dirUuid=%s'%dirUuid
                        uploadResult = self.publicObj.uploadDirByHttp(self.URL,user_Token_headers,self.localdirPath_up,driveUuid,dirUuid,f)###Uploader for files < 1G
                        if uploadResult == 'FAIL':
                            msg = u'在设备文件夹%s下【上传】PC本地文件夹%s中的文件【失败】！' %(self.mkDirName,self.localdirPath_up)
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                            return 'FAIL'
                        else:
                            msg = u'将PC本地文件夹%s中的文件【上传】到目标文件夹%s下【全部成功】，准备对上传的文件分别进行重命名！' %(self.localdirPath_up,self.mkDirName)
                            self.publicObj.log_write(msg.encode("gbk"), f)
                            self.publicObj.show_log(msg)
                            listBD = os.listdir(self.localdirPath_up)
                            numBD = len(listBD)
                            for BDi in range(numBD):
                                oldFileName = listBD[BDi]
                                newFileName = 'new'+oldFileName
                                renameInfo = self.publicObj.renameByHttp(self.URL,driveUuid,dirUuid,oldFileName,newFileName,user_Token_headers,f)
                                if renameInfo[0] != 200:
                                    msg = u'在目录%s下【重命名】文件%s【失败】！' %(self.mkDirName,oldFileName)
                                    self.publicObj.show_log(msg)
                                    self.publicObj.log_write(msg.encode("gbk"), f)
                                    return 'FAIL'
                                else:
                                    msg = u'在目录%s下【重命名】文件%s【成功】！' %(self.mkDirName,oldFileName)
                                    self.publicObj.show_log(msg)
                                    self.publicObj.log_write(msg.encode("gbk"), f)
                                    time.sleep(2)
                            msg = u'在目标文件夹%s下【重命名】里面文件【全部成功】,准备下载文件到本地！' %self.mkDirName
                            self.publicObj.show_log(msg)
                            self.publicObj.log_write(msg.encode("gbk"), f)
			    #downloadFile from NAS
                            downloadResult = self.publicObj.downloadDirByHttp(self.URL,user_Token_headers,self.localdirPath_down,driveUuid,dirUuid,f)
                            if downloadResult == 'FAIL':
                                msg = u'【下载】文件夹%s中文件到本地PC的文件夹%s中【失败】！' %(self.mkDirName,self.localdirPath_down)
                                self.publicObj.show_log(msg)
                                self.publicObj.log_write(msg.encode("gbk"), f)
                                return 'FAIL'
                            else:
                                msg = u'【下载】文件夹%s中文件到本地PC的文件夹%s中【成功】！' %(self.mkDirName,self.localdirPath_down)
                                self.publicObj.show_log(msg)
                                self.publicObj.log_write(msg.encode("gbk"), f)
            removeInfo= self.publicObj.removeFileByHttp(self.URL,driveUuid,driveUuid,dirUuid,self.mkDirName,user_Token_headers,f)
            if removeInfo[0] != 200:
                msg = u'【删除】文件夹%s【失败】,服务器返回%s！' %(self.mkDirName,removeInfo[0])
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                s = requests.session()
                s.keep_alive = False#关闭http连接
                return 'FAIL'
            else:
                msg = u'【删除】文件夹%s【成功】！\n\n ' %(self.mkDirName)
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                msg = u'####【第%s次】轮询基本【【业务全部成功】】####\n\n\n\n' %loop_index
                self.publicObj.show_log(msg)
                self.publicObj.log_write(msg.encode("gbk"), f)
                s = requests.session()
                s.keep_alive = False#关闭http连接
                return 'SUCCESS'      
        except Exception as e:
            msg1 = u'http服务存在问题，请检查线路或服务器服务是否出现问题：异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            self.publicObj.show_log(msg1)
            self.publicObj.log_write(msg1, f)
            self.publicObj.show_log(msg2)
            self.publicObj.log_write(msg2, f)
            return 'FAIL'
    def Services_interrupt(self,user_uuid,loop_index,f):
        try:
            user_tokenInfo = self.publicObj.getToken(user_uuid,self.userPwd,self.URL)#return [statusCode,token,tokenType]
            user_tokenStatus = user_tokenInfo[0]
            if user_tokenStatus != 200:
                return 'FAIL'############??????????????弹出dos窗口是否手动创建新用户Y/N
            else:
                user_Token_headers = self.publicObj.Token_headers(user_tokenInfo[2],user_tokenInfo[1])
                driveUuid = self.publicObj.getDrives(self.URL,user_Token_headers,'private')
                if driveUuid == '':
                    return 'FAIL'
                else:
                    isExist=self.publicObj.queryFileByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory')#查询并删除上一轮中断操作后未删除文件夹
                    if isExist == 'Y':
                        dirInfo = self.publicObj.getFileInfoByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory')
                        dirUuid = dirInfo[1]['uuid']
                        removeInfo= self.publicObj.removeFileByHttp(self.URL,driveUuid,driveUuid,dirUuid,self.mkDirName,user_Token_headers)
                        if removeInfo[0] != 200:
                            return 'FAIL'
                        else:
                            msg = u'【删除】系统遗留文件夹%s【成功】！\n\n ' %(self.mkDirName)
                            self.publicObj.show_log(msg)
                    else:
                        msg = u'【原我的文件】里面不存在待创建文件夹，准备新创建'
                        self.publicObj.show_log(msg)
                    dirInfo = self.publicObj.mkDirByHttp(self.URL,driveUuid,driveUuid,self.mkDirName,user_Token_headers)
                    if dirInfo[0] != 200:
                        return 'FAIL'
                    else:
                        dirInfo = self.publicObj.getFileInfoByHttp(self.URL,driveUuid,driveUuid,user_Token_headers,self.mkDirName,'directory')
                        dirUuid = dirInfo[1]['uuid']
                        uploadResult = self.publicObj.uploadDirByHttp(self.URL,user_Token_headers,self.localdirPath_up,driveUuid,dirUuid)
                        if uploadResult == 'FAIL':
                            return 'FAIL'
                        else:
                            listBD = os.listdir(self.localdirPath_up)
                            numBD = len(listBD)
                            for BDi in range(numBD-1):
                                oldFileName = listBD[BDi]
                                newFileName = 'new'+oldFileName
                                renameInfo = self.publicObj.renameByHttp(self.URL,driveUuid,dirUuid,oldFileName,newFileName,user_Token_headers)
                                if renameInfo[0] != 200:
                                    return 'FAIL'
                                else:
                                    time.sleep(2)
                            downloadResult = self.publicObj.downloadDirByHttp(self.URL,user_Token_headers,self.localdirPath_down,driveUuid,dirUuid)
                            if downloadResult == 'FAIL':
                                return 'FAIL'
                            else:
                                msg = u'【下载】目录%s中文件到文件夹%s【成功】！' %(self.mkDirName,self.localdirPath_down)
                                self.publicObj.show_log(msg)
            removeInfo= self.publicObj.removeFileByHttp(self.URL,driveUuid,driveUuid,dirUuid,self.mkDirName,user_Token_headers)
            if removeInfo[0] != 200:
                s = requests.session()
                s.keep_alive = False#关闭http连接
                return 'FAIL'
            else:
                return 'SUCCESS'      
        except Exception as e:
            msg1 = u'[service_interrupt]http服务存在问题，请检查线路或服务器服务是否出现问题：异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            self.publicObj.show_log(msg1)
            self.publicObj.log_write(msg1, f)
            self.publicObj.show_log(msg2)
            self.publicObj.log_write(msg2, f)
            return 'FAIL'
        
##ww=NAS_Switch_case()
##URL = 'http://13.0.0.1:3000/'
##userName ='admin'
##basic_log_path = 'D:\\03TestResoultLOG\\RIDERun\\CurrentResoultLog\\'
##log_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())###########删除to
##log_file = basic_log_path + "%s_Reboot_" + log_time + ".txt"
##logging.info(log_file)
##f = open(log_file, 'w')
##user_uuid = '1ac68288-43e6-413e-89c9-98583e16a859'############删除to此
##ww.Services('1',f)
##ww.Reboot_Button('1',f)

