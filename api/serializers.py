from datetime import timedelta
from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from api.models import User, Quest, Question, Game, QuestResult, File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'uploaded_at', 'file')
        read_only_fields = ('id', 'uploaded_at', 'file')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password',
                  'confirm_password',)
        read_only_fields = ('created_at', 'updated_at',)

        def create(self, validated_data):
            return User.objects.create()

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


class QuestSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, required=False)
    questions = QuestionSerializer(many=True, write_only=True, required=True)
    photo = serializers.PrimaryKeyRelatedField(required=True, queryset=File.objects.all())

    class Meta:
        model = Quest
        fields = ('id', 'name', 'timelimit', 'author', 'description',
                  'photo', 'questions')
        read_only_fields = ('id', 'created_at', 'updated_at', 'questions')

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        #file_id = validated_data.pop('photo')
        print(validated_data)
        ##validated_data["photo"] = File.objects.get(id=file_id)
        quest = Quest.objects.create(**validated_data)
        #photo = File.objects.get(id=file_id)
        #quest.photo = photo
        #quest.save()
        for question_data in questions:
            Question.objects.create(quest=quest)
        return quest

    def update(self, instance, validated_data):
        validated_data.pop('questions')
        return super().update(instance, validated_data)

    def get_validation_exclusions(self, *args, **kwargs):
        exclusions = super(QuestSerializer, self).get_validation_exclusions()
        return exclusions + ['author']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['photo'] = File.objects.get(id=repr['photo']).file.url
        return repr


class StatusQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = QuestResult
        fields = ('question',)

    def to_representation(self, instance):
        base_data = super().to_representation(instance)
        result = {"status": instance.status, "id": base_data["question"]["id"]}
        if instance.status == 0:
            result["text"] = base_data["question"]["text"]
            result["photo"] = base_data["question"]["photo"]
        elif instance.status > 0:
            result["name"] = base_data["question"]["name"]
            result["longitude"] = base_data["question"]["longitude"]
            result["latitude"] = base_data["question"]["latitude"]
        if instance.status == 2:
            result["description"] = base_data["question"]["description"]
        return result


class GameSerializer(serializers.ModelSerializer):
    questions = StatusQuestionSerializer(many=True)
    quest = QuestSerializer()

    class Meta:
        model = Game
        fields = ('questions', 'quest')

    def to_representation(self, instance):
        base_rep = super().to_representation(instance)
        name = base_rep["quest"]["name"]
        endtime = instance.startTime + timedelta(seconds=base_rep["quest"]["timelimit"])
        return {"name": name, "endtime": endtime, "questions": base_rep["questions"]}

    def update(self, instance, validated_data):
        pass

