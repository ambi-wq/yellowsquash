from django.urls import path
from django.conf.urls import url
from .views import CustomTokenObtainPairView, ResetPassword, ForgotPassword, VerifyOtp, ResetForgotPassword,GetUpdatePasswordToken


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('reset-password/', ResetPassword.as_view(), name='reset/change password'),
    path('forgot/', ForgotPassword.as_view(), name='forgot password mail for opt'),
    path('verify-otp/', VerifyOtp.as_view(), name='verify otp'),
    path('reset-forgot-password/', ResetForgotPassword.as_view(), name='forgot password mail for opt'),
    path('update-password-token/', GetUpdatePasswordToken.as_view(),name=" get update password token for ananymous user"),

]

