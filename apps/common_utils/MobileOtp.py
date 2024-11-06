import requests
import json
from django.conf import settings

class Otp:
    def MobileOtp(self, mobile, otp):
        otpUrl = 'https://2factor.in/API/V1/{0}/SMS/+91{1}/{2}/'.format(
            settings.API_KEY_2FACTOR,
            mobile,
            otp
        )
        resp = requests.get(otpUrl)
        return resp.json()

    def EmailOtp(self,task):
        respdata = requests.post('https://api.sendinblue.com/v3/smtp/email',
                    data=json.dumps(task),
                    headers={
                        'Content-Type':'application/json',
                        'api-key':'{0}'.format(settings.API_KEY_SENDINBLUE)
                    })
        return respdata.json()
