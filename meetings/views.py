from django.shortcuts import render

# Create your views here.

from meetings.models import Meeting
from meetings.serializers import MeetingSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from meetings.serializers import UserSerializer
from rest_framework import permissions
from meetings.permissions import IsOwnerOrReadOnly


class MeetingList(generics.ListCreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MeetingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer