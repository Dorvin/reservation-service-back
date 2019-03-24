from django.forms import widgets
from rest_framework import serializers
from meetings.models import Meeting
from django.contrib.auth.models import User


class MeetingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.pk')
    
    def validate(self, attrs):
        if attrs['sinceWhen'] >= attrs['tilWhen']:
            raise serializers.ValidationError("since time is late than untill time")
        meetings = Meeting.objects.all()
        for meeting in meetings:
            if self.instance != None:
                if meeting.id == self.instance.id:
                    continue
            if meeting.sinceWhen <= attrs['sinceWhen'] and attrs['sinceWhen'] < meeting.tilWhen:
                raise serializers.ValidationError("there is already existing meeting on the time you want")
            if meeting.sinceWhen < attrs['tilWhen'] and attrs['tilWhen'] <= meeting.tilWhen:
                raise serializers.ValidationError("there is already existing meeting on the time you want")
            if meeting.sinceWhen > attrs['sinceWhen'] and attrs['tilWhen'] > meeting.tilWhen:
                raise serializers.ValidationError("there is already existing meeting on the time you want")
        return attrs

    class Meta:
        model = Meeting
        fields = ('id', 'created', 'sinceWhen', 'tilWhen', 'user')

class UserSerializer(serializers.ModelSerializer):
    meetings = serializers.PrimaryKeyRelatedField(many=True, queryset=Meeting.objects.all())
    class Meta:
        model = User
        fields = ('id', 'username', 'meetings')
