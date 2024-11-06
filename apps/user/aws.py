# import boto3
# from django.conf import settings


# class Aws:
#     s3_client = None

#     def __init__(self):
#         self.s3_client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)

#     def upload_file(self, file, file_path_name):
#         self.s3_client.upload_fileobj(file.file, settings.AWS_STORAGE_BUCKET_NAME, file_path_name,
#         ExtraArgs={'ACL': 'public-read'})
#         file_url = settings.AWS_S3_CUSTOM_DOMAIN + file_path_name
#         return file_url



    