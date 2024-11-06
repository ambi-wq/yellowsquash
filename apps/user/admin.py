from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from apps.common_utils.MobileOtp import Otp
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)
from .models import (
    User,
    Group,
    Permission,
    GroupPermission,
    Category,
    UserIntrestOrExpertise,
    UserIntrestOrExpertise,
    UserEducationDetail,
    UserDeviceToken,
    UserOrder,
    Location,
    TimeZone,
    Languages,
    Expertise,
    ExpertTeamMember,
    Role,
    DegreeCertification
)


class CategoryInline(admin.TabularInline):
    model = UserIntrestOrExpertise
    extra = 0


class UserEducationDetailInline(admin.TabularInline):
    model = UserEducationDetail
    extra = 0
    show_change_link = True

    
class UserAdmin(admin.ModelAdmin):
    search_fields = ('id', 'username', 'first_name', 'last_name', 'email', 'mobile')
    list_filter = [
        ('category', RelatedDropdownFilter), 
        ('user_type'), 
        ('is_verified'),
        ('status'),
    ]
    list_display = 'id', 'profile_picture', 'email', 'mobile', 'first_name', 'last_name', 'user_type', 'is_verified', 'professional_title', 'created_at', 'last_updated_at'
    fields = ('profile_picture', 'username', 'first_name', 'last_name', 'mobile', 'mobile_verified', 'email', 'email_verified', 
    'is_verified', 'user_type', 'password', 'expert_score', 'status', 'short_description', 'fb_link', 'twitter_link', 'linked_link', 'google_link', 'language', 'professional_title', 'location', 
    'video_url', 'is_profile_complete')
    #readonly_fields = ['profile_picture']
    inlines = [
        CategoryInline,
        UserEducationDetailInline
    ]
    def get_ordering(self, request):
        return ['-last_updated_at']
    '''
    def save_model(self, request, obj, form, change):
        sendOtp = Otp()
        prevStatus = User.objects.get(pk=obj.pk)
        #expert get a email when his account is going to be inactive to active
        if obj.status == 'active' and prevStatus.status == 'inactive'  and obj.user_type =='expert':
            task={  
                "sender":{  
                    "name":"YellowSquash",
                    "email":"yellowsquash@gmail.com"
                },
                "to":[  
                    {  
                        "email":"{0}".format(obj.email),
                        "name":"yellowsaquash"
                    }
                ],
                "templateId":29,
                "params":{"first_name":"{0}".format(obj.first_name)}
            }
            sendOtp.EmailOtp(task)

        obj.save()
        '''



admin.site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = 'name','created_by', 'updated_by', 'created_by', 'updated_by', 'created_at', 'last_updated_at'

admin.site.register(Group, GroupAdmin)


class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description', 'status')
    list_display = 'name', 'description', 'status', 'created_by', 'updated_by', 'created_at', 'last_updated_at'

admin.site.register(Permission, PermissionAdmin)


class GroupPermissionAdmin(admin.ModelAdmin):
    search_fields = ('is_access', 'group__name', 'permission__name')
    list_display = 'group', 'permission', 'is_access', 'created_by', 'updated_by', 'created_at', 'last_updated_at', 'status'

admin.site.register(GroupPermission, GroupPermissionAdmin)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = 'name', 'logo_tag'
    exclude = ('logo',) # no need to show logo base64
    readonly_fields = ['logo_tag']

admin.site.register(Category, CategoryAdmin)

class UserEducationDetailAdmin(admin.ModelAdmin):
    search_fields = ('user', 'course_name', 'institution_name', 'completion_year', 'certificate_doc_url')
    list_filter = [
        ('user', RelatedDropdownFilter),
    ]
    list_display = 'user', 'course_name', 'institution_name', 'completion_year', 'certificate_doc_url', 'DownloadDocument'
    fields = ('user', 'course_name', 'institution_name', 'completion_year', 'description', 'certificate_doc', 'certificate_doc_url')

admin.site.register(UserEducationDetail, UserEducationDetailAdmin)


class UserDeviceTokenAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__mobile', 'device_token', 'device', 'created_at')
    list_filter = [
        ('user', RelatedDropdownFilter),
    ]
    list_display = 'user', 'device', 'created_at', 'device_token'
    fields = ('user', 'device_token', 'device', 'created_at')

admin.site.register(UserDeviceToken, UserDeviceTokenAdmin)



admin.site.register(UserOrder)
admin.site.register(Location)
admin.site.register(TimeZone)
admin.site.register(Languages)
admin.site.register(Expertise)
admin.site.register(ExpertTeamMember)
admin.site.register(Role)
admin.site.register(DegreeCertification)