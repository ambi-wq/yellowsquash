
from django.conf import settings
from apps.program.models import Program
from apps.webinar.models import Webinar
from apps.user.models import User
from apps.blog.models import Blog
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

import boto3
from botocore.errorfactory import ClientError


class UpdateImageUrlApiView(APIView):
    permission_classes = (AllowAny,)

    def put(self,request):

        table_name = request.data['table_name']
        column_name =  request.data['column_name']
        aws_s3_bucket_url = settings.AWS_S3_CUSTOM_DOMAIN
        imageUrl = list()
        imageNotExist = list()

        if(table_name=='Blog'):  
            blogs = Blog.objects.all()
            for blog in blogs:
                if column_name=="feature_image_url" and (blog.feature_image_url):
                    old_url = blog.feature_image_url
                    image_path = old_url.split('amazonaws.com/')[1]
                    new_url = aws_s3_bucket_url+image_path
                    if not (self.check_Image_exist(image_path)):
                        imageNotExist.append(new_url)
                    else:
                        blog.feature_image_url = new_url
                        blog.save()
                        imageUrl.append([old_url,new_url])

                elif column_name=='banner_image_url' and blog.banner_image_url:
                    old_url = blog.banner_image_url
                    image_path = old_url.split('amazonaws.com/')[1]
                    new_url = aws_s3_bucket_url+image_path
                    if(not (self.check_Image_exist(image_path))):
                        imageNotExist.append(new_url)
                    else:
                        blog.banner_image_url = new_url
                        blog.save()
                        imageUrl.append([old_url,new_url])


        elif table_name=="Program":
            programs = Program.objects.all()
            for program in programs:
                if(column_name=="image_url" and program.image_url):
                    old_url = program.image_url
                    if old_url.find('amazonaws.com')!=-1:
                        image_path = old_url.split('amazonaws.com/')[1]
                        new_url = aws_s3_bucket_url+image_path
                        if(not (self.check_Image_exist(image_path))):
                            imageNotExist.append(new_url)
                        else:
                            program.image_url = new_url
                            program.save()
                            imageUrl.append([old_url,new_url])

                    elif(old_url.find('yellowsquash.in'))!=-1:
                        image_path = old_url.split('yellowsquash.in/')[1]
                        new_url = aws_s3_bucket_url+image_path
                        if(not self.check_Image_exist(image_path)):
                            print(old_url)
                            imageNotExist.append(new_url)
                        else:
                            program.image_url = new_url
                            program.save()
                            imageUrl.append([old_url,new_url])

        elif(table_name=='Webinar'):
            webinars = Webinar.objects.all()
            for webinar in webinars:
                if(column_name=='thumbnail_url' and webinar.thumbnail_url):
                    old_url = webinar.thumbnail_url
                    if old_url.find('amazonaws.com')!=-1:
                        image_path = old_url.split('amazonaws.com/')[1]
                        new_url = aws_s3_bucket_url+image_path
                        if(not self.check_Image_exist(image_path)):
                            imageNotExist.append(new_url)
                        else:
                            webinar.thumbnail_url = new_url
                            webinar.save()
                            imageUrl.append([old_url,new_url])

        elif(table_name=='User'):
            users = User.objects.all()
            for user in users:
                if(column_name=='user_img' and user.user_img):
                    old_image_url = user.user_img
                    if old_image_url.find('amazonaws.com')!=-1:
                        image_path = old_image_url.split('amazonaws.com/')[1]
                        new_url = aws_s3_bucket_url+image_path
                        if(not self.check_Image_exist(image_path)):
                            imageNotExist.append(new_url)
                        else:
                            user.user_img = new_url
                            user.save()
                            imageUrl.append([old_image_url,new_url])
                                    
        return Response({
            "exist_image":imageUrl,
            "not_exist_image":imageNotExist
        })



    def check_Image_exist(self,image_path):
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)
        try:
            s3.head_object(Bucket=bucket_name, Key=image_path)
            return True
        except ClientError as e:
            return False



    


