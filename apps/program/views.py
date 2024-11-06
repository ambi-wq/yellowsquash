from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from rest_framework import filters
from rest_framework import generics, status, views
from rest_framework.pagination import LimitOffsetPagination
# from rest_framework import authentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.common_utils.standard_response import success_response, error_response
from apps.user.models import FavoriteExpert
from .models import *
from .serializer import *

logger = logging.getLogger(__name__)


def prepare_program_data(data, request):
    currentDate = datetime.today()

    for d in data:
        # print('userx!', request.user.is_anonymous)

        if (not request.user.is_anonymous):
            d['is_favorite'] = FavoriteProgram.objects.filter(Q(user=request.user) & Q(program=d['id'])).count() > 0

        tasks_data = ProgramTaskSerializer(ProgramTask.objects.filter(program_id=d['id']).values(), many=True).data
        if not request.user.is_anonymous:
            for t in tasks_data:
                t['actions'] = ActionTaskUserProgramSerializer(
                    ActionTaskUserProgram.objects.prefetch_related('task').filter(
                        Q(program_id=d['id']) & Q(task_id=t['id']) & Q(user=request.user) & Q(
                            created_at__gte=currentDate.replace(hour=0, minute=0, second=0)) & Q(
                            created_at__lte=currentDate.replace(hour=23, minute=59, second=59))).values(),
                    many=True).data
        d['tasks'] = tasks_data

        expert = User.objects.filter(id=d['expert']).first()

        d['expert'] = {
            'first_name': expert.first_name,
            'last_name': expert.last_name,
            'biographic_info': expert.biographic_info,
            'short_description': expert.short_description,

            'qualification': expert.qualification,
            'designation': expert.designation,

            'experience': expert.experience,
            'professional_title': expert.professional_title,
            'id': expert.id,
            'profile_picture': os.path.join(settings.MEDIA_URL, str(expert.profile_picture)),
        }

        if not request.user.is_anonymous:
            d['expert']['is_favorite'] = FavoriteExpert.objects.filter(user=request.user, expert=expert.id).count() > 0
    return data


def prepare_program_batch_handling(data):
    currentDate2 = datetime.today()

    data2 = list(filter(lambda x: x['is_subscribed'] == 'active', data))
    for d in data2:
        # print('removing batch', d['batch_id'], d['id'])
        data = list(filter(lambda x: x['id'] != d['id'], data))

    # print('dat', data2)
    for f in data:
        print('issi', f['is_subscribed'], f['batch_id'])
        f['sort_status'] = 0 if f['is_subscribed'] == 'active' else 1 if f[
                                                                             'is_subscribed'] == 'payment_under_review' else 2
        f['registered'] = ProgramBatchUser.objects.filter(programBatch__id=f['batch_id']).count()
        f['capacity_flag'] = 0 if f['registered'] < f['capacity'] else 1
        f['date_flag'] = 0 if currentDate2 < datetime.strptime(f['start_date'], '%Y-%m-%d') + timedelta(
            days=f['additional_days']) else 1

        # check batch count and then capacity and date flags
        batch_count = len(list(filter(lambda x: x['id'] == f['id'], data)))
        f['hide_flag'] = (
                (batch_count > 0 and f['sort_status'] > 0) and (f['capacity_flag'] == 1 or f['date_flag'] == 1)
                or
                (f['sort_status'] == 0 and
                 ((currentDate2 - timedelta(days=1) if f['batch_end_date'] is None else datetime.strptime(
                     f['batch_end_date'], '%Y-%m-%d') < currentDate2)))
        )

    data = list(filter(lambda x: not x['hide_flag'], data))

    data = sorted(data, key=lambda d: (d['sort_status'], d['start_date']))

    for i in range(len(data)):
        if i >= len(data):
            print(i, len(data), 'break')
            break

        program_id = data[i]['id']
        for j in range(len(data)):
            if i == j:
                continue
            if data[i]['id'] == data[j]['id']:
                print('removing', data[j]['batch_id'])
                # data[j]['remove_it'] = True
                data.pop(j)
                break

    return data


class ProgramList(generics.ListAPIView):
    serializer_class = UserProgramListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self, request=None):
        currentDate = datetime.today().strftime('%Y-%m-%d')
        queryset = ProgramBatch.objects.all()
        currentDate2 = datetime.today()
        if request:
            if request.user.is_authenticated and request.user.user_type == 'expert':
                queryset = queryset.filter(program__expert_id=request.user.id)
            elif request.user.is_authenticated:
                userId = request.user.id
                print('user:', userId)
                programBatchIds = ProgramBatchUser.objects.filter(programBatch__batch_end_date__gte=currentDate,
                                                                  user__id=userId).values_list('programBatch_id',
                                                                                               flat=True)
                queryset = ProgramBatch.objects.prefetch_related('program').filter(program__status='active').filter(
                    Q(id__in=programBatchIds) | Q(additional_start_date__gte=currentDate))

            else:
                queryset = ProgramBatch.objects.prefetch_related('program').filter(program__status='active').filter(
                    additional_start_date__gte=currentDate)
        else:
            queryset = ProgramBatch.objects.prefetch_related('program').filter(program__status='active').filter(
                additional_start_date__gte=currentDate)

        print(queryset.query)

        queryset = queryset.order_by('batch_start_date', 'program__rating', 'program__title')
        return queryset

    @never_cache
    def get(self, request):
        currentDate = datetime.today()

        serializer = ProgramBatchSerializer(
            self.get_queryset(request),
            many=True,
            context={'user_id': request.user.id}
        )

        data = prepare_program_batch_handling(serializer.data)

        # bring subscribed on top
        # new_data = [f['sort_status'] = 0 if f['sort_status'] == 'active' else f['sort_status'] = 1 if f['sort_status'] == 'payment_under_review' else 2 for f in data]

        data = prepare_program_data(data, request)

        return JsonResponse(data, safe=False)


class SearchProgramList(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def get_queryset(self, request=None):
        currentDate = datetime.today().strftime('%Y-%m-%d')
        queryset = ProgramBatch.objects.filter(batch_status='open')

        if request:
            if request.user.is_authenticated and request.user.user_type == 'expert':
                print("if =========")
                queryset = queryset.filter(program__expert_id=request.user.id)
            elif request.user.is_authenticated:
                print("elif =========")
                programBatchIds = ProgramBatchUser.objects.filter(programBatch__batch_end_date__gte=currentDate,
                                                                  user__id=request.user.id).values_list(
                    'programBatch_id', flat=True)
                print(programBatchIds, "===========")
                queryset = ProgramBatch.objects.prefetch_related('program').filter(
                    Q(batch_status='open', id__in=programBatchIds) | Q(batch_status='open',
                                                                       additional_start_date__gte=currentDate,
                                                                       program__status='active'))
                print(queryset, "=====qu")
            else:
                print("else =========")
                # queryset = ProgramBatch.objects.prefetch_related('program').filter(batch_start_date__gte = currentDate)
                queryset = ProgramBatch.objects.prefetch_related('program').filter(
                    Q(batch_status='open', additional_start_date__gte=currentDate) & Q(program__status='active'))

            if request.data:

                # sorting if any applicable
                if 'sorting' in request.data and request.data.get('sorting'):
                    if request.data.get('sorting') == 'name':
                        queryset = queryset.order_by('program__title')
                    if request.data.get('sorting') == 'rating':
                        queryset = queryset.order_by('-program__rating')
                    if request.data.get('sorting') == 'date':
                        queryset = queryset.order_by('batch_start_date')

                # filter results for categories
                if 'filters' in request.data and request.data.get('filters'):
                    if 'categories' in request.data.get('filters') and request.data.get('filters').get('categories') \
                            and type(request.data.get('filters').get('categories')) == list and request.data.get(
                        'filters').get('categories'):
                        # for category in request.data.get('filters').get('categories'):
                        #     queryset = queryset.filter(program__category=category).distinct()
                        queryset = queryset.filter(
                            program__category__in=request.data.get('filters').get('categories')).distinct()

                if 'search' in request.data and request.data.get('search', None):
                    if type(request.data.get('search')) == str:
                        searchTag = request.data.get('search')
                        categories = Category.objects.filter(name__icontains=searchTag).values_list('id', flat=True)
                        queryset = queryset.filter(
                            Q(title__icontains=searchTag) | Q(program__title__icontains=searchTag) | Q(
                                program__category__in=categories)).distinct()

        else:
            print("out else =========")
            queryset = ProgramBatch.objects.prefetch_related('program').filter(additional_start_date__gte=currentDate,
                                                                               batch_status='open',
                                                                               program__status='active')

        return queryset.order_by('batch_start_date')

    def post(self, request):
        # if not requested with limti and ofset use default as :
        # limit : 10
        # ofset : 0
        limit = int(request.GET.get('limit', 10))
        offSet = int(request.GET.get('offset', 0))

        serializer = ProgramBatchSerializer(
            self.get_queryset(request),
            many=True,
            context={'user_id': request.user.id}
        )
        serializedData = prepare_program_batch_handling(serializer.data)[offSet: (offSet + limit)]
        # data = serializedData

        serializedData = prepare_program_data(serializedData, request)
        return JsonResponse({
            "next_data_query": 'limit={limit}&offset={offset}'.format(
                limit=limit,
                offset=offSet + limit
            ),
            "data": serializedData,
        })


class FavoriteProgramsList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, request=None):
        currentDate = datetime.today().strftime('%Y-%m-%d')
        queryset = ProgramBatch.objects.prefetch_related('program').all()

        if request.user.user_type == 'expert':
            queryset = queryset.filter(program__expert_id=request.user.id)
        else:
            programIds = FavoriteProgram.objects.filter(user_id=request.user.id).values_list('program_id', flat=True)
            queryset = queryset.filter(program_id__in=programIds, additional_start_date__gte=currentDate)

        queryset = queryset.order_by('batch_start_date', 'program__rating', 'program__title')
        return queryset

    def get(self, request):
        currentDate = datetime.today()

        serializer = ProgramBatchSerializer(
            self.get_queryset(request),
            many=True,
            context={'user_id': request.user.id}
        )

        data = prepare_program_batch_handling(serializer.data)

        data = prepare_program_data(data, request)
        '''
        for d in data:
            d['is_favorite'] = True
            tasks_data = ProgramTaskSerializer(ProgramTask.objects.filter(program_id=d['id']).values(), many=True).data
            for t in tasks_data:
                t['actions'] = ActionTaskUserProgramSerializer(
                    ActionTaskUserProgram.objects.prefetch_related('task').filter(
                        Q(program_id=d['id']) & Q(task_id=t['id']) & Q(
                created_at__gte=currentDate.replace(hour=0, minute=0, second=0)) & Q(
                created_at__lte=currentDate.replace(hour=23, minute=59, second=59))).values(),
                    many=True).data
            d['tasks'] = tasks_data

            expert = User.objects.filter(id=d['expert']).first()

            d['expert'] = {
                'first_name': expert.first_name,
                'last_name': expert.last_name,
                'biographic_info': expert.biographic_info,
                'short_description': expert.short_description,

                'qualification': expert.qualification,
                'designation': expert.designation,

                'experience': expert.experience,
                'professional_title': expert.professional_title,
                'id': expert.id,
                'profile_picture': os.path.join(settings.MEDIA_URL, str(expert.profile_picture)),
                'is_favorite': FavoriteExpert.objects.filter(user=request.user, expert=expert.id).count() > 0

            }
        '''
        return JsonResponse(data, safe=False)


class MyPrograms(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ProgramBatch.objects.all().order_by('batch_start_date')

    @never_cache
    def get(self, request, *kwargs, **args):

        queryset = self.get_queryset()

        if request.user.user_type and request.user.user_type == 'expert':
            queryset = queryset.filter(expert=request.user.id)

        if request.user.user_type and request.user.user_type == 'customer':
            queryset = queryset.filter(
                id__in=ProgramBatchUser.objects.filter(user=request.user.id).values_list('programBatch',
                                                                                         flat=True))

        # print('QRY', queryset.query)
        serializer = ProgramBatchSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id, }
        )

        data = serializer.data

        data = prepare_program_data(data, request)

        return JsonResponse(data, safe=False)


class ExpertPrograms(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer = ProgramSerializer

    def get_queryset(self):
        return ProgramBatch.objects.prefetch_related('program').all().order_by('batch_start_date').filter(
            program__status='active').filter(
            program__expert=self.kwargs.get("expert_id"))

    @never_cache
    def get(self, request, *kwargs, **args):
        serializer = ProgramBatchSerializer(
            self.get_queryset(),
            many=True,
            context={'user_id': request.user.id}
        )
        print(self.get_queryset().query)
        data = serializer.data
        data = prepare_program_batch_handling(data)

        data = prepare_program_data(data, request)

        return JsonResponse(data, safe=False)


class ProgramDetails(generics.ListAPIView):
    permission_classes = (AllowAny,)

    @never_cache
    # program deatils should can be fetch from program batch id only
    def get(self, request, batch_id):
        currentDate = datetime.today()

        program = {}
        user_id = request.user.id
        if ProgramBatch.objects.filter(id=batch_id).exists():

            programBatch = ProgramBatch.objects.get(id=batch_id)
            print(batch_id)
            queryset = Program.objects.get(id=programBatch.program_id)

            programSerializer = ProgramBatchSerializer(programBatch, many=False, context={'user_id': request.user.id})
            program['program'] = [programSerializer.data, ]
            # program['program'][0]['offer_price'] = programBatch.offer_price

            program_id = queryset.id

            count = 0
            for p in ProgramBatch.objects.filter(program=program_id):
                count = ProgramBatchUser.objects.filter(id=p.id).count()
                # count = ProgramBatchUser.objects.filter(programBatch_id=p.id).count()

            program['program'][0]['subscribers'] = count

            if not request.user.is_anonymous:
                program['program'][0]['is_favorite'] = FavoriteProgram.objects.filter(
                    Q(user=request.user) & Q(program=program_id)).count() > 0

            serializer = ProgramVideoSerializer(queryset.videos_set, many=True)
            program['videos'] = serializer.data

            serializer = ProgramReviewSerializer(queryset.review_set, many=True)
            program['reviews'] = serializer.data

            serializer = ProgramTaskSerializer()

            serializer = ProgramBatchSessionSerializer(
                ProgramBatchSession.objects.filter(programBatch_id=batch_id).order_by('sequence_num'), many=True)
            program['sessions'] = serializer.data
            # print(program.__repr__())

            program['overviews'] = OverviewSerializer(Overview.objects.filter(program_id=program_id), many=True).data

            serializer = ProgramFrequentlyAskedQuestionSerializer(queryset.frequentlyaskedquestion_set, many=True)
            program['faqs'] = serializer.data

            tasks = ProgramTaskSerializer(ProgramTask.objects.filter(program_id=program_id).values(), many=True)
            tasks_data = tasks.data
            if not request.user.is_anonymous:
                for t in tasks_data:
                    t['actions'] = ActionTaskUserProgramSerializer(
                        ActionTaskUserProgram.objects.prefetch_related('task').filter(
                            Q(program_id=program_id) & Q(task_id=t['id'])
                            & Q(created_at__gte=currentDate.replace(hour=0, minute=0, second=0)) & Q(
                                created_at__lte=currentDate.replace(hour=23, minute=59, second=59))).values(),
                        many=True).data
            program['tasks'] = tasks_data

            # print(ActionTaskUserProgram.objects.prefetch_related('task').filter(program_id=program_id).values().__repr__())
            # task_actions = ActionTaskUserProgramSerializer(
            #     ActionTaskUserProgram.objects.prefetch_related('task').filter(program_id=program_id).values(),
            #     many=True)
            # program['task_actions'] = task_actions.data

            plts = ProgramLevelTracker.objects.filter(program_id=program_id)
            lst_lt = []
            for plt in plts:
                lt = LevelTracker.objects.filter(id=plt.level_tracker_id).first()

                lst_lt.append(
                    {
                        'id': lt.id,
                        'title': lt.title,
                        'icon_url': lt.icon_url,
                        'tags': [{'tag': t.tag, 'id': t.id} for t in
                                 LevelTrackerTag.objects.filter(level_tracker_id=lt.id)],
                        'value_types': [
                            {'level_tracker': t.id, 'title': t.title, 'unit': t.unit, 'initial_value': t.initial_value}
                            for t in
                            LevelTrackerValueType.objects.filter(level_tracker_id=lt.id)],

                    }
                )

            program['level_tracker'] = lst_lt

            pst = ProgramSymptomTracker.objects.filter(program_id=program_id)
            expert = User.objects.filter(id=program['program'][0]['expert']).first()

            program['expert'] = {
                'first_name': expert.first_name,
                'last_name': expert.last_name,
                'biographic_info': expert.biographic_info,
                'short_description': expert.short_description,

                'qualification': expert.qualification,
                'designation': expert.designation,

                'experience': expert.experience,
                'professional_title': expert.professional_title,
                'id': expert.id,
                'profile_picture': os.path.join(settings.MEDIA_URL, str(expert.profile_picture)),

            }
            if not request.user.is_anonymous:
                program['expert']['is_favorite']: FavoriteExpert.objects.filter(user=request.user,
                                                                                expert=expert.id).count() > 0

            lst_pt = []
            for p in pst:
                lst_pt.extend(
                    [{"title": s.title, "id": s.id} for s in SymptomTracker.objects.filter(id=p.symptom_tracker_id)])

            program['symptom_tracker'] = lst_pt

            program['isSubscribed'] = 'inactive'

            if ProgramBatchUser.objects.filter(user=user_id, programBatch=batch_id).exists():
                data = ProgramBatchUser.objects.filter(user=user_id, programBatch=batch_id).values('status')
                print('status:', data)
                if data[0]['status'] == 'active':
                    program['isSubscribed'] = 'active'
                if data[0]['status'] == 'payment_under_review':
                    program['isSubscribed'] = 'payment_under_review'
                if data[0]['status'] == 'inactive':
                    program['isSubscribed'] = 'inactive'

        return JsonResponse(program, status=status.HTTP_201_CREATED)


class GetActionsDatewise(generics.ListAPIView):
    @never_cache
    def get(self, request, program_id, dt_low, dt_high):
        dat = ActionTaskUserProgram.objects.filter(Q(program_id=program_id)
                                                   & Q(created_at__gte=dt_low)
                                                   & Q(created_at__lte=dt_high))

        # print(dat.query)
        data = ActionTaskUserProgramSerializer(dat.values(), many=True).data

        return JsonResponse(data, status=status.HTTP_201_CREATED, safe=False)


class GetProgramBatchUser(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    @never_cache
    def get(self, request, *kwargs, **args):
        queryset = ProgramBatchUser.objects.all()
        serializer = ProgramBatchUserSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateProgramBatchUser(generics.CreateAPIView):
    serializer_class = ProgramBatchUserSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            request.data['user'] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddFavoriteProgarm(generics.CreateAPIView):
    serializer_class = FavoriteProgramSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            # request.data._mutable = True
            data = {'program': request.data['program'], 'user': request.user.id}
            # request.data['user'] = request.user.id
            # print(request.data, data)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # request.data._mutable = False
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemoveFavoriteProgram(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            favoritePrograms = FavoriteProgram.objects.filter(user=request.user.id, program=request.data.get('program'))
            if favoritePrograms.exists():
                favoritePrograms.delete()
            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetProgramBatchSessionResources(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    @never_cache
    def get(self, request, programBatchSession_id):
        user_id = request.user.id
        program_batch = ProgramBatchSession.objects.get(id=programBatchSession_id)
        program_batch_id = program_batch.programBatch_id
        is_open_to_see = datetime.combine(program_batch.session_date, program_batch.end_time) < datetime.now()

        is_purchased = ProgramBatchUser.objects.filter(programBatch_id=program_batch_id, user_id=user_id).exists()

        queryset = ProgramBatchSessionResource.objects.filter(programBatchSession_id=programBatchSession_id)
        # print(user_id, program_batch_id, programBatchSession_id, queryset.values)
        # for e in queryset:
        #     print('qs : ', e)
        if (is_purchased and is_open_to_see) or request.user.user_type == 'expert':
            serializer = ProgramBatchSessionAccessedResourceSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False, )
        else:
            return JsonResponse([], safe=False, )
        # else:
        #     serializer = ProgramBatchSessionNonAccessedResourceSerializer(queryset,many=True)


class UpdateProgramBatchSessionDateTime(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, programBatchSession_id):
        program_batch_session = ProgramBatchSession.objects.get(id=programBatchSession_id)

        program_batch_session.actual_start_datetime = datetime.now()
        program_batch_session.save()
        return JsonResponse(
            data={'message': 'success'},
            status=status.HTTP_201_CREATED
        )


class GlobalSearchProgram(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            queryset = Program.objects.filter(title__icontains=request.data['searchBy'])[:40]
            serializer = GlobalSearchProgramSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        except BaseException as error:
            return JsonResponse({
                'error': str(error)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPaymentDetailCreate(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    @never_cache
    def post(self, request):

        try:
            try:
                if not request.user.is_authenticated:
                    user = User.objects.get(email=request.data['email'])
                    request.user = user
                else:
                    user = request.user
            except User.DoesNotExist:
                user = None

            # checking is user already subscribed
            programBatchUserObj = ProgramBatchUser.objects.filter(user_id=request.user.id,
                                                                  programBatch=request.data['batch_id'])
            if programBatchUserObj:
                return JsonResponse(
                    data={"message": "already subscribed"},
                    status=status.HTTP_200_OK
                )

            if UserPaymentDetail.objects.filter(user_id=request.user.id, batch_id=request.data['batch_id']).exists():
                return JsonResponse(
                    data={"message": "user data already present", "user_id": user.id},
                    status=status.HTTP_201_CREATED
                )
            else:

                if not user:
                    # ananyoumous user basic detail
                    first_name = request.data['first_name']
                    last_name = request.data['last_name']
                    mobile = request.data['mobile']
                    email_id = request.data["email"]

                    user = User.objects.create(
                        username=first_name + "_" + ''.join(
                            random.choice(string.ascii_uppercase + string.digits) for _ in range(8)),
                        first_name=first_name,
                        last_name=last_name,
                        email=email_id,
                        mobile=mobile,
                    )
                    user.is_verified = True
                    user.save()

                UserPaymentDetail.objects.create(
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    mobile=request.data['mobile'],
                    email_id=request.data['email'],
                    flat_or_house_no=request.data.get('flat_or_house_no', ''),
                    stret_or_landmark=request.data.get('street_or_landmark', ''),
                    town_city_dist=request.data.get('town_city_dist', ''),
                    state=request.data.get('state', ''),
                    country=request.data.get('country', ''),
                    pincode=request.data.get('pincode', ''),
                    gst_no=request.data.get('gst_no', ''),
                    aadhar_no=request.data['aadhar_no'],
                    pan_no=request.data.get('pan_no', ''),
                    payment_type=request.data['payment_type'],
                    batch_id=request.data['batch_id'],
                    user_id=user.id
                )

                return JsonResponse(
                    data={"message": "done", "user_id": user.id},
                    status=status.HTTP_201_CREATED
                )
        except BaseException as err:
            return JsonResponse({
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPaymentDetailUpload(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    @never_cache
    def post(self, request):
        aws = Aws()

        try:
            if not request.user.is_authenticated:
                user = User.objects.get(id=int(request.data['user_id']))
                request.user = user

            if UserPaymentDetail.objects.filter(user_id=request.user.id, batch_id=request.data['batch_id']).exists():
                fileUploadPath = AwsFilePath.userPaymentScreenShort(
                    user_id=request.user.id,
                    batch_id=request.data['batch_id'],
                    screen_short_name=request.FILES['payment_screen_short'].name,
                )
                payemtData = UserPaymentDetail.objects.filter(user_id=request.user.id,
                                                              batch_id=request.data['batch_id']).update(
                    payment_screen_short_url=aws.upload_file(request.FILES['payment_screen_short'], fileUploadPath))
                if ProgramBatchUser.objects.filter(user_id=request.user.id,
                                                   programBatch=request.data['batch_id']).exists:
                    ProgramBatchUser.objects.create(
                        programBatch_id=request.data['batch_id'],
                        user_id=request.user.id,
                        status='payment_under_review'
                    )
                else:
                    ProgramBatchUser.objects.create(
                        programBatch_id=request.data['batch_id'],
                        user_id=request.user.id,
                        status='payment_under_review'
                    )
                return JsonResponse(
                    data={
                        "message": "You already subscribed for this program, Our backend is reviewing your payment information!"},
                    status=status.HTTP_201_CREATED
                )
        except BaseException as err:
            return JsonResponse({
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserPaymentRazorPay(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    @never_cache
    def post(self, request):
        if not request.user.is_authenticated:
            if request.data.__contains__("user_id"):
                request.user = User.objects.get(id=int(request.data["user_id"]))

        UserPaymentDetail.objects.filter(user_id=request.user.id, batch_id=request.data['batch_id']).update(
            razorpay_order_id=request.data['razorpay_order_id'],
            razorpay_payment_id=request.data['razorpay_payment_id'],
            razorpay_signature=request.data['razorpay_signature']
        )
        return JsonResponse(
            data={"message": "razorpay information done"},
            status=status.HTTP_201_CREATED
        )


class ApplyDiscount(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        code_data = request.data
        code = code_data['code'].strip()
        amount = float(code_data['amount'])
        try:
            discount_obj = Discount.objects.get(code=code_data['code'].upper())
            if discount_obj.status == "Active":
                discount = float(discount_obj.discount)
                if discount_obj.discount_type == 'Fixed':
                    amount_after_discout = float(amount) - float(discount)
                elif discount_obj.discount_type == 'Percentage':
                    discount = amount * (discount / 100)
                    amount_after_discout = float(amount) - float(discount)
                res = {
                    "code": code,
                    "status": "Applied",
                    "amount": amount,
                    "discount": discount,
                    "amount_after_discout": amount_after_discout
                }
                return JsonResponse(res, status=200)
            else:
                print("else")
                res = {
                    # "code": code_data['code'],
                    "status": "Rejected",
                    "amount": amount,
                }
            return JsonResponse(res, status=200)
        except BaseException as err:
            print(err)
            res = {
                "code": code_data['code'],
                "status": "Rejected",
                "amount": amount,
            }
            return JsonResponse(res, status=200)


class AddTaskActionTask(generics.CreateAPIView):
    serializer_class = AddActionTaskUserProgramSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            currentDate = datetime.today()
            data = {'task': request.data['task'], 'status': request.data['status'], 'program': request.data['program'],
                    'user': request.user.id}

            taskUser = ActionTaskUserProgram.objects.filter(user=request.user.id, task=request.data.get('task'),
                                                            program=request.data.get('program'),
                                                            created_at__gte=currentDate.replace(hour=0, minute=0,
                                                                                                second=0),
                                                            created_at__lte=currentDate.replace(hour=23, minute=59,
                                                                                                second=59))
            print(taskUser)
            if taskUser.count() > 0:
                taskUser.delete()
            # ActionTaskUserProgram.objects.all().delete()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=False)

            self.perform_create(serializer)
            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddLevelTrackerValue(generics.CreateAPIView):
    serializer_class = ProgramLevelValueSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            data = {'program': request.data['program'], 'level_tracker': request.data['level_tracker'],
                    'tag': request.data['tag'] if request.data['tag'] != 0 else None,
                    'user': request.user.id, 'date': request.data['date']}

            # taskUser = ActionTaskUserProgram.objects.filter(user=request.user.id, task=request.data.get('task'),
            #                                                program=request.data.get('program'))
            # if taskUser.exists():
            #    taskUser.delete()

            serializer = ProgramLevelValueSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            # print(serializer.data)

            level_value_id = serializer.save()

            values = request.data['values']
            for v in values:
                v['program_level'] = level_value_id.id

                serializer = ProgramLevelValueTypeSerializer(data=v)
                serializer.is_valid(raise_exception=True)
                id = serializer.save()
                print(v, id.id)

            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetLevelTrackerValue(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, program, level_tracker, userid, tag, days):
        # print('tag', tag, type(tag))
        if tag == '0' or tag == 0:
            return ProgramLevelValue.objects.filter(Q(program=program) & Q(level_tracker=level_tracker)
                                                    & Q(user=userid) & Q(
                date__gte=datetime.now() - timedelta(days=days)))
        else:
            return ProgramLevelValue.objects.filter(Q(program=program) & Q(level_tracker=level_tracker)
                                                    & Q(user=userid) & Q(tag=tag) & Q(
                date__gte=datetime.now() - timedelta(days=days)))

    @never_cache
    def get(self, request, program, level_tracker, tag, days):
        # print('pt :', program, tag)
        queryset = self.get_queryset(program, level_tracker, request.user.id, tag, int(days))
        print(queryset)
        serializer = ProgramLevelValueSerializer2(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data
        for d in data:
            s = ProgramLevelValueTypeSerializer(ProgramLevelValueType.objects.filter(program_level=d['id']), many=True)
            d['values'] = s.data

        return JsonResponse(data, safe=False)


class RemoveLevelTrackerValue(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            level_tracker_value = ProgramLevelValue.objects.filter(user=request.user.id, id=request.data.get('id'))
            if level_tracker_value.exists():
                level_tracker_value.delete()

            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddSymptomTrackerValue(generics.CreateAPIView):
    serializer_class = ProgramSymptomTrackerValueDateSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            data = {'program': request.data['program'], 'user': request.user.id, 'date': request.data['date'],
                    'frequency': request.data['frequency']}

            serializer = ProgramSymptomTrackerValueDateSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            symptom_value_id = serializer.save()

            values = request.data['values']
            for v in values:
                v['program_symptom_tracker_value_date'] = symptom_value_id.id

                serializer = ProgramSymptomTrackerValueSerializer(data=v)
                serializer.is_valid(raise_exception=True)
                id = serializer.save()
                print(v, id.id)

            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetSymptomTrackerValue(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, program, userid, days):
        return ProgramSymptomTrackerValueDate.objects.filter(
            Q(program=program) & Q(user=userid) & Q(date__gte=datetime.now() - timedelta(days=days)))

    @never_cache
    def get(self, request, program, days):
        print('pt :', program)
        queryset = self.get_queryset(program, request.user.id, int(days))

        serializer = ProgramSymptomTrackerValueDateSerializer(
            queryset,
            many=True,
            context={'user_id': request.user.id}
        )
        data = serializer.data
        for d in data:
            s = ProgramSymptomTrackerValueSerializer(
                ProgramSymptomTrackerValue.objects.filter(program_symptom_tracker_value_date_id=d['id']), many=True)
            d['values'] = s.data

        return JsonResponse(data, safe=False)


class RemoveSymptomTrackerValue(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            symptom_tracker_value = ProgramSymptomTrackerValueDate.objects.filter(user=request.user.id,
                                                                                  id=request.data.get('id'))
            print('exists : ', symptom_tracker_value.exists())
            if symptom_tracker_value.exists():
                symptom_tracker_value.delete()

            return JsonResponse(
                data={'message': 'success'},
                status=status.HTTP_201_CREATED)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgramCategoryWiseList(generics.ListAPIView):
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get Categories
        categories = json.loads(self.request.data.get('categories', '[]'))
        if categories:
            programs = Program.objects.filter(category__in=categories, status='active')
        else:
            programs = Program.objects.filter(status='active')
        queryset = self.filter_queryset(programs)
        return queryset

    def get(self, request):

        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        page = self.paginate_queryset(self.get_queryset())
        program_serializer = ProgramCategoryWiseSerializer(self.get_queryset(), many=True)
        # return Response(program_serializer.data, status=status.HTTP_200_OK)
        data = program_serializer.data
        return self.get_paginated_response(data[start_limit:end_limit])


class UpcomingPrograms(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get(self, request):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 3))
        end_limit = start_limit + limit

        today = datetime.today().strftime('%Y-%m-%d')

        programs = Program.objects.filter(status='active', start_date__gt=today)
        page = self.paginate_queryset(programs)
        program_serializer = UpcomingProgramSerializer(programs, many=True)
        data = program_serializer.data
        # return Response(data,status=status.HTTP_200_OK)
        return self.get_paginated_response(data[start_limit:end_limit])


class ExpertAllPrograms(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        program = Program.objects.filter(expert=user, status='active').values_list('id', flat=True)
        program_batch = ProgramBatch.objects.filter(program_id__in=program)
        return program_batch

    def list(self, request, *args, **kwargs):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 10))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        program_serailizer = ExpertAllProgramsSerializer(queryset, many=True)
        data = program_serailizer.data
        # return Response(program_serailizer.data)
        return self.get_paginated_response(data[start_limit:end_limit])


class ExpertUpcomingSession(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        today = datetime.today()
        program = Program.objects.filter(expert=user, status='active').values_list('id', flat=True)
        upcoming_session = ProgramBatchSession.objects.filter(programBatch__program_id__in=program,
                                                              session_date__gte=today.date(),
                                                              end_time__gte=today.time())
        return upcoming_session

    def list(self, request, *args, **kwargs):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 4))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        session_serailizer = UpcomingSessionSerializer(queryset, many=True)
        data = session_serailizer.data
        # return Response(program_serailizer.data)
        return self.get_paginated_response(data[start_limit:end_limit])


class ExpertProgramBatchDetails(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, batch_id):
        data = {}
        batch = ProgramBatch.objects.get(id=batch_id)

        data['program_id'] = batch.program_id
        data['batch_id'] = batch.id
        data['description'] = batch.program.html_description
        data['duration_in_weeks'] = batch.program.duration_in_weeks
        data['start_date'] = batch.batch_start_date.strftime('%d %b %Y')
        data['end_date'] = batch.batch_end_date.strftime('%d %b %Y')
        data['status'] = batch.batch_status
        data['category'] = ProgramCategory.objects.filter(program=batch.program).values_list('category__name',
                                                                                             flat=True)
        data['program_title'] = batch.program.title + "|" + batch.title

        batch_session = ProgramBatchSession.objects.filter(programBatch_id=batch_id)
        session_serializer = ProgramBatchSessionDetailsSerializer(batch_session, many=True)

        data['sessions'] = session_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        print(request.data)
        try:
            session = request.data['session']
            session_resource = request.data['session_resources']

            if session:
                for data in session:
                    session = ProgramBatchSession.objects.create(title=data['title'], description=data['description'],
                                                                 sequence_num=data['sequence_num'],
                                                                 duration=data['duration'],
                                                                 session_type=data['session_type'],
                                                                 session_date=data['session_date'],
                                                                 start_time=data['start_time'],
                                                                 end_time=data['end_time'],
                                                                 programBatch_id=data['programBatch_id']).save()

            if session_resource:
                for sr in session_resource:
                    session_resource = ProgramBatchSessionResource.objects.create(
                        programBatchSession_id=sr['programBatchSession_id'], title=sr['title'],
                        description=sr['description'], doc_file=sr['doc_file']).save()
            return Response({"message": "Records added successfully"}, status=status.HTTP_200_OK)
        except BaseException as err:
            print(err)
            return JsonResponse({
                'message': 'Something went wrong',
                'error': str(err)
            },
                safe=False,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExpertAppProgramDetails(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, batch_id):
        try:
            user = request.user
            program_details = {}
            program_batch = ProgramBatch.objects.get(id=batch_id)
            program = Program.objects.get(id=program_batch.program_id)
            program_serializer = ProgramDetailsSerializer(program, context={'batch': program_batch})

            batch_session = ProgramBatchSession.objects.filter(programBatch_id=batch_id).order_by('session_date')
            session_serializer = ProgramBatchSessionDetailsSerializer(batch_session, many=True)

            program_details['program'] = program_serializer.data
            program_details['overviews'] = OverviewSerializer(Overview.objects.filter(program_id=program.id),
                                                              many=True).data
            program_details['sessions'] = session_serializer.data

            review = Review.objects.filter(program=program, status='approved').order_by('-created_date')[:2]
            program_details['reviews'] = ProgramReviewDetailSerializer(review, many=True).data
            program_details['faqs'] = ProgramFrequentlyAskedQuestionSerializer(program.frequentlyaskedquestion_set,
                                                                               many=True).data

            return Response(success_response(program_details), status=status.HTTP_200_OK)
        except ProgramBatch.DoesNotExist:
            return JsonResponse(error_response("Program Batch Does not exist"), status=status.HTTP_404_NOT_FOUND)
        except Program.DoesNotExist:
            return JsonResponse(error_response("Program Does not exist"), status=status.HTTP_404_NOT_FOUND)
        except BaseException as err:
            return JsonResponse(error_response(str(err)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgramListing(generics.ListAPIView):
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['program__title']

    def get_queryset(self):
        user = self.request.user
        current_date = datetime.today().strftime('%Y-%m-%d')
        category = self.request.query_params.get('category', None)

        if user.is_authenticated:
            if self.request.user.user_type == 'expert':
                queryset = ProgramBatch.objects.filter(batch_status='open', program__expert=user)
            elif self.request.user.user_type == 'customer':
                programBatchIds = ProgramBatchUser.objects.filter(programBatch__batch_end_date__gte=current_date,
                                                                  user=user).values_list(
                    'programBatch_id', flat=True)
                queryset = ProgramBatch.objects.prefetch_related('program').filter(
                    Q(batch_status='open', id__in=programBatchIds) | Q(batch_status='open',
                                                                       additional_start_date__gte=current_date,
                                                                       program__status='active'))
        else:
            queryset = ProgramBatch.objects.prefetch_related('program').filter(batch_status='open',
                                                                               additional_start_date__gte=current_date,
                                                                               program__status='active')

        if category:
            category = [int(c) for c in category.split(',')]
            queryset = queryset.filter(program__category__in=category)

        return queryset

    def list(self, request, *args, **kwargs):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = ProgramListSerializer(queryset, many=True, context={'user': request.user})
        # return Response(program_serailizer.data)
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)


class ProgramFavoriteList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        currentDate = datetime.today().strftime('%Y-%m-%d')
        queryset = ProgramBatch.objects.prefetch_related('program').all()

        if self.request.user.user_type == 'expert':
            queryset = queryset.filter(program__expert_id=self.request.user.id)
        else:
            programIds = FavoriteProgram.objects.filter(user_id=self.request.user.id).values_list('program_id',
                                                                                                  flat=True)
            print(f"{programIds=}")
            queryset = queryset.filter(program_id__in=programIds).distinct('program_id')

        print(f"{queryset=}")
        return queryset

    def list(self, request, *args, **kwargs):
        # Pagination Detail
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = ProgramListSerializer(queryset, many=True, context={'user': request.user})
        # return Response(program_serailizer.data)
        data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data
        return Response(success_response(data), status=status.HTTP_200_OK)


class ProgramReview(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user = request.user
            if Program.objects.filter(id=request.data['program']).exists():
                files = request.data.getlist('files')
                print(f"{files=}")
                review = Review.objects.create(title=request.data['title'], description=request.data['description'],
                                               program_id=request.data['program'], user=user,
                                               rating=request.data['rating'])
                review.save()
                if files:
                    for f in files:
                        review_files = ReviewFiles.objects.create(files=f, review=review).save()

                serializer = ProgramReviewSerializer(review, many=False)
                return Response(success_response(serializer.data), status=status.HTTP_201_CREATED)
            else:
                return Response(error_response("Program not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(error_response(str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self, program_id):
        queryset = Review.objects.filter(program_id=program_id, status='approved')
        return queryset

    def list(self, request, program_id):
        if Program.objects.filter(id=program_id).exists():
            # Pagination Detail
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.get_queryset(program_id)
            page = self.paginate_queryset(queryset)
            serializer = ProgramReviewDetailSerializer(queryset, many=True)
            data = self.get_paginated_response(serializer.data[start_limit:end_limit]).data

            review_data = {}
            review_data['program_rating'] = Program.objects.get(id=program_id).rating
            review_data['total_review'] = Review.objects.filter(program_id=program_id, status='approved').count()
            review_data['total_rating'] = \
            Review.objects.filter(program_id=program_id, status='approved').aggregate(total=Sum('rating'))['total']
            review_data['review'] = data
            return Response(success_response(review_data), status=status.HTTP_200_OK)
        else:
            return Response(error_response("Program not found"), status=status.HTTP_404_NOT_FOUND)


class ReviewLike(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, review_id):
        try:
            user = request.user
            if Review.objects.filter(id=review_id,like=user).exists():
                return Response(error_response("You have already liked this review"),status=status.HTTP_200_OK)
            review = Review.objects.get(id=review_id)
            review.like.add(user)
            review.save()

            return Response(success_response("Successfully added like for review"), status=status.HTTP_201_CREATED)
        except Review.DoesNotExists:
            return Response(error_response("Review not found"),status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(error_response(str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, review_id):
        try:
            user = request.user

            review = Review.objects.get(id=review_id)
            review.like.remove(user)
            review.save()

            return Response(success_response("Successfully removed like for review"), status=status.HTTP_200_OK)
        except Review.DoesNotExists:
            return Response(error_response("Review not found"),status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(error_response(str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)