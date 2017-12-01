#!/usr/bin/python
#coding: UTF-8
#######
# Copyright FUJITSU LIMITED 2017
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######

# import
import json
import re
from os import path
from ansible.module_utils.ism_user_settings import *

# common class
class IsmCommon:

    # constant
    TIME_OUT_SECOND = "60"
    COMMAND = "curl -S -s -m " + TIME_OUT_SECOND + " "
    GET = " -X GET "
    POST = " -X POST -d "
    PATCH = " --request PATCH -d "
    HEADER = " -H 'Content-Type: application/json' "
    HTTP_RESPONSE_CODE = " -w 'ISM_HTTP_RESPONSE_CODE=%{http_code}' "
    CERTIFICATE = " --cacert "
    UNICODE_STRING = "utf-8"
    
    # rest url
    LOGIN_REST_URL = "/ism/api/v2/users/login"
    GET_NODE_OS_REST_URL = "/ism/api/v2/nodes/os"
    LOGOUT_REST_URL = "/ism/api/v2/users/logout"
    NODE_LIST_REST_URL = "/ism/api/v2/nodes"
    
    def __init__(self, module):
        self.ism_ip = ""
        self.ism_port_no = ""
        self.user_name = ""
        self.password = ""
        self.certificate = ""
        self.session_id = ""
        self.node_id = ""
        self.module = module
        
#   ***** set method *****

    # set the ip address of ISM
    def setIsmIp(self, ism_ip):
        self.ism_ip = ism_ip

    # set port number of ISM
    def setIsmPortNo(self, ism_port_no):
        self.ism_port_no = ism_port_no

    # set login user name of ISM
    def setIsmUserName(self, user_name):
        self.user_name = user_name

    # set login password of ISM
    def setIsmPassword(self, password):
        self.password = password

    # set certificate of ISM
    def setIsmCertificate(self, certificate):
        self.certificate = certificate

    # set session id
    def setSessionId(self, session_id):
        self.session_id = session_id

    # set node id
    def setNodeId(self, node_id):
        self.node_id = str(node_id)
        
#   ***** set method *****



#   ***** get method *****

    # get ip of ISM
    def getIsmIp(self):
        return self.ism_ip

    # get port number of ISM
    def getIsmPortNo(self):
        return self.ism_port_no

    # get login user name of ISM
    def getIsmUserName(self):
        return self.user_name

    # get login password of ISM
    def getIsmPassword(self):
        return self.password

    # get certificate of ISM
    def getIsmCertificate(self):
        return self.certificate

    # get session id
    def getSessionId(self):
        return self.session_id

    # get node id
    def getNodeId(self):
        return self.node_id

    # get rest url
    def getRestUrl(self, rest_url, param = ""):
        if param != "":
            rest_url = "https://" + self.getIsmIp() + ":" + self.getIsmPortNo() + rest_url + str(param)
        else:
            rest_url = "https://" + self.getIsmIp() + ":" + self.getIsmPortNo() + rest_url
        return rest_url
        
#   ***** get method *****


#   ***** escape method *****
    # singlequote escape
    def singleEscape(self, str):
        escape_str = str.replace("'","'\\''")
        return escape_str

#   ***** escape method *****


#   *****  unicode method *****
    # run_command_unicode
    def run_command_unicode(self, exec_command):
        (rc, stdout, stderr) = self.module.run_command(exec_command)
        return (rc, unicode(stdout, IsmCommon.UNICODE_STRING), unicode(stderr, IsmCommon.UNICODE_STRING))

    # convert to unicode string
    def covert_unicode(self, str_var):
        if str_var is not None:
            convert_str = unicode(str_var, IsmCommon.UNICODE_STRING)
            return convert_str
        else:
            return str_var
        
#   ***** unicode method *****


#   ***** param check method *****
    # param check
    def param_check(self, firmware_update_list):
        required_keys = ["firmware_name", "repository_name", "operation_mode"]
        
        # firmware_update_list
        # [
        #    {'repository_name': 'Individual Repository Administrator',
        #     'firmware_version': '8.43F&3.60',
        #     'operation_mode': 'Online',
        #     'firmware_name': 'RX200 S8_iRMC'
        #     },
        #    {'repository_name': 'Individual Repository Administrator',
        #     'firmware_version': 'R1.11.0',
        #     'operation_mode': 'Online',
        #     'firmware_name': 'RX200 S8_BIOS'
        #    }
        # ]
        
        for param_hash in firmware_update_list:
            for key in required_keys:
                if key not in param_hash:
                    self.module.log("missing required arguments: " + key)
                    self.module.fail_json(msg="missing required arguments: " + key)
                if param_hash[key] == "" or param_hash[key] is None:
                    self.module.log("no value key: " + key)
                    self.module.fail_json(msg="no value key: " + key)
                param_hash[key] = self.covert_unicode(param_hash[key])
                
            if "firmware_version" in param_hash:
                param_hash['firmware_version'] = self.covert_unicode(param_hash['firmware_version'])
                
#   ***** param check method *****


#   ***** common function *****

    # ism login
    def ismLogin(self, data):
        try :
            self.module.debug("***** ismLogin Start *****")
            
            # setting up ISM connection infomation
            self.setIsmIp(data["ip"])
            self.setIsmPortNo(data["portNo"])
            self.setIsmUserName(data["credentials"]["userName"])
            self.setIsmPassword(data["credentials"]["password"])
            self.setIsmCertificate(data["certificate"])
            
            # get rest url
            rest_url = self.getRestUrl(IsmCommon.LOGIN_REST_URL)
            
            # execute rest
            param =  " '{\"IsmBody\": {\"UserName\":\"" + self.getIsmUserName() + "\",\"Password\":\"" + self.getIsmPassword() + "\"}}' "
            exec_command = IsmCommon.COMMAND + rest_url + IsmCommon.HEADER + IsmCommon.POST + param + IsmCommon.HTTP_RESPONSE_CODE + IsmCommon.CERTIFICATE + "'" + self.singleEscape(self.getIsmCertificate()) + "'"
            self.module.debug("exec_command = " + exec_command)
            
            (rc, stdout, stderr) = self.run_command_unicode(exec_command)
            self.module.debug("rc = " + str(rc))
            self.module.debug("stdout = " + stdout)
            
            if str(rc) != "0":
                self.module.log("curl communication error: stdout=" + stdout + ". stderr=" + stderr + ". exec_command=" + exec_command)
                self.module.fail_json(msg="curl communication error: " + stderr)
                
            ism_login_result = re.search(r'(.+)ISM_HTTP_RESPONSE_CODE=(\d+)', stdout.replace('\n', ''))
            
            if ism_login_result is None:
                self.module.log("REST result is fault: stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                self.module.fail_json(msg="REST result is fault: " + stderr)
            else:
                if ism_login_result.group(2) == "201":
                    try :
                        json_data = json.loads(ism_login_result.group(1))
                    except Exception as e:
                        self.module.log("Not json format data: e=" + str(e) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                        self.module.fail_json(msg="Not json format data: " + ism_login_result.group(1))
                    
                    # set session id
                    self.setSessionId(json_data["IsmBody"]["Auth"])
                else:
                    self.module.log("Response Code=" + ism_login_result.group(2) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                    self.module.fail_json(msg=ism_login_result.group(1))
                
            self.module.debug("***** ismLogin End *****")
        except Exception as e:
            self.module.log(str(e))
            self.module.fail_json(msg=str(e))
            
    # ism logout
    def ismLogout(self):
        try :
            self.module.debug("***** ismLogout Start *****")
            
            # get rest url
            rest_url = self.getRestUrl(IsmCommon.LOGOUT_REST_URL)
            
            # adding a response header
            add_head = " -H 'X-Ism-Authorization: " + self.getSessionId() + "' "
            
            # execute rest
            exec_command = IsmCommon.COMMAND + rest_url + IsmCommon.HEADER + add_head + IsmCommon.HTTP_RESPONSE_CODE + IsmCommon.CERTIFICATE + "'" + self.singleEscape(self.getIsmCertificate()) + "'"
            self.module.debug("exec_command = " + exec_command)
            
            (rc, stdout, stderr) = self.run_command_unicode(exec_command)
            self.module.debug("rc = " + str(rc))
            self.module.debug("stdout = " + stdout)
            
            if str(rc) != "0":
                self.module.log("curl communication error: stdout=" + stdout + ". stderr=" + stderr + ". exec_command=" + exec_command)
                self.module.fail_json(msg="curl communication error: " + stderr)
                
            ism_logout_result = re.search(r'(.+)ISM_HTTP_RESPONSE_CODE=(\d+)', stdout.replace('\n', ''))
            
            if ism_logout_result is None:
                self.module.log("REST result is fault: stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                self.module.fail_json(msg="REST result is fault: " + stderr)
            else:
                if ism_logout_result.group(2) != "201":
                    self.module.log("Response Code=" + ism_logout_result.group(2) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                    self.module.fail_json(msg=ism_logout_result.group(1))
                
            self.module.debug("***** ismLogout End *****")
        except Exception as e:
            self.module.log(str(e))
            self.module.fail_json(msg=str(e))
            
    # get node OS
    def getNodeOS(self):
        try :
            self.module.debug("***** getNodeOS Start *****")
            
            # get rest url
            rest_url = self.getRestUrl(IsmCommon.GET_NODE_OS_REST_URL)
            
            # adding a response header
            add_head = " -H 'X-Ism-Authorization: " + self.getSessionId() + "' "
            
            # execute rest
            exec_command = IsmCommon.COMMAND + rest_url + IsmCommon.HEADER + add_head + IsmCommon.GET + IsmCommon.HTTP_RESPONSE_CODE + IsmCommon.CERTIFICATE + "'" + self.singleEscape(self.getIsmCertificate()) + "'"
            self.module.debug("exec_command = " + exec_command)
            
            (rc, stdout, stderr) = self.run_command_unicode(exec_command)
            self.module.debug("rc = " + str(rc))
            self.module.debug("stdout = " + stdout)
            
            if str(rc) != "0":
                self.module.log("curl communication error: stdout=" + stdout + ". stderr=" + stderr + ". exec_command=" + exec_command)
                self.module.fail_json(msg="curl communication error: " + stderr)
                
            get_node_os_result = re.search(r'(.+)ISM_HTTP_RESPONSE_CODE=(\d+)', stdout.replace('\n', ''))
            
            if get_node_os_result is None:
                self.module.log("REST result is fault: stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                self.module.fail_json(msg="REST result is fault: " + stderr)
            else:
                if get_node_os_result.group(2) == "200":
                    try :
                        json_data = json.loads(get_node_os_result.group(1))
                    except Exception as e:
                        self.module.log("REST result is fault: stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                        self.module.fail_json(msg="REST result is fault: " + stderr)
                    
                    for list in json_data["IsmBody"]["Hosts"]:
                        if (list["OsIpAddress"] == self.module.params['hostname']):
                            self.setNodeId(list["NodeId"])
                            break
                else:
                    self.module.log("Response Code=" + get_node_os_result.group(2) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                    self.module.fail_json(msg=get_node_os_result.group(1))
                
            self.module.debug("***** getNodeOS End *****")
            
        except Exception as e:
            self.module.log(str(e))
            self.module.fail_json(msg=str(e))
            
    # get node Hard
    def getNodeHard(self):
        try :
            self.module.debug("***** getNodeHard Start *****")
            
            # get rest url
            rest_url = self.getRestUrl(IsmCommon.NODE_LIST_REST_URL, "?ipaddress=" + self.module.params['hostname'])
            
            # adding a response header
            add_head = " -H 'X-Ism-Authorization: " + self.getSessionId() + "' "
            
            # execute rest
            exec_command = IsmCommon.COMMAND + rest_url + IsmCommon.HEADER + add_head + IsmCommon.GET + IsmCommon.HTTP_RESPONSE_CODE + IsmCommon.CERTIFICATE + "'" + self.singleEscape(self.getIsmCertificate()) + "'"
            self.module.debug("exec_command = " + exec_command)
            
            (rc, stdout, stderr) = self.run_command_unicode(exec_command)
            self.module.debug("rc = " + str(rc))
            self.module.debug("stdout = " + stdout)
            
            if str(rc) != "0":
                self.module.log("curl communication error: stdout=" + stdout + ". stderr=" + stderr + ". exec_command=" + exec_command)
                self.module.fail_json(msg="curl communication error: " + stderr)
                
            get_node_hard_result = re.search(r'(.+)ISM_HTTP_RESPONSE_CODE=(\d+)', stdout.replace('\n', ''))
            
            if get_node_hard_result is None:
                self.module.log("REST result is fault: stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                self.module.fail_json(msg="REST result is fault: " + stderr)
            else:
                if get_node_hard_result.group(2) == "200":
                    try :
                        json_data = json.loads(get_node_hard_result.group(1))
                    except Exception as e:
                        self.module.log("Not json format data: e=" + str(e) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                        self.module.fail_json(msg="Not json format data: " + get_node_hard_result.group(1))
                    if json_data["IsmBody"]["Nodes"]:
                        self.setNodeId(json_data["IsmBody"]["Nodes"][0]["NodeId"])
                else:
                    self.module.log("Response Code=" + get_node_hard_result.group(2) + ", stdout=" + stdout + ", stderr=" + stderr + ", exec_command=" + exec_command)
                    self.module.fail_json(msg=get_node_hard_result.group(1))
                
            self.module.debug("***** getNodeHard End *****")
        except Exception as e:
            self.module.log(str(e))
            self.module.fail_json(msg=str(e))
            
#   ***** common function *****
