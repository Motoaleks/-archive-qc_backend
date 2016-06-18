from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from api.Permissions import IsAccountOwner
from api.models import User, Quest
from api.serializers import UserSerializer, QuestSerializer


class UserViewSet(viewsets.ModelViewSet):
    # lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated(), IsAccountOwner(),)

    def create(self, request):
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
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)

        return (permissions.IsAuthenticated(),)

    # def create(self, request):
    #     serializer = self.serializer_class(data=request.data)
    #
    #     if serializer.is_valid():
    #         Quest.objects.create(**serializer.validated_data)
    #
    #         return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
    #
    #     return Response({
    #         'status': 'Bad request',
    #         'message': 'Account could not be created with received data.'
    #     }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)

        return super(QuestViewSet, self).perform_create(serializer)
