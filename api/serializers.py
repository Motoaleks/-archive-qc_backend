from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from api.models import User, Quest, Question


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'created_at', 'updated_at',
                  'first_name', 'last_name', 'password',
                  'confirm_password',)
        read_only_fields = ('created_at', 'updated_at',)

        def create(self, validated_data):
            return User.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.username = validated_data.get('username', instance.username)
            instance.save()

            password = validated_data.get('password', None)
            confirm_password = validated_data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            update_session_auth_hash(self.context.get('request'), instance)

            return instance


class QuestionSerializer(serializers.ModelSerializer):
    # quest = QuestSerializer(read_only=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'photo', 'text', 'name', 'description', 'latitude', 'longitude')
        read_only_fields = ('id', 'created_at', 'updated_at')
'''
        def get_validation_exclusions(self, *args, **kwargs):
        exclusion = super(QuestionSerializer, self).get_validation_exclusion()
        return exclusion + ['quest']
'''


class QuestSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, required=False)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quest
        fields = ('id', 'name', 'timelimit', 'author', 'description',
                  'photo', 'questions')
        read_only_fields = ('id', 'created_at', 'updated_at', 'questions')

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        quest = Quest.objects.create(**validated_data)
        for question_data in questions:
            Question.objects.create(quest=quest, **question_data)
        return quest

    def update(self, instance, validated_data):
        validated_data.pop('questions')
        return super().update(instance, validated_data)

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(QuestSerializer, self).get_validation_exclusions()
        return exclusions + ['author']
