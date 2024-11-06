from rest_framework import views, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from .models import *
from .serializer import *

from apps.common_utils.standard_response import success_response, error_response


# Create your views here.
class UserQueries(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            user = request.user

            query = Query.objects.create(program_batch_id=request.data['program_batch'], user=user,
                                         query=request.data['query'])
            if 'attachment' in request.data and request.data.getlist('attachment'):
                for attach in request.data.getlist('attachment'):
                    QueryAttachments.objects.create(query=query, attachment=attach).save()

            query.save()
            serializers = QuerySerializer(query, many=False)
            return Response(success_response(serializers.data), status=status.HTTP_200_OK)
        except BaseException as err:
            print(err)
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, query_id):
        try:
            user = request.user
            queryset = Query.objects.get(query_id=query_id)

            if 'attachment' in request.data and request.data.getlist('attachment'):
                for attach in request.data.getlist('attachment'):
                    QueryAttachments.objects.create(query=queryset, attachment=attach).save()

            if 'delete_attachment' in request.data and request.data.getlist('delete_attachment'):
                ids = request.data.getlist('delete_attachment')
                QueryAttachments.objects.filter(attachment_id__in=ids).delete()

            queryset.query = request.data['query']
            queryset.update_at = datetime.now()
            queryset.save()

            serializers = QuerySerializer(queryset, many=False)
            return Response(success_response(serializers.data), status=status.HTTP_200_OK)
        except Query.DoesNotExist:
            return Response(error_response("Query does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            print(err)
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, query_id):
        try:
            query = Query.objects.get(query_id=query_id)
            query.delete()
            return Response(success_response("Query deleted successfully"), status=status.HTTP_200_OK)
        except Query.DoesNotExist:
            return Response(error_response("Query does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            print(err)
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpertQueries(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = request.user
            query_comment = QueryComment.objects.create(user=user, query_id=request.data['query_id'],
                                                        comment=request.data['comment'])
            query_comment.save()

            serializer = QueryCommentSerializer(query_comment, many=False)
            return Response(success_response(serializer.data), status=status.HTTP_200_OK)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id):
        try:
            query_comment = QueryComment.objects.get(comment_id=comment_id)
            query_comment.delete()

            return Response(success_response("QueryComment deleted successfully"), status=status.HTTP_200_OK)
        except QueryComment.DoesNotExist:
            return Response(error_response("QueryComment does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentReply(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = request.user
            if QueryComment.objects.get(comment_id=request.data['comment_id']):
                reply = QueryCommentReply.objects.create(comment_id=request.data['comment_id'],
                                                         reply=request.data['reply'], user=user)
                reply.save()

                serializer = QueryCommentReplySerializer(reply, many=False)
                return Response(success_response(serializer.data), status=status.HTTP_200_OK)
        except QueryComment.DoesNotExist:
            return Response(error_response("Comment does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, reply_id):
        try:
            user = request.user
            if QueryCommentReply.objects.get(reply_id=reply_id):
                reply = QueryCommentReply.objects.filter(reply_id=reply_id)
                reply.delete()

                return Response(success_response("Reply deleted successfully"), status=status.HTTP_200_OK)
        except QueryCommentReply.DoesNotExist:
            return Response(error_response("Reply does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllQueries(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        query_data = Query.objects.filter(program_batch__program__expert=user).order_by('-update_at')
        return query_data

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = AllQueriesSerializer(queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(success_response(response.data), status=status.HTTP_200_OK)


class UnansweredQueries(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        expert_query = Query.objects.filter(program_batch__program__expert=user).values_list('query_id', flat=True)
        comment_query = QueryComment.objects.filter(query_id__in=expert_query).values_list('query_id', flat=True)
        query_data = Query.objects.filter(program_batch__program__expert=user).exclude(
            query_id__in=comment_query).order_by('-update_at')

        return query_data

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = AllQueriesSerializer(queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(success_response(response.data), status=status.HTTP_200_OK)


class QueryDetails(views.APIView):
    permission_classes = (AllowAny,)

    def get(self, request, query_id):
        try:
            query = Query.objects.get(query_id=query_id)
            serializer = QueryDetailsSerializer(query, many=False)
            return Response(success_response(serializer.data), status=status.HTTP_200_OK)
        except Query.DoesNotExist:
            return Response(error_response("Query Does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryCommentLiked(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self,request,comment_id):
        try:
            user = request.user
            comment = QueryComment.objects.get(comment_id=comment_id)
            comment.liked_user.add(user)
            comment.save()
            return Response(success_response("User added successfully"),status=status.HTTP_200_OK)
        except QueryComment.DoesNotExist:
            return Response(error_response("Comment does not exist"),status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, comment_id):
        try:
            user = request.user
            comment = QueryComment.objects.get(comment_id=comment_id)
            comment.liked_user.remove(user)
            comment.save()
            return Response(success_response("User removed successfully"), status=status.HTTP_200_OK)
        except QueryComment.DoesNotExist:
            return Response(error_response("Comment does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return Response(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
