import argparse
import sys
import grpc
from tinode_grpc import pb
from tinode_grpc import pbx
import queue
import json
import datetime
from google.protobuf.json_format import MessageToDict
import pkg_resources
import platform
import random
import time
import logging
import jwt
from django.conf import settings
from yellowsquash import env_constants

logger = logging.getLogger(__name__)


if sys.version_info[0] >= 3:
    unicode = str



class Tinode:

    MAX_LOG_LEN = 64
    APP_NAME = "tn-cli"
    APP_VERSION = "1.5.5"
    PROTOCOL_VERSION = "0"
    LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
    GRPC_VERSION = pkg_resources.get_distribution("grpcio").version
    onCompletion = {}
    WaitingFor = None
    Variables = {}
    queue_out = None
    channel = None
    stream = None
    token=None
    user=None
    group=None
    id = random.randint(10000,60000)
    terminationId = str(0)
    terminateOnFailure = True

    def __init__(self):
        self.queue_out = queue.Queue()
        logger.info("############################ "+ env_constants.getTinodeChannel() + " ####################################")
        self.channel = grpc.insecure_channel(env_constants.getTinodeChannel())
        self.stream = pbx.NodeStub(self.channel).MessageLoop(self.generate())


    def generate(self):
        while True:
            msg = self.queue_out.get()
            if msg == None:
                return
            #("out:", self.to_json(msg))
            yield msg


    def post(self, msg):
        self.queue_out.put(msg)


    def parse_cred(self, cred):
        result = None
        if cred != None:
            result = []
            for c in cred.split(","):
                parts = c.split(":")
                result.append(pb.ClientCred(method=parts[0] if len(parts) > 0 else None,
                    value=parts[1] if len(parts) > 1 else None,
                    response=parts[2] if len(parts) > 2 else None))

        return result


    def to_json(self, msg):
        return json.dumps(self.clip_long_string(MessageToDict(msg)))


    def clip_long_string(self, obj):
        if isinstance(obj, unicode) or isinstance(obj, str):
            if len(obj) > self.MAX_LOG_LEN:
                return '<' + str(len(obj)) + ' bytes: ' + obj[:12] + '...' + obj[-12:] + '>'
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self.clip_long_string(item) for item in obj]
        elif isinstance(obj, dict):
            return dict((key, self.clip_long_string(val)) for key, val in obj.items())
        else:
            return obj


    def client_message_loop(self):
        try:
            # Read server responses
            for msg in self.stream:
                print(msg)
                if msg.HasField("ctrl"):
                    self.handle_ctrl(msg.ctrl)
                    # Run code on command completion
                elif msg.HasField("data"):
                    logger.info("message from:", msg.data.from_user_id)
                elif msg.HasField("pres"):
                    logger.info("presence:", msg.pres.topic, msg.pres.what)
                else:
                    logger.info("else")
                    # Ignore everything else
                    pass
            return
            logger.info("prcessong done!")

        except grpc._channel._Rendezvous as err:
            logger.exception("Disconnected:", exc_info=err)


    def handle_ctrl(self, ctrl):
        
        # bind data into nice
        nice = {}
        for p in ctrl.params:
            nice[p] = json.loads(ctrl.params[p])
        logger.info(nice)

        if 'token' in nice:
            self.token = nice.get('token')
        
        if 'desc' in nice and 'user' in nice:
            self.user = nice.get('user')

        if hasattr(ctrl, 'topic'):
            self.group = ctrl.topic

        if ctrl.id == self.terminationId:
            self.channel.close()

        if ctrl.code >= 400:
            logger.info(str(ctrl.code) + " " + ctrl.text)
            if self.terminateOnFailure:
                time.sleep(1)
                self.channel.close()
                raise Exception(str(ctrl.code) + " " + ctrl.text)

    # {hi}
    def hiMsg(self, id):
        background = None
        return pb.ClientMsg(hi=pb.ClientHi(id=str(id), user_agent=self.APP_NAME + "/" + self.APP_VERSION + " (" +
            platform.system() + "/" + platform.release() + "); gRPC-python/" +
                            self.LIB_VERSION + "+" + self.GRPC_VERSION,
            ver=self.LIB_VERSION, lang="EN", background=background))

    # {login}
    def loginMsg(self, id, username, password):
        return pb.ClientMsg(login=pb.ClientLogin(id=str(id), scheme="basic", 
            secret=str(username+':'+password).encode('utf-8'),cred=self.parse_cred(username+':'+password)))


    def AccMsg(self, id, username, password, tags, first_name):
        # acc --scheme=basic --secret=test:test123 --fn='Test User' --photo=./test-128.jpg --tags=test,test-user --do-login --auth=JRWPA --anon=JW
        return pb.ClientMsg(acc=pb.ClientAcc(id=str(id), user_id='new', state=None,
                scheme="basic", secret=str(username+':'+password).encode('utf-8'), login=False, tags=tags,
                desc=pb.SetDesc(default_acs=pb.DefaultAcsMode(auth='', anon=''),
                    public=str('{"fn": "'+first_name+'"}').encode('utf-8'), private=None),
                cred=self.parse_cred(username+':'+password)), on_behalf_of=None)


    def subUserMsg(self, id, userKey):
        """
        sub new --fn='Test Group' --tags=test,test-group --auth=JRWPA --anon=JR
        """
        return pb.ClientMsg(sub=pb.ClientSub(id=str(id), topic=userKey,
            set_query=pb.SetQuery(desc=pb.SetDesc(public=None, private=None, default_acs=pb.DefaultAcsMode(auth='', anon='')),
                sub=pb.SetSub(mode=None),
                tags=None),
            get_query=None), on_behalf_of=None)


    def createGroupMsg(self, id, groupName, tags):
        """
        sub new --fn='Test Group' --tags=test,test-group --auth=JRWPA --anon=JR
        """
        return pb.ClientMsg(sub=pb.ClientSub(id=str(id), topic='new',
            set_query=pb.SetQuery(
                desc=pb.SetDesc(public=str('{"fn": "'+groupName+'"}').encode('utf-8'), private=None, default_acs=pb.DefaultAcsMode(auth='', anon='')),
                sub=pb.SetSub(mode=None),
                tags=tags),
            get_query=None), on_behalf_of=None)


    def setMsg(self, id, chatGroupKey, tinodeUserKey):
        """
        set grpojSLu0SdEXg --user=usrHewts8c8fsU
        """
        return pb.ClientMsg(set=pb.ClientSet(id=str(id), topic=chatGroupKey,
            query=pb.SetQuery(desc=pb.SetDesc(default_acs=pb.DefaultAcsMode(auth='', anon=''), public=None, private=None),
            sub=pb.SetSub(user_id=tinodeUserKey, mode=None),
            tags=None,
            cred=None)), on_behalf_of=None)


    # {del}
    def delUser(self, id, userKeyToDelete):

        msg = pb.ClientMsg(on_behalf_of=None)
        # Field named 'del' conflicts with the keyword 'del. This is a work around.
        xdel = getattr(msg, 'del')
        """
        setattr(msg, 'del', pb.ClientDel(id=str(id), topic=topic, what=enum_what, hard=hard,
            del_seq=seq_list, user_id=user))
        """
        xdel.id = str(id)
        xdel.what = pb.ClientDel.USER
        xdel.hard = True
        xdel.del_seq.extend([])
        xdel.user_id = userKeyToDelete
        # xdel.topic = None
        # xdel.cred = None

        return msg

 
    def delGroup(self, id, groupKeyToDelete):

        msg = pb.ClientMsg(on_behalf_of=None)
        # Field named 'del' conflicts with the keyword 'del. This is a work around.
        xdel = getattr(msg, 'del')
        """
        setattr(msg, 'del', pb.ClientDel(id=str(id), topic=topic, what=enum_what, hard=hard,
            del_seq=seq_list, user_id=user))
        """
        xdel.id = str(id)
        xdel.what = pb.ClientDel.TOPIC
        xdel.hard = True
        xdel.del_seq.extend([])
        # xdel.user_id = None
        xdel.topic = groupKeyToDelete
        # xdel.cred = None

        return msg


    def leaveGroup(self, id, groupKeyToLeave):
        msg = pb.ClientMsg(leave=pb.ClientDel(id=str(id), topic=groupKeyToLeave, unsub=True),
        on_behalf_of=None)
        return msg


    def CreateUserAndGetToken(self, username, password, tags=['customer'], first_name='User'):
        try:
            if not first_name:
                first_name = 'User'

            if not tags:
                tags = ['customer']

            id = self.id
                
            self.post(self.hiMsg(id=id,))

            id = id + 1
            self.post(self.AccMsg(
                id=id,
                username=username,
                password=password,
                tags=tags,
                first_name=first_name
            ))

            id = id + 1
            self.terminationId = str(id)
            self.post(self.loginMsg(
                id=id,
                username=username,
                password=password
            ))
        
            self.client_message_loop()

            # wait for create user
            for i in range(5):
                if self.user and None != self.user:
                    break
                else:
                    time.sleep(1)

            # wait for token to get
            for i in range(5):
                if self.token and None != self.token:
                    break
                else:
                    time.sleep(1)

            logger.info(self.token)


            access_token_payload = {
                'tinode_user_id': self.user,
                'username': username,
                'password': password,
            }
            access_token = jwt.encode(access_token_payload,
                                    settings.SECRET_KEY, algorithm='HS256')

            return access_token

        except BaseException as err:
            logger.exception("Error While Getting Tinode Token : ", exc_info=err)
            return ""


    def CreateChatGroup(self, adminUserToken, userToken, groupName, tags=['program']):
        try:

            if not tags:
                tags = ['program']

            id = self.id
                

            adminUserData = jwt.decode(
                adminUserToken, settings.SECRET_KEY, algorithms=['HS256'])

            userData = jwt.decode(
                userToken, settings.SECRET_KEY, algorithms=['HS256'])

            # set credential to session
            self.post(self.hiMsg(id=id,))

            # login into session
            id = id + 1
            self.post(self.loginMsg(
                id=id,
                username=adminUserData.get('username'),
                password=adminUserData.get('password')
            ))

            # create group
            id = id + 1
            self.terminationId = str(id)
            self.post(self.createGroupMsg(
                id=id,
                groupName=groupName,
                tags=tags
            ))

            self.client_message_loop()

            # wait for create user
            for i in range(5):
                if self.group and None != self.group:
                    break
                else:
                    time.sleep(1)

            logger.info(self.group)

            return self.group

        except BaseException as err:
            logger.exception("Error While Creating Chat group : ", exc_info=err)
            return ""


    def AddUserToChatGroup(self, adminUserToken, userToken, tinodeGroupkey):
        try:

            id = self.id    
            self.terminateOnFailure = False
            
            adminUserData = jwt.decode(
                adminUserToken, settings.SECRET_KEY, algorithms=['HS256'])

            userData = jwt.decode(
                userToken, settings.SECRET_KEY, algorithms=['HS256'])


            # set credential to session
            self.post(self.hiMsg(id=id,))

            # login into session
            id = id + 1
            self.post(self.loginMsg(
                id=id,
                username=adminUserData.get('username'),
                password=adminUserData.get('password')
            ))

            time.sleep(1)

            # subscribe user to admin
            id = id + 1
            self.post(self.subUserMsg(
                id=id,
                userKey=userData.get('tinode_user_id'),
            ))

            time.sleep(1)

            # subscribe group to admin
            id = id + 1
            self.post(self.subUserMsg(
                id=id,
                userKey=tinodeGroupkey,
            ))

            time.sleep(1)

           # add user to group
            id = id + 1
            self.terminationId = str(id)
            self.post(self.setMsg(
                id=id,
                chatGroupKey=tinodeGroupkey,
                tinodeUserKey=userData.get('tinode_user_id')
            ))

            self.client_message_loop()

            return None

        except BaseException as err:
            logger.exception("Error While adding user to chat group : ", exc_info=err)
            return ""


    def ConnectUser1ToUser2(self, user1Token, user2Token):
        try:

            id = self.id
            
            user1Data = jwt.decode(
                user1Token, settings.SECRET_KEY, algorithms=['HS256'])

            user2Data = jwt.decode(
                user2Token, settings.SECRET_KEY, algorithms=['HS256'])


            # set credential to session
            self.post(self.hiMsg(id=id,))

            # login into session
            id = id + 1
            self.post(self.loginMsg(
                id=id,
                username=user1Data.get('username'),
                password=user1Data.get('password')
            ))

            time.sleep(1)

            # subscribe user to admin
            id = id + 1
            self.terminationId = str(id)
            self.post(self.subUserMsg(
                id=id,
                userKey=user2Data.get('tinode_user_id'),
            ))

            self.client_message_loop()

            return None

        except BaseException as err:
            logger.exception("Error occured While connecting two users ", exc_info=err)
            return ""


    def DeleteProgramChatGroup(self, groupAdminToken, tinodeGroupkey):
        try:
            id = self.id
            
            adminData = jwt.decode(
                groupAdminToken, settings.SECRET_KEY, algorithms=['HS256'])

            # set credential to session
            self.post(self.hiMsg(id=id,))

            # login into session
            id = id + 1
            self.post(self.loginMsg(
                id=id,
                username=adminData.get('username'),
                password=adminData.get('password')
            ))
            time.sleep(1)

            # subscribe group to admin
            id = id + 1
            self.post(self.subUserMsg(
                id=id,
                userKey=tinodeGroupkey,
            ))
            time.sleep(1)

            # subscribe user to admin
            id = id + 1
            self.terminationId = str(id)
            self.post(self.delGroup(
                id=id,
                groupKeyToDelete=tinodeGroupkey,
            ))
            time.sleep(1)

            self.client_message_loop()

            return None

        except BaseException as err:
            logger.exception("Error While Getting Tinode Token : ", exc_info=err)
            return None


    def LeaveUserGroupChat(self, userToken, tinodeGroupkey):
        try:
            id = self.id
            userData = jwt.decode(
                userToken, settings.SECRET_KEY, algorithms=['HS256'])
            
            # set credential to session
            self.post(self.hiMsg(id=id,))
            
            # login into session
            id = id + 1
            self.post(self.loginMsg(
                id=id,
                username=userData.get('username'),
                password=userData.get('password')
            ))
            
            time.sleep(1)
            
            # user leave group
            id = id + 1
            self.terminationId = str(id)
            self.post(self.leaveGroup(
                id=id,
                groupKeyToLeave=tinodeGroupkey,
            ))
            time.sleep(1)
            
            self.client_message_loop()
            return None
        
        except BaseException as err:
            logger.exception("Error While user leaving group : ", exc_info=err)
            return None
