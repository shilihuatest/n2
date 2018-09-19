# -*- coding:utf-8 -*-
import itertools
import mimetools
import mimetypes
import urllib2
import os
import hashlib
import requests
import json
import logging
import paramiko
import base64
import xlutils
import serial
import shutil
import subprocess
import sys
import time
import re
from requests_toolbelt import MultipartEncoder

class Public_Library():
    ##输出log到控制台 
    def show_log(self, text):
        logging.info(text)

    ##输出log到日志文件
    def log_write(self, text, f):
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if isinstance(text, unicode):
            text = text.encode("utf-8")
        f.write(localtime)
        f.write(' ')
        f.write(text)
        f.write('\n')
    #获取登陆者的user_uuid
    def GetUserUuid(self,URL,username):
        try:
            User_URL = requests.get(URL+'users')
            status_code = User_URL.status_code
            User_Info = User_URL.json()
            for i in range(len(User_Info)):
                if User_Info[i]['username']==username:
                    user_uuid=User_Info[i]['uuid']
                    return user_uuid
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
            
    #登陆者的Login_headers
    def Login_headers(self,user_uuid,user_PASSword):
        user_info = user_uuid+':'+user_PASSword
        Token_Authorization = base64.b64encode(user_info)
        Login_headers = {'Authorization':''}
        Login_headers['Authorization']='Basic '+Token_Authorization
        msg = u'Login_headers: %s'%Login_headers
        logging.info(msg)
        return Login_headers

    #获取登陆者的token和token_type
    def getToken(self,userUuid,userPASSword,url):
        userInfo = userUuid+':'+userPASSword
        tokenAuthorization = base64.b64encode(userInfo)
        headers = {'Authorization':''}
        headers['Authorization']='Basic '+tokenAuthorization
        try:
            getToken = requests.get(url+'token',headers=headers)
            statusCode = getToken.status_code
            if statusCode==200:
                token = getToken.json()['token']
                tokenType = getToken.json()['type']
                return [statusCode,token,tokenType]
            else:
                return [statusCode,'','']
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''


    #登陆者的Token_headers
    def Token_headers(self,Token_Type,token):
        Token_headers = {'Authorization':''}
        Token_headers['Authorization']=Token_Type+' '+token
        return Token_headers
    
    def getDrives(self,url,Token_headers,driveType):
        try:
            drives=requests.get(url+'drives',headers=Token_headers)
            drivesInfo=drives.json()
            n=len(drivesInfo)
            if driveType=='private':
                for i in range(n):
                    if drivesInfo[i]['type']=='private':
                        return drivesInfo[i]['uuid']
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    
    def mkDirByHttp(self,url,driverUuid,dirUuid,dirName,headers):
        operate = MultipartEncoder(
            fields={dirName: json.dumps({'op': 'mkdir'})}
        )
        headers['content-type'] = operate.content_type
        try:            
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate)
            code = resp.status_code
            respInfo = resp.json()
            return [code,respInfo]
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    def getFileInfoByHttp(self,url,driverUuid,dirUuid,headers,fileName,fileType):
        try:
            resp=requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'?metadata=true',headers=headers)
            code = resp.status_code
            respInfo = resp.json()
            entries = respInfo['entries']
            n=len(entries)
            for i in range(n):
                if entries[i]['name'] == fileName and entries[i]['type'] == fileType:
                    return [code,entries[i]]
            return[code,'']
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    def queryFileByHttp(self,url,driverUuid,dirUuid,headers,fileName,fileType):
        try:
            resp=requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'?metadata=true',headers=headers)
            code = resp.status_code
            if code == 200:
                msg = u'查询文件操作成功'
                self.show_log(msg)
                respInfo = resp.json()
                entries = respInfo['entries']
                n=len(entries)
                isExist = 'N'
                for i in range(n):
                    if entries[i]['name'] == fileName and entries[i]['type'] == fileType:
                        isExist = 'Y'
                        return isExist
                if isExist == 'N':   
                    return isExist
            else:
                msg = u'查询文件操作失败，服务器返回code==%s'%code
                self.show_log(msg)
                return[code,'']
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    def getDirInfoByHttp(self,url,driverUuid,dirUuid,headers):
        try:
            resp=requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'?metadata=true',headers=headers)
            code = resp.status_code
            respInfo = resp.json()
            entries = respInfo['entries']
            return [code,entries]
            return[code,'']
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''

    #download_file
    def downloadFile(self,URL,driverUUID,dirUUID,entriesUUID,srcFileName,dstFilePath,Token_headers):
        try:
            resp = requests.get(URL+'drives/'+driverUUID+'/dirs/'+dirUUID+'/entries/'+entriesUUID+'?name='+srcFileName,headers=Token_headers)
            code = resp.status_code
            with open(dstFilePath, 'wb') as f:
                f.write(resp.content)
            return code
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
           
    #创建新用户    
    def CreatUser(self,new_username,new_PASSword,Token_headers,URL):
        new_user = {"username":new_username,"PASSword":new_PASSword}
        try:            
            creat_user = requests.post(URL+'users',headers=Token_headers,data=new_user)#自研：http://wisnuc.station:3000/station/info
            print [creat_user.status_code,creat_user.json()]
            return [creat_user.status_code,creat_user.json()]
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''

    def GetValue(self,user_list,username,key):
        n = len(user_list)
        for i in range(n):
            if user_list[i]['username']==username:
                return user_list[i][key]
    
    def Rename(self,URL,newname,user_uuid,headers):
        new_name = {"username":newname}
        rename = requests.patch(URL+'users'+'/'+user_uuid,headers=headers,data=new_name)
        return [rename.status_code,rename.json()]
    
    def renameByHttp(self,url,driverUuid,dirUuid,oldFileName,newFileName,headers):#文件夹重命名
        operate = MultipartEncoder(
            fields={oldFileName+'|'+newFileName: json.dumps({"op": "rename"})}
        )
        headers['content-type'] = operate.content_type
        try:
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate)
            code = resp.status_code
            return [code,resp.json()]
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''

    def ModifyPASSword(self,URL,newPASSword,user_uuid,headers):
        new_PASSword = {'PASSword':newPASSword}
        modify_PASSword = requests.put(URL+'users'+'/'+user_uuid+'/'+'PASSword',headers=headers,data=new_PASSword)
        if modify_PASSword.status_code == 200:
            return [modify_PASSword.status_code,'']
        else:
            return [modify_PASSword.status_code,modify_PASSword.json()]

    def ModifyPermission(self,URL,permission,uuid,headers):
        user_permission={'isAdmin':permission}
        modify_permission=requests.patch(URL+'users'+'/'+uuid,headers=headers,data=json.dumps(user_permission))
        return [modify_permission.stastus,modify_permission.json()]
    
    def removeFileByHttp(self,url,driverUuid,dirUuid,fileUuid,fileName,headers):
        operate = MultipartEncoder(
            fields={fileName: json.dumps({"op":"remove","uuid":fileUuid})}
        )
        headers['content-type'] = operate.content_type
        try:            
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate)
            code = resp.status_code
            respInfo = resp.json()
            return [code,respInfo]
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''

        #远程SSH进程检查   
    def SSH_Check(self,SSH_Ip,SSH_Port,SSH_Loginname,SSH_PASSword,ps_check1,ps_check2,ps_check3,ps_check4,SSH_until_tag,f):
        #创建SSH对象
        try:
            ssh = paramiko.SSHClient()
            #把要连接的机器添加到known_hosts文件中,跳过了远程连接中选择‘是’的环节
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #连接服务器
            ssh.connect(SSH_Ip,SSH_Port,SSH_Loginname,SSH_PASSword)
            time.sleep(2)
            list=[ps_check1,ps_check2,ps_check3,ps_check4]
            print list
            msg=u'本次测试需要检查的进程有%s'%list
            self.show_log(msg)
            self.log_write(msg, f)
            for p in list:#########检查ps_check的进程数
                cmd = 'ps -aux| grep %s |grep -v "grep"'%(p)
                stdin,stdout,stderr = ssh.exec_command(cmd)
                result = stdout.read()
                logging.info(result)            
                if not result:
                    result = stderr.read().decode
                    msg=u'SSH_PS(%s进程)无任何信息,测试需要检查'%p
                    self.show_log(msg)
                    self.log_write(msg, f)
                    ssh.close()
                    return 'FAIL'
                else :
                    msg= u'%s进程检查OK'%(p)
                    self.show_log(msg)
                    self.log_write(msg, f)
            msg=u'本次进程检查全部通过'
            self.show_log(msg)
            self.log_write(msg, f)
            return 'PASS'
            ssh.close()
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    def uploadFileByMultiPartForm(self,url,driverUuid,dirUuid,filePath,headers,mimetype = None,operate = '',fileUuid = ''):
    #using urllib2
        try:            
            fileSize = self.getFileSize(filePath)
            fileSha256 = self.getFileSha256(filePath)
            boundary = self.getBoundary()
            if mimetype is None:
                mimetype = mimetypes.guess_type(filePath)[0] or 'application/octet-stream'
            contentType = 'multipart/form-data; boundary=%s' % boundary        

            formFields = []
            partBoundary = '--' + boundary
            files = []
            fileName = filePath[filePath.rfind('\\')+1:]
            openfile = open(filePath, 'rb')
            body = openfile.read()
            fieldName = {"size":fileSize,"sha256":fileSha256}
            files.append((fileName,json.dumps(fieldName),mimetype, body))
            parts = []
            # Add the forms to upload
            parts.extend(
                [partBoundary,
                 'Content-Disposition: form-data; name="%s"' % name,
                 '',
                 value,
                 ]
                for name, value in formFields
            )
            if operate != '':
                opeField = {"op":operate,"uuid":fileUuid}
                parts.extend(
                    [partBoundary,
                     'Content-Disposition: form-data; name="%s"' % fileName,
                     '',
                     opeField,
                     ]
                )
            # Add the files to upload
            parts.extend(
                [partBoundary,
                 'Content-Disposition: form-data; name="%s"; filename="%s"' % \
                 (fieldName, fileName),
                 'Content-Type: %s' % content_type,
                 '',
                 body,
                 ]
                for fieldName, fileName, content_type, body in files
            )
            flattened = list(itertools.chain(*parts))
            flattened.append(partBoundary + '--')
            flattened.append('')
            form = '\r\n'.join(flattened)
            httpUrl = url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries'
            request = urllib2.Request(str(httpUrl))
            request.add_header('Authorization',headers['Authorization'])
            request.add_header('Content-type', contentType)
            request.add_header('Content-length', len(form))
            request.add_data(form)
            resp = urllib2.urlopen(request).read()
            openfile.close()
            return resp
        except Exception as e:
            msg1 = u'异常的类型是：%s'%type(e)
            msg2 = u'异常的内容是：%s'%e
            logging.info(msg1)
            logging.info(msg2)
            return ''
    def getFileSize(self,filePath):
        size = os.stat(filePath)
        return int(size.st_size)

    def getFileSha256(self,filePath):
        openedFile = open(filePath, 'rb')
        sha256 = hashlib.sha256(openedFile.read())
        openedFile.close()
        return sha256.hexdigest()

    def getFileSha256Byfsum(self,filePath):
        fileName = filePath[filePath.rfind('\\')+1:]
        dirName = filePath[0:filePath.rfind('\\')]
        cmd = 'fsum.exe -sha256 -d"'+dirName+'" '+fileName+''
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = p.stdout.read().replace('\r\n','').split(';')
        hashVal = out[4].split(' ')[0]
        return hashVal

    def getBoundary(self):
        return mimetools.choose_boundary()

    def linkStatus_Check(self, URL,ff):
        msg = 'ping %s -n 10' % URL
        p = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        line = p.stdout.read()
        self.show_log(line.decode("gbk"))
        self.log_write(str(line), ff)
        matchobj = re.search(r'TTL', line, re.M | re.I)
        if matchobj:
            logging.info('DUT ip has been UP-----Check success!')
            return 'PASS'
        else:
            logging.info('Ip ping still not successful-----Check FAIL!')
            time.sleep(5)
            return 'FAIL'
        
    ##case测试结束时，统计用例测试结果：什么产品，什么用例，测试多少次，pass多少次，fail多少次
    def statics_result(self, model, version, times, ff, sn, pass_times, fail_times, case):
        msg_list = []
        msg_list.append('********************Test Finished!***********************')
        msg_list.append('This case %s(%s) test this DUT %s %s times,the details is:' % (model, version, case, times))
        msg_list.append('DUT (SN:%s) PASS %s times;' % (sn, pass_times))
        msg_list.append('DUT (SN:%s) FAIL %s times;' % (sn, fail_times))
        for msg in msg_list:
            self.show_log(msg)
            self.log_write(msg, ff)

    ##case一次测试结果，统计到目前为止测试结果：此次（第多少次）测试结果是PASS还是FAIL，到目前为止PASS次数，FAIL次数。测试结果FAIL时，如果是非概率，结束测试。否则，继续下一次测试
    def conn_status_statics(self, ff, sn, loop_index, PASS_times, FAIL_times, stop_when_neterr, test_case,
                            result_tag, console, com, bound, start_time,matchobj,AutoHand_com, AutoHand_bound):
        result = []
        if result_tag == 'PASS':
            logging.info( 'Test the route that should be PASS!')
            if matchobj == 'PASS':
                logging.info('In fact the route is:PASS!')
                msg = ' The DUT (SN:%s) the %sth %s Link detection result is:PASS;' % (sn, loop_index, test_case)
                self.show_log(u'被测设备(SN:%s) 第%s次 %s 链路检测结果是:PASS' % (sn, loop_index, test_case))
                self.log_write(msg, ff)

                temp_times = PASS_times + 1
                msg = ' The DUT (SN:%s) at present %s Succeeded %s times;' % (sn, test_case, temp_times)
                self.show_log(u'被测设备(SN:%s)目前%s成功%s次' % (sn, test_case, temp_times))
                self.log_write(msg, ff)
                PASS_times = PASS_times + 1
            else:
                logging.info('In fact the route is: FAIL!')
                msg = ' The DUT (SN:%s) the %sth %s Link detection result is:FAIL;' % (sn, loop_index, test_case)
                self.show_log(u'被测设备(SN:%s)第%s次%s链路检测结果是:FAIL;' % (sn, loop_index, test_case))
                self.log_write(msg, ff)

                if stop_when_neterr == 'False':
                    temp_times = FAIL_times + 1
                    msg = ' The DUT (SN:%s) has FAILed,at present %s FAILed %s times;' % (sn, test_case, temp_times)
                    self.show_log(u'被测设备(SN:%s),目前%s失败%s次' % (sn, test_case, temp_times))
                    self.log_write(msg, ff)
                    FAIL_times = FAIL_times + 1

                    msg = ' KaiGuanJi Restart the DUT...........'
                    self.show_log(u'本次测试失败，断电重启恢复系统正常状态')
                    self.log_write(msg, ff)
##                    self.zhouqi(console, com, bound)
##                    #机械手
##                    self.AutoHand_DownUp(self,AutoHand_com, AutoHand_bound)
##                    time.sleep(start_time)
                    result.append(PASS_times)
                    result.append(FAIL_times)
                    result.append('continue')
                    return result
                else:
                    result.append(PASS_times)
                    result.append(FAIL_times)
                    result.append('end')
                    return result
        else:
            logging.info('Test the route that should be FAIL!')
            if matchobj == 'FAIL':
                logging.info('In fact the route is: FAIL!')
                msg = ' The DUT (SN:%s) the %sth %s Link detection result is:PASS;' % (sn, loop_index, test_case)
                self.show_log(u'被测设备(SN:%s) 第%s次 %s 链路检测结果是:PASS' % (sn, loop_index, test_case))
                self.log_write(msg, ff)

                times_tmp = PASS_times + 1
                msg = ' The DUT (SN:%s) at present %s Succeeded %s times;' % (sn, test_case, times_tmp)
                self.show_log(u'被测设备(SN:%s)目前%s成功%s次' % (sn, test_case, times_tmp))
                self.log_write(msg, ff)
                PASS_times = PASS_times + 1

            else:
                logging.info('In fact the route is: PASS!')
                msg = ' The DUT (SN:%s) the %sth %s Link detection result is:FAIL;' % (sn, loop_index, test_case)
                self.show_log(u'被测设备(SN:%s)第%s次%s链路检测结果是:FAIL;' % (sn, loop_index, test_case))
                self.log_write(msg, ff)

                if stop_when_neterr == 'False':
                    temp_times = FAIL_times + 1
                    msg = ' The DUT (SN:%s) has FAILed,at present %s FAILed %s times;' % (sn, test_case, temp_times)
                    self.show_log(u'被测设备(SN:%s),目前%s失败%s次' % (sn, test_case, temp_times))
                    self.log_write(msg, ff)
                    FAIL_times = FAIL_times + 1

                    msg = ' KaiGuanJi Restart the DUT...........'
                    self.show_log(u'开关机重启被测设备')
                    self.log_write(msg, ff)
                    self.zhouqi(console, com, bound)
                    time.sleep(start_time)
                else:
                    result.append(PASS_times)
                    result.append(FAIL_times)
                    result.append('end')
                    return result

        result.append(PASS_times)
        result.append(FAIL_times)
        result.append('ing')
        return result
    def uploadDirByHttp(self,url,headers,dsrc,driveUuid,dirUuid):
        result = 'SUCCESS'
        print dsrc
        listdsrc = os.listdir(dsrc)
        nsrc = len(listdsrc)
        for i in range(nsrc):
            tmp = dsrc + listdsrc[i]
            print tmp
            if os.path.isfile(tmp):
                self.uploadFileByMultiPartForm(url,driveUuid,dirUuid,tmp,headers,mimetype = None,operate = '',fileUuid = '')
                #####添加上传失败逻辑
            else:
                dirInfo = self.mkDirByHttp(url,driveUuid,dirUuid,listdsrc[i],headers)
                if dirInfo[0] != 200:
                    msg = u'在目录%s下创建目录%s失败！' %(dirUuid,listdsrc[i])
                    self.show_log(msg)
                    result = 'FAIL'
                    return result
                else:
                    dirInfo = self.getFileInfoByHttp(url,driveUuid,dirUuid,headers,listdsrc[i],'directory')
                    dirnUuid = dirInfo[1]['uuid']
                    result = self.uploadDirByHttp(url,headers,tmp+'\\',driveUuid,dirnUuid)
        return result    
    
    def downloadDirByHttp(self,url,headers,dirPath,driveUuid,dirUuid):
        result = 'SUCCESS'
        entriesInfo = self.getDirInfoByHttp(url,driveUuid,dirUuid,headers)
        if entriesInfo[0] != 200:
            result = 'FAIL'
            return result
        else:
            entries = entriesInfo[1]
            entryNum = len(entries)
            for entryi in range(entryNum):
                fileName = entries[entryi]['name']
                fileType = entries[entryi]['type']
                entryUuid = entries[entryi]['uuid']
                dstFilePath = dirPath + '\\' + fileName
                if fileType == 'file':
                    downCode = self.downloadFile(url,driveUuid,dirUuid,entryUuid,fileName,dstFilePath,headers)
                    if downCode != 200:
                        msg = u'目录%s下文件%s下载失败！' %(dirUuid,fileName)
                        self.show_log(msg)
                        result = 'FAIL'
                        return result
                else:
                    os.mkdir(dstFilePath)
                    result = self.downloadDirByHttp(url,headers,dstFilePath,driveUuid,entryUuid)
            return result
        
        ##控制继电器随机断电
    def suiji(self, console, com, bound):
        down_power=""
        up_power=""
        if console == '1':
            down_power = "\xAA\x5A\x00\x01\x00\xFF"
            up_power = "\xAA\x5A\x00\x00\x00\xFF"
        elif console == '2':
            down_power = "\xAA\x5A\x00\x11\x00\xFF"
            up_power = "\xAA\x5A\x00\x10\x00\xFF"
        elif console == '3':
            down_power = "\xAA\x5A\x00\x21\x00\xFF"
            up_power = "\xAA\x5A\x00\x20\x00\xFF"
        elif console == '4':
            down_power = "\xAA\x5A\x00\x31\x00\xFF"
            up_power = "\xAA\x5A\x00\x30\x00\xFF"

        i = random.randint(2, 50)
        msg = 'Tool %sth slot is working ' % console
        self.show_log(msg)
        t = serial.Serial(str(com), int(bound), timeout=0.01)
        self.show_log('Shutdown the power!')
        t.write(down_power)
        time.sleep(2)
        self.show_log('Up the power!')
        t.write(up_power)
        self.show_log('Wait for %s seconds.....' % i)
        time.sleep(i)
        self.show_log('Shutdown the power!')
        t.write(down_power)
        time.sleep(2)
        self.show_log('Up the power!')
        t.write(up_power)
        time.sleep(2)
        t.close()

    def zhouqi(self, console, com, bound):
        down_power=""
        up_power=""
        if console == '1':
            down_power = "\xAA\x5A\x00\x01\x00\xFF"
            up_power = "\xAA\x5A\x00\x00\x00\xFF"
        elif console == '2':
            down_power = "\xAA\x5A\x00\x11\x00\xFF"
            up_power = "\xAA\x5A\x00\x10\x00\xFF"
        elif console == '3':
            down_power = "\xAA\x5A\x00\x21\x00\xFF"
            up_power = "\xAA\x5A\x00\x20\x00\xFF"
        elif console == '4':
            down_power = "\xAA\x5A\x00\x31\x00\xFF"
            up_power = "\xAA\x5A\x00\x30\x00\xFF"
        msg = 'Tool %sth slot is working' % console
        self.show_log(msg)
        try:
            t = serial.Serial(str(com), int(bound), timeout=0.01)
            self.show_log('Shutdown the power!')
            t.write(down_power)
            time.sleep(2)
            self.show_log('Up the power!')
            t.write(up_power)
            t.close()
        except Exception as e:
            msg = u'继电器串口出现异常，异常类型：%s，异常内容是：%s'%(type(e),e)
            self.show_log(msg)
            return 'FAIL'

    def AutoHand_DownUp(self, com, bound):
        Button_down = "\xAA\xFE\x00\x11\x55"########按下去
        Button_up = "\xAA\xFE\x11\x11\x55"########弹回来
        t = serial.Serial(str(com), int(bound), timeout=0.01)
        self.show_log('........Button_down......')
        t.write(Button_down)
        print "down"
        time.sleep(3)############按键持续时间
        self.show_log('........Button_up.......')
        t.write(Button_up)
        time.sleep(2)
        print "up"
        t.close()
        
    ##检测开关机治具关机是否成功。命令：ping %s -n 4
    def check_shutdown(self, URL):
        #检查route链路：
        msg = 'ping %s -n 4' % URL
        p = subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        line = p.stdout.read()
        self.show_log(line.decode("gbk"))
        matchobj = re.search(r'TTL', line, re.M | re.I)
        if matchobj:
            msg=u'DUT still working! 断电或重启动作操作 FAIL!'
            self.show_log(msg)
            return 'FAIL'
        else:
            msg=u'DUT not working! 断电或重启动作操作 SUCCESS!'
            self.show_log(msg)
        return 'PASS'
##aa=Public_Library()
##while (1):
##    aa.AutoHand_DownUp('com10','9600')
