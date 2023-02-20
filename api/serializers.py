from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from .models import Team, Exercise, Membership, Submission, Workbook
from authentication.models import User

class UserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', ]
        expandable_fields = {
          'members': ('api.MemberSerializer', {'many': True}),
          'submissions' : ('api.SubmissionSerializer', {'many': True}),
        }

class TeamSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Team 
        fields = ['pk', 'name', 'detail']
        expandable_fields = {
          'users': ('api.UserSerializer', {'many': True}),
          'members': ('api.MemberSerializer', {'many': True}),
          'workbooks': ('api.WorkbookSerializer', {'many': True}),
        }
        
class ExerciseSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'instruction', 'created', 'source_code', 'updated']
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
        fields = ['openTime', 'dueTime', 'isOpen']
        expandable_fields = {
          'team': ('api.TeamSerializer'),
          'exercise': ('api.ExerciseSerializer'),
        }

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ('id', 'user', 'team', 'isStaff')
        
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