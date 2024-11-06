from datetime import datetime
import requests, json, logging
from pyfcm import FCMNotification

from yellowsquash import env_constants

logger = logging.getLogger(__name__)

# push notification configuration
push_service = FCMNotification(api_key=env_constants.getFirebaseApiKey())


def notifyMobileAppUser(title, body, device_token=None, device_tokens=None, payload={}, small_img_url=None, large_img_url=None):
    """ sample value for payload
    payload : {
        "type":"OPEN_URL",
        "open_screen":"Screen Name",
        "type_summary":"New Update",
        "open_url":"any url to open"
    }
    """
    try:
        # if only one token available then motify one
        if device_token:
            result = push_service.notify_single_device(registration_id=device_token, message_title=title, message_body=body, data_message={
                "title": title,
                "large_img_url": small_img_url,
                "small_img_url": large_img_url,
                "body": body,
                "payload": payload,
                "click_action": "FLUTTER_NOTIFICATION_CLICK" 
            })

        # if request is came for multiple tokens then then motify all in one go
        if device_tokens:
            result = push_service.notify_multiple_devices(registration_ids=device_tokens, message_title=title, message_body=body, data_message={
                "title": title,
                "large_img_url": small_img_url,
                "small_img_url": large_img_url,
                "body": body,
                "payload": payload,
                "click_action": "FLUTTER_NOTIFICATION_CLICK" 
            })
    except BaseException as err:
        logger.exception("failed sending firebase notification to users : ", exc_info=err)


# channel : string
# data : dict format/json parsable
def centrifugePublish(channel, data):
    try:
        contentType = "application/x-www-form-urlencoded; charset=UTF-8"
        
        # get centri token with password
        getCentriTokenUri = env_constants.getCentrifugeBaseUrl() + "auth"
        getCentriTokenResp = requests.post(getCentriTokenUri, data=env_constants.getCentrifugePassword(), headers={
            "Content-Type": contentType
        })
        
        # publish on centri with token
        reqData = json.dumps({
            "method": "publish",
            "params": {
                "channel": channel,
                "data": data
            }
        })
        reqHeaders = {
            'Content-type': contentType, 
            'Authorization': 'token ' + getCentriTokenResp.json().get('token')
        }
        publishCentriUri = env_constants.getCentrifugeBaseUrl() + "api"
        resp = requests.post(publishCentriUri, data=reqData, headers=reqHeaders)

    except BaseException as err:
        logger.exception("failed publishing data on wbsocket for the channel : {}".format(channel), exc_info=err)
