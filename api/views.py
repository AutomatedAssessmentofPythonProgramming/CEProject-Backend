from .models import Team, Exercise, Membership, Workbook, Submission
from authentication.models import User
from .serializers import (TeamSerializer, 
                          ExerciseSerializer, 
                          TeamMemberSerializer, 
                          MemberSerializer,
                          FileUploadSerializer,
                          MultiFileUploadSerializer,
                          )
from rest_flex_fields.views import FlexFieldsMixin
from rest_flex_fields import is_expanded
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework import permissions, response, status, generics
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response

from django.core.files.storage import default_storage

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import os 
import subprocess
import json

class TeamViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamSerializer
    # queryset = Team.objects.all()
    permit_list_expands = ['users', 'members', 'workbooks', 'workbooks.exercise']
    
    def get_queryset(self):
        queryset = Team.objects.all()

        if is_expanded(self.request, 'users'):
            queryset = queryset.prefetch_related('users')
            
        if is_expanded(self.request, 'members'):
            queryset = queryset.prefetch_related('members')
        
        if is_expanded(self.request, 'workbooks'):
            queryset = queryset.prefetch_related('workbooks')
            
        if is_expanded(self.request, 'workbooks__exercise'):
            queryset = queryset.prefetch_related('workbooks__exercise')

        return queryset
    
class ExerciseViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseSerializer
    permit_list_expands = ['submissions', 'submissions.user', 'workbooks']
    
    def get_queryset(self):
        queryset = Exercise.objects.all()
            
        if is_expanded(self.request, 'submissions'):
            queryset = queryset.prefetch_related('submissions')
            
        if is_expanded(self.request, 'submissions__user'):
            queryset = queryset.prefetch_related('submissions__user')
            
        if is_expanded(self.request, 'workbooks'):
            queryset = queryset.prefetch_related('workbooks')
            
        return queryset
    
class ListTeamView(generics.GenericAPIView):
    '''
    Return List of Team that user joined
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamMemberSerializer
    
    def get(self, request):
        try:
            # user = User.objects.get(id=request.user.id)
            # ถ้าไม่มี permissions.IsAuthenticated จะเกิด error ถ้าไม่ authentication ต้อง login ก่อน
            # find team of member
            memberships = Membership.objects.filter(user=request.user.id)
            teams = []
            for membership in memberships:
                members = Membership.objects.filter(team=membership.team.id)
                teams.append({'id': membership.team.id, 
                              'name': membership.team.name,
                              'membersCount': members.count()
                              })
            return response.Response({'teams': teams}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        
class CreateTeamView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    @swagger_auto_schema(
        operation_description="Create Team",
        responses={
            201: openapi.Response("Successfully created team"),
            400: openapi.Response("Invalid request"),
        },
        request_body=TeamSerializer
    )
    def post(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # team_data = serializer.data
            # team_serializer = TeamSerializer(data=team_data)
            # team_serializer.is_valid(raise_exception=True)
            # team = team_serializer.save()
            team = serializer.save()
            member_data = {"isStaff": True}
            member_serializer = MemberSerializer(data=member_data)
            member_serializer.is_valid(raise_exception=True)
            member = member_serializer.save(user=request.user, team=team)
            return response.Response({'team': serializer.data, 
                                      'member': {'username':member.user.username,
                                                 'email':member.user.email,
                                                 'status':member_serializer.data
                                                 },
                                      }, 
                                     status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetailTeamView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    @swagger_auto_schema(
        operation_description="Delete a team by ID",
        responses={
            204: openapi.Response("Successfully deleted team"),
            400: openapi.Response("Invalid request"),
            404: openapi.Response("Team not found"),
        },
    )
    def delete(self, request, pk):
        try:
            team = Team.objects.get(id=pk)
            team.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request, pk):
        try:
            team = Team.objects.get(id=pk)
            serializer = TeamSerializer(team)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Patch Success"),
            400: openapi.Response("Invalid request"),
            404: openapi.Response("Not found"),
        },
        request_body=TeamSerializer
    )
    def patch(self, request, pk):
        try:
            team = Team.objects.get(id=pk)
            serializer = TeamSerializer(team, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

class TeamMemberView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    def get(self, request, pk):
        try:
            isMember = Membership.objects.get(team=pk, user=request.user.id)
        except Membership.DoesNotExist:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            members = Membership.objects.filter(team=pk)
        except Membership.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        members_data = []
        for member in members:
            user_data = {
                'username': member.user.username,
                'email': member.user.email,
                'id': member.user.id,
                'studentid': member.user.studentid,
            }
            members_data.append(user_data)
        return response.Response({'members':members_data}, status=status.HTTP_200_OK)
    
class ExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    @swagger_auto_schema(
        operation_description="Create Exercise",
        responses={
            201: openapi.Response("Successfully created exercise"),
            400: openapi.Response("Invalid request"),
        },
        request_body=ExerciseSerializer
    )
    def post(self, request):
        serializer = ExerciseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner=request.user)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
        
class DetailExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    
    def get(self, request, pk):
        try:
            exercise = Exercise.objects.get(pk=pk)
            serializer = ExerciseSerializer(exercise)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exercise.DoesNotExist():
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        responses={
            200: openapi.Response("Patch Success"),
            400: openapi.Response("Invalid request"),
            404: openapi.Response("Not found"),
        },
        request_body=ExerciseSerializer
    )
    def patch(self, request, pk):
        try:
            exercise = Exercise.objects.get(id=pk)
            serializer = ExerciseSerializer(exercise, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exercise.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
            
    
    def delete(self, request, pk):
        try:
            exercise = Exercise.objects.get(id=pk)
            exercise.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
class ListExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    def get(self, request, pk):
        try:
            members = Membership.objects.get(team=pk, user=request.user.id)
        except Membership.DoesNotExist:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        
        workbooks = Workbook.objects.filter(team=pk)
        if not workbooks.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = []
        for workbook in workbooks:
            data.append({'dueTime': workbook.dueTime,
                         'openTime': workbook.openTime,
                         'isOpen': workbook.isOpen,
                         'week': workbook.week,
                         'Team': {
                             'pk': workbook.team.pk,
                             'name': workbook.team.name,
                            },
                         'exercise': {
                                'pk': workbook.exercise.pk,
                                'title': workbook.exercise.title,
                                'instruction': workbook.exercise.instruction,
                                'created': workbook.exercise.created,
                                'updated': workbook.exercise.updated,
                                'isDone': workbook.isDone
                            },
                         })
        return response.Response(data, status=status.HTTP_200_OK)
    
class ListSubmissionView(generics.GenericAPIView):
    '''
    Which Team
    Which exercise
    want User that submit exercise and get score
    '''
    # permission_classes=(permissions.IsAuthenticated)
    
    def get(self, request, teamId, exerciseId):
        submissions = Submission.objects.filter(exercise=exerciseId, team=teamId)
        if not submissions.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = []
        # print(submissions)
        for submission in submissions:
            user = submission.user
            data.append(
                {
                    'user': {
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'username': user.username,
                        'email': user.email,
                        'studentid': user.studentid,
                    },
                    'dateSubmit': submission.dateSubmit,
                    'score': submission.score,
                }
            )
        exercise = submissions[0].exercise
        exercise_data = {
            'pk': exercise.pk,
            'title': exercise.title,
            'instruction': exercise.instruction,
            'created': exercise.created,
            'updated': exercise.updated,
            'owner': {
                'email': exercise.owner.email
                },
        }
        return response.Response({'exericse': exercise_data,'data':data}, status=status.HTTP_200_OK)

class SubmissionView(generics.GenericAPIView):
    '''
    ดูว่าส่งอะไรไปแล้วบ้าง
    '''
    
    def get(self, request):
        try:
            submissions = Submission.objects.filter(user=request.user.pk)
        except Submission.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        data = []
        for submission in submissions:
            exercise = submission.exercise
            data.append(
                {
                    'exercise': {
                            'title': exercise.title,
                        },
                    'submitDate': submission.dateSubmit,
                    'score': submission.score,
                }
            )
            
        return response.Response(data, status=status.HTTP_200_OK)
 
 
#  ตรวจ
class FileSubmissionView(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    # serializer_class = FileUploadSerializer
    
    @swagger_auto_schema(
        operation_id="upload_file",
        operation_description="Upload a file",
        manual_parameters=[openapi.Parameter(
                            name="file",
                            in_=openapi.IN_FORM,
                            type=openapi.TYPE_FILE,
                            # required=True,
                            description="Document"
                            )],
    )
    def post(self, request, pk, format=None):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            # Save the uploaded file to the server
            uploaded_file = serializer.validated_data['file']
            file_name = uploaded_file.name
            file_name = default_storage.save(uploaded_file.name, uploaded_file)
            print("Uploaded file name:", file_name)
            
            exercise = Exercise.objects.get(pk=pk)
            filename = exercise.title
            code = exercise.source_code
            config = exercise.config_code
            unittest = exercise.unittest
            if config.strip() == '' or unittest.strip() == '':
                return Response({'error': 'configcode or unittest error'}, status=status.HTTP_400_BAD_REQUEST)
            
            with open(filename + '.py', 'w') as outfile:
                outfile.write(code)
            with open(filename + '.yaml', 'w') as outfile:
                outfile.write(config)
            with open(filename + '_tests.py', 'w') as outfile:
                outfile.write(unittest)
                
            results = 'results.json'
                
            cmd = ['python3', '-m', 'graderutils.main', filename+'.yaml', '--develop-mode']
            with open(results, 'w') as outfile:
                subprocess.run(cmd, stdout=outfile)
            with open(results, 'r') as infile:
                data = json.load(infile)
                
            os.remove(filename + '.py')
            os.remove(filename + '.yaml')
            os.remove(filename + '_tests.py')
            os.remove(uploaded_file.name)
            os.remove(results)
            
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=400)
        
class MultiFileUploadView(generics.GenericAPIView):
    parser_classes = [MultiPartParser]
    # serializer_class = MultiFileUploadSerializer
    
    @swagger_auto_schema(
        # request_body=MultiFileUploadSerializer,
        operation_id="upload_multi_files",
        operation_description="Upload multiple files",
        responses={200: "Success", 400: "Bad Request"},
        manual_parameters=[
            openapi.Parameter(
                name="files",
                in_=openapi.IN_FORM,
                description="Multiple files to upload",
                type=openapi.TYPE_FILE,
                required=True,
                explode=True
            )
        ]
    )
    def post(self, request):
        file_serializer = MultiFileUploadSerializer(data=request.data)
        if file_serializer.is_valid():
            # Save the uploaded files to the server
            uploaded_files = file_serializer.validated_data['files']
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                print("Uploaded file name:", file_name)
                # Do something with the file
            return Response({'status': 'success'})
        else:
            return Response(file_serializer.errors, status=400)
    
class WorkbookView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated)
    
    def post(self, request):
        pass
    
    