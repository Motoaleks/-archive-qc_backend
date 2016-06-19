from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.Permissions import IsAccountOwner
from api.models import User, Quest, Game, QuestResult, Question, File
from api.serializers import UserSerializer, QuestSerializer, GameSerializer, StatusQuestionSerializer, FileSerializer

from geopy.distance import vincenty


class UserViewSet(viewsets.ModelViewSet):
    # lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.AllowAny(),

        if self.request.method == 'POST':
            return permissions.AllowAny(),

        return permissions.IsAuthenticated(), IsAccountOwner(),

    def create(self, request, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            User.objects.create_user(**serializer.validated_data)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)


class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer

    def get_permissions(self):
        # return (permissions.AllowAny(), )
        if self.request.method in permissions.SAFE_METHODS:
            return permissions.AllowAny(),
        if self.request.method == 'POST':
            return permissions.IsAuthenticated(),
        return permissions.IsAdminUser(),

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        return instance


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, **kwargs):
        try:
            quest = Quest.objects.get(id=self.request.data["quest_id"])
        except Quest.DoesNotExist:
            return Response({
                'status': 'Not found',
                'message': 'There is no such quest.'
            }, status=status.HTTP_404_NOT_FOUND)

        game = Game.objects.create(user=self.request.user, quest=quest)
        for question in quest.questions.all():
            QuestResult.objects.create(game=game, question=question)
        return Response(GameSerializer().to_representation(game))

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Game.objects.filter(user=user)

    @detail_route(methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, pk=None):
        try:
            question = Question.objects.get(id=request.data["question_id"])
            game = Game.objects.get(id=pk)
            result = QuestResult.objects.get(question=question, game=game)
        except (Question.DoesNotExist, Game.DoesNotExist, QuestResult.DoesNotExist):
            return Response({
                'status': 'Not found',
                'message': 'There is no such game or question.'
            }, status=status.HTTP_404_NOT_FOUND)
        if "answer" in request.data and result.status == 0:
            if request.data["answer"] == question.name:
                result.status = 1
                result.save()
                good = True
        elif "latitude" in request.data and "longitude" in request.data and result.status == 1:
            dist = vincenty((request.data["latitude"], request.data["longitude"]),
                            (question.latitude, question.longitude))
            if dist.m < 100:
                result.status = 2
                result.save()
                good = True

        if good:
            return Response(StatusQuestionSerializer().to_representation(result))
        return Response({'status': 'Bad request',
                         'message': 'Impossible to pass check with such request'
                         }, status=status.HTTP_400_BAD_REQUEST)


class FileViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    serializer_class = FileSerializer
    queryset = File.objects.all()

    def get_permissions(self):
        return permissions.IsAuthenticated(),

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            f = File.objects.create(**serializer.validated_data)
            upload = request.data['file']
            f.file.save(upload.name, upload)
            return Response(serializer.to_representation(f))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)