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
##import MultiPartForm
import base64
import xlutils
import serial
import time
import re
import codecs
import shutil
import subprocess
import math
import sys
import chardet
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from requests_toolbelt import MultipartEncoder


class Public_Library():
    def getUserUuid(self,url,userName,f):
        NETWORK_STATUS = True
        try:
            userUrl = requests.get(url+'users',timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
        if NETWORK_STATUS == True:
            statusCode = userUrl.status_code
            userInfo = userUrl.json()
            for i in range(len(userInfo)):
                if userInfo[i]['username'] == userName:
                    return userInfo[i]['uuid']
        return ''
    
    def getToken(self,userUuid,userPassword,url,f):
        userInfo = userUuid+':'+userPassword
        tokenAuthorization = base64.b64encode(userInfo)
        headers = {'Authorization':''}
        headers['Authorization']='Basic '+tokenAuthorization
        try:
            getToken = requests.get(url+'token',headers=headers,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','','']
        statusCode = getToken.status_code
        if statusCode==200:
            token = getToken.json()['token']
            tokenType = getToken.json()['type']
            return [statusCode,token,tokenType]
        else:
            return [statusCode,'','']        
    
    def login(self,tokenType,token,userUuid,url,f):
        headers = {'Authorization':''}
        headers['Authorization']=tokenType+' '+token
        try:
            userLogin = requests.get(url+'users'+'/'+userUuid,headers=headers,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = userLogin.status_code
        loginInfo = userLogin.json()
        return [code,loginInfo]

    def creatUser(self,userName,password,tokenType,token,url,f):
        headers = {'Authorization':''}
        headers['Authorization']=tokenType+' '+token
        newUser = {"username":userName,"password":password}
        try:
            creatUser = requests.post(url+'users',headers=headers,data=newUser,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        return [creatUser.status_code,creatUser.json()]

    def getUserValue(self,userList,userName,key):
        n = len(userList)
        for i in range(n):
            if userList[i]['username']==userName:
                return userList[i][key]

    def loginHeaders(self,userUuid,userPassword):
        userInfo = userUuid+':'+userPassword
        tokenAuthorization = base64.b64encode(userInfo)
        headers = {'Authorization':''}
        headers['Authorization']='Basic '+tokenAuthorization
        return headers
    
    def tokenHeaders(self,tokenType,token):
        headers = {'Authorization':''}
        headers['Authorization']=tokenType+' '+token
        return headers
    
    def renameUser(self,url,newName,userUuid,headers,f):
        userName = {"username":newName}
        try:
            rename = requests.patch(url+'users'+'/'+userUuid,headers=headers,data=userName,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        return [rename.status_code,rename.json()]

    def modifyPassword(self,url,newPassword,userUuid,headers,f):
        password = {'password':newPassword}
        try:
            modifyPassword = requests.put(url+'users'+'/'+userUuid+'/'+'password',headers=headers,data=password,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        if modifyPassword.status_code == 200:
            return [modifyPassword.status_code,'']
        else:
            return [modifyPassword.status_code,modifyPassword.json()]

    def modifyPermission(self,url,permission,uuid,headers,f):
        userPermission={'isAdmin':permission}
        try:
            modifyPermission=requests.patch(url+'users'+'/'+uuid,headers=headers,data=json.dumps(userPermission),timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        return [modifyPermission.stastus,modifyPermission.json()]

    def getDrives(self,url,headers,driveType,f):
        try:
            drives=requests.get(url+'drives',headers=headers,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
        drivesInfo=drives.json()
        n=len(drivesInfo)
        if driveType=='private':
            for i in range(n):
                if drivesInfo[i]['type']=='private':
                    return drivesInfo[i]['uuid']
        for i in range(n):
            if drivesInfo[i]['type'] == driveType:
                return drivesInfo[i]['uuid']
        return ''
    
    #创建共享盘(POST/drives)

    def PostDrives(self,headers,userUuid,label):
        Request_Body={"writelist":userUuid,"label":label}
        PostDrives_request=requests.post(self.url+'drives',headers=headers,data=Request_Body)        
        return [PostDrives_request.status_code,PostDrives_request.json()]

    def getFileSize(self,filePath):
        size = os.stat(filePath)
        return int(size.st_size)

    def getFileSha256(self,filePath):
        openedFile = open(filePath, 'rb')
        sha256 = hashlib.sha256(openedFile.read())
        openedFile.close()
        return sha256.hexdigest()
    
    def getBigFileSha256(self,filePath):
        sha256 = hashlib.sha256()
        with open(filePath, 'rb') as file:
            while True:
                data = file.read(1024*1024*128)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()


    def getFileSha256Byfsum(self,filePath,f):
        fileName = filePath[filePath.rfind('\\')+1:]
        dirName = filePath[0:filePath.rfind('\\')]
        cmd = 'fsum.exe -sha256 -d"'+dirName+'" '+fileName+''
        try:
            p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = p.stdout.read().replace('\r\n','').split(';')
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
        hashVal = out[4].split(' ')[0]
        return hashVal

    def mkDirByHttp(self,url,driverUuid,dirUuid,dirName,headers,f):
        operate = MultipartEncoder(
            fields={dirName: json.dumps({'op': 'mkdir'})}
        )
        headers['content-type'] = operate.content_type
        try:
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        return [code,respInfo]

    def getFileInfoByHttp(self,url,driverUuid,dirUuid,headers,fileName,fileType,f):
        try:
            resp=requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'?metadata=true',headers=headers,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        entries = respInfo['entries']
        n=len(entries)
        for i in range(n):
            if entries[i]['name'] == fileName and entries[i]['type'] == fileType:
                return [code,entries[i]]
        return[code,'']
    
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

    def getDirInfoByHttp(self,url,driverUuid,dirUuid,headers,f):
        try:
            resp=requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'?metadata=true',headers=headers,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        entries = respInfo['entries']
        return [code,entries]

    def dupFileByHttp(self,url,driverUuid,dirUuid,oldFileName,newFileName,headers,f):
        operate = MultipartEncoder(
            fields={oldFileName+'|'+newFileName: json.dumps({"op": "dup"})}
        )
        headers['content-type'] = operate.content_type
        try:
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        return [code,respInfo]

    def removeFileByHttp(self,url,driverUuid,dirUuid,fileUuid,fileName,headers,f):
        operate = MultipartEncoder(
            fields={fileName: json.dumps({"op":"remove","uuid":fileUuid})}
        )
        headers['content-type'] = operate.content_type
        try:
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        return [code,respInfo]

    def renameByHttp(self,url,driverUuid,dirUuid,oldFileName,newFileName,headers,f):
        operate = MultipartEncoder(
            fields={oldFileName+'|'+newFileName: json.dumps({"op": "rename"})}
        )
        headers['content-type'] = operate.content_type
        try:
            resp = requests.post(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries',headers=headers, data=operate,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ['','']
        code = resp.status_code
        respInfo = resp.json()
        return [code,respInfo]

    def getBoundary(self):
        return mimetools.choose_boundary()

    
    def FileSlicer(self,input_file, output_file, slice_size, chunk_size=1024 * 1024):
##        slice_size = 1024 * 1024 * 1024
##        inputfile = 'K:\\transformers.mp4'
##        outputfile = 'K:\\transformer_part'
        file_size = float(os.stat(input_file).st_size)
        parts = int(math.ceil(file_size / slice_size))
        subFlist = []
        if not os.path.exists(output_file):
            os.makedirs(output_file)
        with open(input_file, 'rb') as f:
            for i in range(parts):
                psize = 0
                output_part = output_file + 'slicerPart%s' % i
                with open(output_part, 'wb') as of:
                    while psize <= slice_size - chunk_size:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        of.write(data)
                        psize += chunk_size
                subFlist.append(output_part)
                self.show_log(input_file + '\'s part '+str(i)+' '+ output_part)
        return subFlist
##                print '%s Finished.' % output_file

    # Uploader for files < 1G
    def StreamFileUploader(self, url, driverUuid,dirUuid,filePath, headers):
        register_openers()
        filenames = filePath[filePath.rfind('\\')+1:]
        size = self.getFileSize(filePath)
        sha = self.getBigFileSha256(filePath)
        driverUuid = str(driverUuid)
        dirUuid = str(dirUuid)
        post_url = url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries'
        fileInfo = json.dumps({'op': 'newfile', 'size': size, 'sha256': sha})
        f = open(filePath, 'rb')
        file_data = MultipartParam(name=filenames, filename=fileInfo, fileobj=f, filesize=size)
        params = {filenames: file_data}
        datagen, data_headers = multipart_encode(params)
        request = urllib2.Request(post_url, datagen, data_headers)        
        request.add_header('Authorization',headers['Authorization'])########lele
        return urllib2.urlopen(request).getcode()############################lele




    # Uploader for files > 1G
    def StreamPartsAppender(self, url, driverUuid,dirUuid,fileName,filePath, headers, fileInfo):
        register_openers()
##        filenames = filePath[filePath.rfind('\\')+1:]
        size = self.file_size(filepath)
        sha = self.file_hash(filepath)
        driverUuid = str(driverUuid)
        dirUuid = str(dirUuid)
        post_url = url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries'
        self.show_log('upload ' + post_url)
        f = open(filePath, 'rb')
        file_data = MultipartParam(name=fileName, filename=fileInfo, fileobj=f)
        params = {fileName: file_data}
        datagen, data_headers = multipart_encode(params)
        # Do the request
        request = urllib2.Request(post_url, datagen, data_headers)
        request.add_header('Authorization',headers['Authorization'])
##        request.add_header('Authorization', headers)
        resp = urllib2.urlopen(request).getcode()
        return resp

    def uploadFileByMultiPartForm(self,url,driverUuid,dirUuid,filePath,headers,f,mimetype = None,operate = '',fileUuid = ''):
    #using urllib2)
##        self.show_log(url+'+'+driverUuid+'+'+dirUuid+'+'+filePath)
##        self.show_log(headers)
        fileSize = self.getFileSize(filePath)
        try:
            fileSha256 = self.getBigFileSha256(filePath)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
        boundary = self.getBoundary()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filePath)[0] or 'application/octet-stream'
        contentType = 'multipart/form-data; boundary=%s' % boundary        

        formFields = []
        partBoundary = '--' + boundary
        files = []
        fileName = filePath[filePath.rfind('\\')+1:]
##        openfile = codecs.open(filePath, 'rb','utf-8')
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
        try:
            request = urllib2.Request(str(httpUrl))
            request.add_header('Authorization',headers['Authorization'])
            request.add_header('Content-type', contentType)
            request.add_header('Content-length', len(form))
            request.add_data(form)
##            resp = urllib2.urlopen(request).read()
            resp = urllib2.urlopen(request).getcode()
            openfile.close()
            return resp
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
                

    def downloadFile(self,url,driverUuid,dirUuid,entryUuid,srcFileName,dstFilePath,headers,f):
        try:
            resp = requests.get(url+'drives/'+driverUuid+'/dirs/'+dirUuid+'/entries/'+entryUuid+'?name='+srcFileName,headers=headers, stream=True,timeout = 5)
        except Exception as e:
            msg = u"异常的类型是:%s"%type(e) 
            self.show_log(msg)
            self.log_write(msg, f)
            msg = u"异常的内容是:%s"%e 
            self.show_log(msg)
            self.log_write(msg, f)
            return ''
        code = resp.status_code
        with open(dstFilePath, 'wb') as f:
##            f.write(resp.content)
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return code

    def copyFileBySmb(self,fsrcPath,fdstPath,f):
        sha256fsrc = self.getBigFileSha256(fsrcPath)
        shutil.copy(fsrcPath, fdstPath)
        self.show_log('copy  '+fsrcPath + ' ' + fdstPath)
        if os.path.isfile(fdstPath):            
            sha256fdst = self.getBigFileSha256(fdstPath)
            if sha256fsrc == sha256fdst:
                return 'SUCCESS'
            else:
                msg = 'the wrong content! failed!!!' 
                self.show_log(msg)
                self.log_write(msg, f)
                return 'FAIL'
        else:
            msg = 'the wrong file name! failed!!!'
            self.show_log(msg)
            self.log_write(msg, f)
            return 'FAIL'

    def moveFileBySmb(self,fsrcPath,fdstPath,f):
        sha256fsrc = self.getBigFileSha256(fsrcPath)
        shutil.move(fsrcPath, fdstPath)
        if os.path.isfile(fsrcPath):
            msg = 'the src file is not delete! failed!!!'
            self.show_log(msg)
            self.log_write(msg, f)
            return 'FAIL'
        if os.path.isfile(fdstPath):           
            sha256fdst = self.getBigFileSha256(fdstPath)
            if sha256fsrc == sha256fdst:
                return 'SUCCESS'
            else:
                msg = 'the dst file has wrong content! failed!!!'
                self.show_log(msg)
                self.log_write(msg, f)
                return 'FAIL'
        else:
            msg = 'the dst file has wrong file name! failed!!!'
            self.show_log(msg)
            return 'FAIL'

    def removeFileBySmb(self,filePath):
        os.remove(filePath)
        self.show_log('remove  '+filePath)
        if os.path.isfile(filePath):
            return 'FAIL'
        else:
            return 'SUCCESS'

    def renameFileBySmb(self,oldFilePath,newFilePath,f):
        self.show_log(oldFilePath)
        sha256fsrc = self.getBigFileSha256(oldFilePath)
        os.rename(oldFilePath, newFilePath)
        self.show_log('rename  '+oldFilePath + ' ' + newFilePath)
        if os.path.isfile(oldFilePath):
            return 'FAIL'
        else:
            sha256fdst = self.getBigFileSha256(newFilePath)
            if sha256fsrc != sha256fdst:
                return 'FAIL'
            else:
                return 'SUCCESS'

    def newFileBySmb(self,newFilePath):
        fp = open(newFilePath,'w')
        fp.close()
        if os.path.isfile(newFilePath):
            return 'SUCCESS'
        else:
            return 'FAIL'

    def copyDirBySmb(self,dsrc,ddst,f):
        listdsrc = os.listdir(dsrc)
        self.show_log('begin copytree  '+dsrc + ' ' + ddst)
        self.log_write('begin copytree  '+dsrc + ' ' + ddst, f)
        shutil.copytree(dsrc, ddst)
        self.show_log('end copytree  '+dsrc + ' ' + ddst)
        self.log_write('end copytree  '+dsrc + ' ' + ddst, f)
        if os.path.isdir(ddst):           
            listddst = os.listdir(ddst)
            nsrc = len(listdsrc)
            ndst = len(listdsrc)
            if nsrc != ndst:
                return "FAIL"
            for i in range(nsrc):
                tmp = ddst+listddst[i]
                if os.path.isfile(tmp):
                    sha256fsrc = self.getBigFileSha256(dsrc+listdsrc[i])
                    sha256fdst = self.getBigFileSha256(ddst+listddst[i])
                    if sha256fsrc != sha256fdst:
                        return 'FAIL'                    
            return "SUCCESS"
        return 'FAIL'

    def moveDirBySmb(self,dsrc,ddst,f):
        listdsrc = os.listdir(dsrc)
        shutil.move(dsrc, ddst)
        if os.path.isdir(dsrc):
            msg = 'the src dir is not delete! failed!!!'
            self.show_log(msg)
            self.log_write(msg, f)
            return 'FAIL'
        if os.path.isdir(ddst):           
            listddst = os.listdir(ddst)
            nsrc = len(listdsrc)
            ndst = len(listddst)
            if nsrc != ndst:
                return "FAIL"                    
            return "SUCCESS"
        return 'FAIL'    
    
    def removeDirBySmb(self,dirpath,f):
        shutil.rmtree(dirpath)
        self.show_log('remove  '+dirpath)
        self.log_write('remove  '+dirpath, f)
        if os.path.isdir(dirpath):
            return 'FAIL'
        return 'SUCCESS'
       
    def renameDirBySmb(self,oldDir,newDir,f):
        self.show_log('rename  '+oldDir + ' ' + newDir)
        os.rename(oldDir, newDir)
        
        if os.path.isdir(oldDir):
            return 'FAIL'
        if not (os.path.isdir(newDir)):
            return 'FAIL'
        return 'SUCCESS'

    def mkDirBySmb(self,dirpath):
        os.mkdir(dirpath)
        if os.path.isdir(dirpath):
            return 'SUCCESS'
        return 'FAIL'

    def copyFileByFastcopy(self,cmd,runtime,srcPath,dstPath):
##        cmd = 'fastCopy.exe /cmd=force_copy  /auto_close /log /filelog /logfile="%s" /utf8 "%s" /to="%s"' %(logPath,srcPath,dstPath)
        starttime = time.time()
        result = ''
        endtime = time.time()
        listdsrc = os.listdir(srcPath)
        while (endtime - starttime)<int(runtime):
            p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            result = p.stdout.read().decode("gbk",'ignore')
            if result != '':
                return 'FAIL'
            endtime = time.time()
            listddst = os.listdir(dstPath)
            nsrc = len(listdsrc)
            ndst = len(listddst)
            if nsrc != ndst:
                return "FAIL"
            for i in range(nsrc):
                tmp = dstPath+listddst[i]
                if os.path.isfile(tmp):
                    sha256fsrc = self.getBigFileSha256(srcPath+listdsrc[i])
                    sha256fdst = self.getBigFileSha256(dstPath+listddst[i])
                    if sha256fsrc != sha256fdst:
                        return 'FAIL'
        if result != '':
            return 'FAIL'
        return 'SUCCESS'

    def sshCmdPost(self,url,userName,pwd,cmd):
        # 创建SSH对象
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())#第一次登录的认证信息
        # 连接服务器
        ssh.connect(hostname = url, port = 22, username = userName, password = pwd)
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 获取命令结果
        res,err = stdout.read(),stderr.read()
        result = res if res else err
        # 关闭连接
        ssh.close()

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

    
    def isChinese(self,char):
        """判断是否包含中文"""
        if not isinstance(char, unicode):
            char = char.decode('utf8')
        if re.search(ur"[\u4e00-\u9fa5]+",char):
            self.show_log(char)
            return True
        else:
            return False

#########添加文件夹上传20180606
    def uploadDirByHttp(self,url,headers,dsrc,driveUuid,dirUuid,f):
        result = 'SUCCESS'
        listdsrc = os.listdir(dsrc)
        nsrc = len(listdsrc)
        for i in range(nsrc):
            if self.isChinese(listdsrc[i]):
                tmp = (dsrc + listdsrc[i]).encode("gbk")
            else:
                tmp = dsrc + listdsrc[i]
            self.show_log('upload '+tmp)          
            if os.path.isfile(tmp):
                fileSize = self.getFileSize(tmp)
                if fileSize > 1024*1024*1024:###############文件大小>1G
                    subFileDir = 'D:\\05TMP\\'
                    shutil.rmtree(subFileDir)
                    subFilelist = self.FileSlicer(tmp, 'D:\\05TMP\\', 1024*1024*1024, 1024*1024)
                    hashList = [self.getBigFileSha256(j) for j in subFilelist]
                    sizeList = [self.getFileSize(j) for j in subFilelist]
                    appendList = self.calcFingerprint(hashList)
                    self.show_log(subFilelist)
                    self.show_log(hashList)
                    self.show_log(sizeList)
                    self.show_log(appendList)
                    for j in range(len(subFilelist)):
                        if j == 0:
                            fileInfo = json.dumps({'op':'newfile','size': sizeList[j], 'sha256': hashList[j]})                            
                        else:
##                            time.sleep(20)
                            fileInfo = json.dumps({'op': 'append','size': sizeList[j], 'sha256': hashList[j], 'hash': appendList[j]})                            
                        resp = self.StreamPartsAppender(url,driveUuid,dirUuid,listdsrc[i], subFilelist[j], headers, fileInfo)
                else:######################################文件大小<1G
                    resp = self.StreamFileUploader(url, driveUuid, dirUuid, tmp, headers)
                    if resp != 200:
                        msg = u'上传文件%s失败！' %tmp
                        self.show_log(msg)
                        self.log_write(msg, f)
                        result = 'FAIL'
                        return result
                    else:
                        msg = u'上传文件%s成功！' %tmp
                        self.show_log(msg)
                        self.log_write(msg, f)
            else:
                dirInfo = self.mkDirByHttp(url,driveUuid,dirUuid,listdsrc[i],headers)
                if dirInfo[0] != 200:
                    msg = u'在目录%s下创建目录%s失败！' %(dirUuid,listdsrc[i])
                    self.show_log(msg)
                    self.log_write(msg, f)
                    result = 'FAIL'
                    return result
                else:
                    dirInfo = self.getFileInfoByHttp(url,driveUuid,dirUuid,headers,listdsrc[i],'directory')
                    dirnUuid = dirInfo[1]['uuid']
                    result = self.uploadDirByHttp(url,headers,tmp+'\\',driveUuid,dirnUuid)
                    if result == 'FAIL':
                        return result
        return result
    def downloadDirByHttp(self,url,headers,dirPath,driveUuid,dirUuid,f):
        result = 'SUCCESS'
        entriesInfo = self.getDirInfoByHttp(url,driveUuid,dirUuid,headers,f)
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
                self.show_log('download '+fileName)
                if fileType == 'file':
                    downCode = self.downloadFile(str(url),str(driveUuid),str(dirUuid),str(entryUuid),str(fileName),str(dstFilePath),headers,f)
                    if downCode != 200:
                        msg = u'目录%s下文件%s下载失败！' %(dirUuid,fileName)
                        self.publicObj.show_log(msg)
                        self.publicObj.log_write(msg, f)
                        result = 'FAIL'
                        return result
                else:
                    os.mkdir(dstFilePath)
                    result = self.downloadDirByHttp(url,headers,dstFilePath,driveUuid,entryUuid,f)
                    if result == 'FAIL':
                        return result
            return result
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
    def SSH_Check(self,SSH_Ip,SSH_Port,SSH_Loginname,SSH_PASSword,SSH_until_tag,PS_Check,f):
        #创建SSH对象
        try:
            ssh = paramiko.SSHClient()
            #把要连接的机器添加到known_hosts文件中,跳过了远程连接中选择‘是’的环节
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #连接服务器
            ssh.connect(SSH_Ip,SSH_Port,SSH_Loginname,SSH_PASSword)
            time.sleep(2)
            msg=u'本次测试需要检查的进程有%s'%PS_Check
            self.show_log(msg)
            self.log_write(msg, f)
            for p in PS_Check:
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
######a=Public_Library()
######URL = 'http://13.0.0.1:3000/'
######driverUuid='d8e6e7eb-0aa9-43cc-beb2-903d19794857'
######dirUuid='0cd2d2c9-845c-40af-bd8e-14facbc03fb2'
######filePath=r'E:\test\2.txt'
######user_Token_headers={'Authorization': u'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiMWFjNjgyODgtNDNlNi00MTNlLTg5YzktOTg1ODNlMTZhODU5In0.xP43lYQ64SEhpgOzg9DyMUi4WURg-3Xf-ZcljsY9szA'}
######print a.getBigFileSha256(filePath)




##a.StreamFileUploader(URL,driverUuid,dirUuid,filePath,user_Token_headers)
####oldFilePath = dstSmbPath + listddst[i]
####newFilePath = dstSmbPath + 'new' + listddst[i]
####\\\\192.168.2.200\\admin\\smb\\document
####a.renameFileBySmb(self,oldFilePath,newFilePath)
####url = 'http://10.5.51.68:3000/'
####driveUuid='7f855894-1f3f-4584-ba2d-9587c761dae8'
####dirUuid='c12ef644-70a9-4f8a-8b50-18cf6892223a'
####tmp=r'E:\bigFile\document\K3C(B1)硬件PRD V1.0.1.doc'
####print chardet.detect(tmp)
####os.stat(tmp.decode('utf8'))
####a.getFileSize(tmp)
####tmp = r'E:\bigFile\document\about_debuggers.help.txt'
####headers={'content-type': 'multipart/form-data; boundary=b0e0d9c3d8594dc99e02eaa3831c6428', 'Authorization': u'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiYWFjM2YwN2ItNTNhMC00MmVmLThiODUtZTIyNTlkMmVjYTRlIn0._FJNf22bkJHEX4mUzatwPYzlo8ScFu4hpuZsLktMPVU'}
####a.uploadFileByMultiPartForm(url,driveUuid,dirUuid,tmp,headers)
####a.uploadFileByMultiPartForm(url,driveUuid,dirUuid,tmp,headers)
####a.StreamFileUploader(url,driveUuid,dirUuid,tmp,headers)
####
