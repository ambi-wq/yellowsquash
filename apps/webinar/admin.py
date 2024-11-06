from django.contrib import admin
from django.db import models
from django.forms.models import BaseInlineFormSet
from rest_framework import status
# from .models import Webinar, WebinarCategory
from .models import Webinar, WebinarSubscriber, Section, WebinarSection,WebinarCategory
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter
)
from rangefilter.filter import (
    DateRangeFilter, DateTimeRangeFilter
)
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from django.utils.text import slugify
from apps.user.models import User
import time
from django.forms import ModelForm, ValidationError

from import_export.admin import ExportMixin



'''
allowing user must select atleast one  webinar category
'''
class WebinarInlineFormSet(BaseInlineFormSet):
    def clean(self) -> None:
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count+=1
            except AttributeError:
                pass
        
        if count < 1:
            raise ValidationError('You must have at least one webinar category')



class WebinarCategoryInline(admin.TabularInline):
    model = WebinarCategory
    extra = 1
    formset = WebinarInlineFormSet


class WebinarAdminForm(ModelForm):
    class Meta:
        model = Webinar
        fields = '__all__'



    def clean_description(self):
        if len(self.cleaned_data["description"])<50:
            raise ValidationError("Atleast 50 charecter required.")
        return self.cleaned_data['description']

    def clean_thumbnail_url(self):
        if not self.cleaned_data["thumbnail_image"] and not self.cleaned_data["thumbnail_url"]:
                self.add_error('thumbnail_image',"This Field Required")
        return self.cleaned_data["thumbnail_url"]
        


        

     

   
class WebinarAdmin(admin.ModelAdmin):
    form = WebinarAdminForm
    list_display = ("title", "webinar_date", "start_time", "end_time", "expert", "status", "createdAt")
    # list_filter = ("id", "title", "webinar_date", "start_time", "end_time", "expert", "status", "createdAt")
    list_filter = [
        ("title",DropdownFilter),
        ("expert",RelatedDropdownFilter),
        ("webinar_date",DateRangeFilter),
        "status"
    ]
    search_fields = ("id", "title", "webinar_date", "start_time", "end_time", "expert__first_name", "status", "createdAt")
    exclude = ['slug']
    inlines = [
        WebinarCategoryInline,
    ]

    @receiver(pre_save, sender=Webinar)
    def update_slug(sender, instance, *args, **kwargs):
        if instance.slug is None:
            instance.slug = slugify(instance.title)+"-"+str(int(time.time()))


    @receiver(post_save, sender=Webinar)
    def attach_sections(sender, instance, *args, **kwargs):
        is_created = bool(kwargs.get('created'));
        print(is_created)
        if is_created:
            print('args: ',args, 'kwargs:', kwargs)
            sections = Section.objects.all() 
            #.filter(status='Active')
            displayOrder = 1
            for section in sections:
                webinar_section = WebinarSection()
                webinar_section.webinar = instance
                webinar_section.section = section
                webinar_section.overiddenContent = section.content
                webinar_section.displayOrder = str(displayOrder)
                webinar_section.status = 'Deactive'
                webinar_section.save()
                displayOrder = displayOrder + 1
   
    def get_expert(self, obj):
        return obj.expert.username

    def formfield_for_foreignkey(self,db_field,request,**kwargs):

        if(db_field.name=='expert'):
            kwargs['queryset'] = User.objects.filter(user_type='expert').order_by('first_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    



   




class WebinarSubscriberAdmin(ExportMixin,admin.ModelAdmin):
    list_display = ("id", "name", "email", "webinar","whatsapp_mobile_no")
    # list_filter = ("id", "name", "email",  "user", "webinar", "status")
    list_filter = [
        ('name',DropdownFilter),
        ('email',DropdownFilter),
        ('user',RelatedDropdownFilter),
        ('webinar',RelatedDropdownFilter)
    ]

    search_fields = ("id", "name", "email",  "user__first_name", "webinar__title", "status")

class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "createdAt", "createdBy", "updatedAt", "updatedBy")
    # list_filter = ("id", "title", "createdAt", "createdBy", "updatedAt", "updatedBy")
    list_filter = [
        ("title",DropdownFilter),
        'createdAt',
        ('createdBy',RelatedDropdownFilter),
        ("updatedBy",RelatedDropdownFilter)
    ]

    search_fields = ("id", "title", "createdAt", "createdBy__first_name", "updatedAt", "updatedBy__first_name")

class WebinarSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "webinar", "section", "displayOrder", "status")
    list_filter = [
        ("webinar",RelatedDropdownFilter),
        ("section",RelatedDropdownFilter)
    ]
    search_fields = ("id", "webinar__title", "section__title", "displayOrder", "status")
    

admin.site.register(Webinar, WebinarAdmin)
admin.site.register(WebinarSubscriber, WebinarSubscriberAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(WebinarSection, WebinarSectionAdmin)
# # Register your models here.


# class CategoryInline(admin.TabularInline):
#     model = WebinarCategory
#     extra = 1



# class WebinarAdmin(admin.ModelAdmin):
#     search_fields = ('id', 'title')
#     list_display = 'id', 'title', 'speaker_user', 'price', 'start_date', 'webinar_start_time', 'webinar_end_time'
#     inlines = [
#         CategoryInline,
#     ]

# admin.site.register(Webinar, WebinarAdmin)
