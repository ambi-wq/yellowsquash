import requests
import json
from django.conf import settings

class SendEmailBlueBirdAPI:

    def send_mail(mail):
        respdata = requests.post('https://api.sendinblue.com/v3/smtp/email',
                    data=json.dumps(mail),
                    headers={
                        'Content-Type':'application/json',
                        'api-key':'{0}'.format(settings.API_KEY_SENDINBLUE)
                    })
        return respdata.json()