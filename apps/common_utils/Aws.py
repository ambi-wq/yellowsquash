import boto3
from django.conf import settings


class Aws:

    def __init__(self):
        self.s3_client = boto3.client('s3',aws_access_key_id = settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)

    def upload_file(self, file, file_path_name):
        self.s3_client.upload_fileobj(file.file, settings.AWS_STORAGE_BUCKET_NAME, file_path_name, ExtraArgs={'ACL': 'public-read'})
        file_url = settings.AWS_S3_CUSTOM_DOMAIN + file_path_name
        return file_url

    def copy_file(self, origin_file_path_url, destination_file_path_name):
        copy_source = {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': origin_file_path_url.replace(settings.AWS_S3_CUSTOM_DOMAIN, "")
        }
        self.s3_client.copy(copy_source, settings.AWS_STORAGE_BUCKET_NAME, destination_file_path_name, ExtraArgs={'ACL': 'public-read'})
        file_url = settings.AWS_S3_CUSTOM_DOMAIN + destination_file_path_name
        return file_url


class AwsFilePath:

    @staticmethod
    def programSessionResourcePath(program_id, session_id, resource_file_name):
        return """program/{program_id}/sessions/{session_id}/resources/{resource_file_name}""".format(
                program_id=program_id,
                session_id=session_id,
                resource_file_name=resource_file_name
            )

    @staticmethod
    def programBatchSessionResourcePath(program_batch_id, batch_session_id, resource_file_name):
        return """program_batch/{program_batch_id}/sessions/{batch_session_id}/resources/{resource_file_name}""".format(
                program_batch_id=program_batch_id,
                batch_session_id=batch_session_id,
                resource_file_name=resource_file_name,
            )

    @staticmethod
    def blogImageResourcePath(blog_id, resource_file_name):
        return """blog/{blog_id}/resources/{resource_file_name}""".format(
                blog_id=blog_id,
                resource_file_name=resource_file_name
            )

    @staticmethod
    def userCertificateDocPath(user_id, course_name,resource_file_name):
        return """user/{user_id}/certificates/{course_name}/{resource_file_name}""".format(
                user_id=user_id,
                course_name=course_name,
                resource_file_name=resource_file_name,
            )

    @staticmethod
    def userProfilePath(user_id, resource_file_name):
        return """user/{user_id}/profile/{resource_file_name}""".format(
                user_id=user_id,
                resource_file_name=resource_file_name,
            )
  
    @staticmethod
    def userMediaFilePath(user_id, resource_file_name):
        return """media/{user_id}/{resource_file_name}""".format(
                user_id=user_id,
                resource_file_name=resource_file_name,
            )

    @staticmethod
    def webinarMediaFilePath(slug, resource_file_name):
        return """media/webinar/{slug}/{resource_file_name}""".format(
                slug=slug,
                resource_file_name=resource_file_name,
            )

    @staticmethod
    def programMediaFilePath(resource_file_name):
        return """media/program/{resource_file_name}""".format(
                resource_file_name=resource_file_name,
            )
    
    @staticmethod
    def staticResourcesFilePath(resource_id, resource_file_name):
        return """payment/{resource_id}/{resource_file_name}""".format(
                resource_id=resource_id,
                resource_file_name=resource_file_name,
            )

    @staticmethod
    def userPaymentScreenShort(user_id, batch_id , screen_short_name):
        return """payment-screenShort/{user_id}/{batch_id}/{screen_short_name}""".format(
                user_id=user_id,
                batch_id = batch_id,
                screen_short_name= screen_short_name,
            )

    @staticmethod
    def GroupCoverImage(user_id, file_name):
        return """group-cover-image/{user_id}/{file_name}""".format(
            user_id=user_id,
            file_name=file_name,
        )

    @staticmethod
    def GroupPostMedia(user_id, post_id, file_name):
        return f"group-post-media/{user_id}/{post_id}/{file_name}"