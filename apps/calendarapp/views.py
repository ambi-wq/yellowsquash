from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import *
from apps.common_utils.standard_response import success_response


# Create your views here.
# class CalendarList(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request):
#         # Get user
#         user = request.user
#         event_type = request.query_params.get('event_type',None)
#         print(f"{event_type=}")
#         program = Program.objects.filter(expert=user, status='active').values('id', 'title')
#         upcoming_session = []
#         today = date.today()
#         if program:
#             program_ids = [prog['id'] for prog in program]
#             upcoming_session = ProgramBatchSession.objects.filter(programBatch__program_id__in=program_ids,
#                                                                session_date__gt=today).values('id', 'title',
#                                                                                               'programBatch_id',
#                                                                                               'programBatch__program_id',
#                                                                                               'session_date', 'start_time',
#                                                                                               'end_time').distinct(
#                 'programBatch_id')
#
#             if upcoming_session:
#                 for bs in upcoming_session:
#                     bs['program_id'] = bs.pop('programBatch__program_id')
#
#         upcoming_webinars = Webinar.objects.filter(status='Active', expert=user, webinar_date__gt=today).values('id',
#                                                                                                                 'title',
#                                                                                                                 'subtitle',
#                                                                                                                 'webinar_date',
#                                                                                                                 'start_time',
#                                                                                                                 'end_time').order_by(
#             'webinar_date')[:1]
#
#         data = {"message": "success", "program_session": program, "upcoming_session": upcoming_session,
#                 'upcoming_webinar': upcoming_webinars}
#         return Response(data, status=status.HTTP_200_OK)


class CalendarList(APIView):
    permission_classes = (IsAuthenticated,)
    today = date.today()

    def program_queryset(self):
        user = self.request.user
        program_ids = Program.objects.filter(expert=user, status='active').values_list('id', flat=True)
        upcoming_session = ProgramBatchSession.objects.filter(programBatch__program_id__in=program_ids,
                                                              session_date__gt=self.today).distinct('programBatch_id')
        session_serializer = UpcomingSessionSerializer(upcoming_session, many=True)
        return session_serializer.data

    def webinar_queryset(self):
        user = self.request.user
        upcoming_webinars = Webinar.objects.filter(status='Active', expert=user, webinar_date__gt=self.today).order_by(
            'webinar_date')[:1]
        webinar_serializer = UpcomingWebinarSerializer(upcoming_webinars, many=True)
        return webinar_serializer.data

    def get(self, request):
        event_type = request.query_params.get('event_type', None)
        upcoming_session = upcoming_webinar = []
        data = {}

        if event_type == '1':
            upcoming_session = self.program_queryset()
        elif event_type == '2':
            upcoming_webinar = self.webinar_queryset()
        else:
            upcoming_session = self.program_queryset()
            upcoming_webinar = self.webinar_queryset()

        data['upcoming_session'] = upcoming_session
        data['upcoming_webinar'] = upcoming_webinar
        return Response(success_response(data), status=status.HTTP_200_OK)
