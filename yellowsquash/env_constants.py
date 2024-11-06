import os




# set envirssh 103.11.153.185oment based constant values
if os.environ.get('ENV', None) == 'prod':
    TinodeChannel = "ys-messages.opskube.com:16060"
    JitsiIss = "ys-meetings_app_id"
    JitsiSub = "ys-meetings.opskube.com"
    JitsiPasswordSecret = "Password2020"
    RazorpayKey = 'rzp_live_j36VAC42H8fbk4'
    RazorpaySecret = '4AYGN2Wqi4DSGKKkcS2ALt58'

    FirebaseApiKey="AAAAtG26RJ4:APA91bEx7iCSzuVq-O0rJPpeDgCl9LZ-Ra8gvnRDywjwjj193UTL_JAW2xVao16uWZRJYHdBgENjDKeMwlZOdOfjtiZ5QB_R88bBoN5tnRaqtU4GEMyGg5uUgshk_TGKA6TezFln3L14"
    CentrifugeBaseUrl = "https://account.aadeshtravels.com/centrifugo/admin/"
    CentrifugePassword = "password=8cf126e5-0e61-47bc-9832-e9fa1ea5ff39"
elif os.environ.get('ENV', None) == 'stage':
    TinodeChannel = "ys-messages.opskube.com:16060"
    JitsiIss = "ys-meetings_app_id"
    JitsiSub = "ys-meetings.opskube.com"
    JitsiPasswordSecret = "Password2020"
    RazorpayKey = 'rzp_test_0cl0ai7afvxeCb'
    RazorpaySecret = 'h0ag7Fm8PLkbyzFV0eJMbbYT'
    FirebaseApiKey="AAAAtG26RJ4:APA91bEx7iCSzuVq-O0rJPpeDgCl9LZ-Ra8gvnRDywjwjj193UTL_JAW2xVao16uWZRJYHdBgENjDKeMwlZOdOfjtiZ5QB_R88bBoN5tnRaqtU4GEMyGg5uUgshk_TGKA6TezFln3L14"
    CentrifugeBaseUrl = "https://account.aadeshtravels.com/centrifugo/admin/"
    CentrifugePassword = "password=8cf126e5-0e61-47bc-9832-e9fa1ea5ff39"
else:
    TinodeChannel = "ys-messages.opskube.com:16060"
    JitsiIss = "ys-meetings_app_id"
    JitsiSub = "ys-meetings.opskube.com"
    JitsiPasswordSecret = "Password2020"
    RazorpayKey = 'rzp_test_0cl0ai7afvxeCb'
    RazorpaySecret = 'h0ag7Fm8PLkbyzFV0eJMbbYT'

    #RazorpayKey = "rzp_live_4lCt8GYpSQ4eb9"
    #RazorpaySecret = "GEfQJzI3TI8WDzB04sOjt9vd"
    # RazorpayKey = "rzp_test_ttaeIJ7VYvfqJd"
    # RazorpaySecret = "Pqx2XCrxiXTONdwdMkpaW0Ch"
    FirebaseApiKey="AAAAtG26RJ4:APA91bEx7iCSzuVq-O0rJPpeDgCl9LZ-Ra8gvnRDywjwjj193UTL_JAW2xVao16uWZRJYHdBgENjDKeMwlZOdOfjtiZ5QB_R88bBoN5tnRaqtU4GEMyGg5uUgshk_TGKA6TezFln3L14"
    CentrifugeBaseUrl = "https://account.aadeshtravels.com/centrifugo/admin/"
    CentrifugePassword = "password=8cf126e5-0e61-47bc-9832-e9fa1ea5ff39"


def getTinodeChannel():
    return TinodeChannel

def getJitsiIss():
    return JitsiIss

def getJitsiSub():
    return JitsiSub

def getJitsiPasswordSecret():
    return JitsiPasswordSecret

def getRazorpayKey():
    return RazorpayKey

def getRazorpaySecret():
    return RazorpaySecret

def getFirebaseApiKey():
    return FirebaseApiKey

def getCentrifugeBaseUrl():
    return CentrifugeBaseUrl

def getCentrifugePassword():
    return CentrifugePassword
    