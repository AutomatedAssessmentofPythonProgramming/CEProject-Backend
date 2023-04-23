from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from .models import Team, Exercise, Membership, Submission, Workbook
from authentication.models import User
import uuid

class UserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', ]
        expandable_fields = {
          'members': ('api.MemberSerializer', {'many': True}),
          'submissions' : ('api.SubmissionSerializer', {'many': True}),
        }

class TeamCreationSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Team 
        fields = ['pk', 'name', 'detail']
        
    def create(self, validated_data):
        # Generate a unique invite code
        invite_code = str(uuid.uuid4())[:8]

        # Check if the generated invite code already exists
        while Team.objects.filter(inviteCode=invite_code).exists():
            invite_code = str(uuid.uuid4())[:8]

        # Assign the unique invite code
        validated_data['inviteCode'] = invite_code

        # Create the team instance
        team = Team.objects.create(**validated_data)

        return team

class TeamSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Team 
        fields = ['pk', 'name', 'detail', 'inviteCode']
        expandable_fields = {
          'users': ('api.UserSerializer', {'many': True}),
          'members': ('api.MemberSerializer', {'many': True}),
          'workbooks': ('api.WorkbookSerializer', {'many': True}),
        }
        
    def create(self, validated_data):
        # Generate a unique invite code
        invite_code = str(uuid.uuid4())[:8]

        # Check if the generated invite code already exists
        while Team.objects.filter(inviteCode=invite_code).exists():
            invite_code = str(uuid.uuid4())[:8]

        # Assign the unique invite code
        validated_data['inviteCode'] = invite_code

        # Create the team instance
        team = Team.objects.create(**validated_data)

        return team
        
class ExerciseSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'instruction', 'created', 'source_code', 'updated', 'config_code', 'unittest']
        expandable_fields = {
          'submissions': ('api.SubmissionSerializer', {'many': True}),
          'workbooks': ('api.WorkbookSerializer', {'many': True}),
        }

class MemberSerializer(FlexFieldsModelSerializer):
    class Meta:
        model =  Membership
        # fields = ['user', 'team', 'isStaff']
        fields = ['isStaff']
        expandable_fields = {
          'user': ('api.UserSerializer'),
          'team': ('api.TeamSerializer')
        }
        
class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ('id', 'user', 'team', 'isStaff')
        
        
class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=255)
    
    def validate_invite_code(self, value):
        user = self.context['request'].user
        team = Team.objects.filter(inviteCode=value).first()

        if not team:
            raise serializers.ValidationError("Invalid invite code")

        if Membership.objects.filter(user=user, team=team).exists():
            raise serializers.ValidationError("User is already a member of the team")

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        team = Team.objects.get(inviteCode=validated_data['invite_code'])
        membership = Membership.objects.create(user=user, team=team)
        return membership
    
class SubmissionSerializer(FlexFieldsModelSerializer):
    class Meta:
        model =  Submission
        # fields = ['user', 'team', 'isStaff']
        fields = ['code', 'dateSubmit']
        expandable_fields = {
          'user': ('api.UserSerializer'),
          'exercise': ('api.ExerciseSerializer'),
        }
        
class WorkbookSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Workbook
        fields = ['team', 'exercise', 'week', 'openTime', 'dueTime', 'isOpen', 'dateCreated']
        # expandable_fields = {
        #   'team': ('api.TeamSerializer'),
        #   'exercise': ('api.ExerciseSerializer'),
        # }

        
class TeamMemberSerializer(serializers.Serializer):
    team = TeamSerializer()
    member = MemberSerializer()

class FileUploadSerializer(serializers.Serializer):
  file = serializers.FileField()
  
class MultiFileUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )
    
class ExerciseWorkbookSerializer(serializers.Serializer):
    exercise_title = serializers.CharField(source='exercise.title')
    exercise_instruction = serializers.CharField(source='exercise.instruction')
    exercise_source_code = serializers.CharField(source='exercise.source_code')
    exercise_config_code = serializers.CharField(source='exercise.config_code')
    exercise_unittest = serializers.CharField(source='exercise.unittest')
    workbook_open_time = serializers.DateTimeField(source='openTime')
    workbook_due_time = serializers.DateTimeField(source='dueTime')
    workbook_is_open = serializers.BooleanField(source='isOpen')
    workbook_team_id = serializers.IntegerField(source='team.id')
    workbook_week = serializers.IntegerField()
    
    def create(self, validated_data):
        exercise_data = validated_data.pop('exercise')
        workbook_data = validated_data
        exercise = Exercise.objects.create(**exercise_data)
        workbook = Workbook.objects.create(exercise=exercise, **workbook_data)
        return workbook
    
    def update(self, instance, validated_data):
        exercise_data = validated_data.pop('exercise')
        exercise = instance.exercise
        for attr, value in exercise_data.items():
            setattr(exercise, attr, value)
        exercise.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
      
class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'studentid']    
        
class SubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercise.title')
    exercise_id = serializers.IntegerField(source='exercise.id')
    user_username = serializers.CharField(source='user.username')
    user_firstname = serializers.CharField(source='user.firstname')
    user_lastname = serializers.CharField(source='user.lastname')

    class Meta:
        model = Submission
        fields = ['id', 'exercise_title', 'exercise_id', 'user_username', 'user_firstname', 'user_lastname', 'dateSubmit', 'isLate', 'isDone', 'score', 'code']
        
class UserSubmissionRequestSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    