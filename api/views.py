from .models import Team, Exercise, Membership, Workbook, Submission
from authentication.models import User
from .serializers import (TeamSerializer, 
                          ExerciseSerializer, 
                          TeamMemberSerializer, 
                          MemberSerializer,
                          FileUploadSerializer,
                          MultiFileUploadSerializer,
                          WorkbookSerializer,
                          MembershipSerializer,
                          InviteCodeSerializer,
                          UserDataSerializer,
                          SubmissionSerializer,
                          TeamCreationSerializer,
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
from tempfile import TemporaryDirectory

from .utils import process_uploaded_file

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
    
# New Controller  

# Get list of team that joined
class ListTeamView(generics.GenericAPIView):
    '''
    Return List of Team that user is member.
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
                teams.append({'pk': membership.team.pk, 
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
        request_body=TeamCreationSerializer
    )
    def post(self, request):
        serializer = TeamCreationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            team = serializer.save()
            member_data = {"isStaff": True}
            member_serializer = MemberSerializer(data=member_data)
            member_serializer.is_valid(raise_exception=True)
            member = member_serializer.save(user=request.user, team=team)
            return response.Response({'team': {
                                                "pk": team.pk,
                                                "name": team.name,
                                                "detail": team.detail,
                                                "inviteCode": team.inviteCode
                                                }, 
                                      'member': {'username':member.user.username,
                                                 'email':member.user.email,
                                                 'status':member_serializer.data
                                                 },
                                      }, 
                                     status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Update Get team by pk
class DetailTeamView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = TeamMemberSerializer
    queryset = Team.objects.all()
    
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
            membership = Membership.objects.get(user=request.user, team=team)

            if membership.isStaff:
                team.delete()
                return response.Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return response.Response({"detail": "You are not authorized to delete this team."}, status=status.HTTP_403_FORBIDDEN)

        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return response.Response({"detail": "You are not a member of this team."}, status=status.HTTP_403_FORBIDDEN)
    
    def get(self, request, pk):
        try:
            team = Team.objects.get(id=pk)
            membership = Membership.objects.get(user=request.user, team=team)

            # User is a member of the team
            serializer = TeamSerializer(team)
            serialized_data = serializer.data
            serialized_data['is_staff'] = membership.isStaff
            # print(team.inviteCode)
            return response.Response(serialized_data, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return response.Response({"detail": "You are not a member of this team."}, status=status.HTTP_403_FORBIDDEN)
    
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
            membership = Membership.objects.get(user=request.user, team=team)

            if membership.isStaff:
                serializer = TeamSerializer(team, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return response.Response(serializer.data, status=status.HTTP_200_OK)
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response({"detail": "You are not authorized to update this team."}, status=status.HTTP_403_FORBIDDEN)

        except Team.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return response.Response({"detail": "You are not a member of this team."}, status=status.HTTP_403_FORBIDDEN)

# Get members of team list
class TeamMemberView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MemberSerializer
    queryset = Team.objects.all()
    
    def get(self, request, pk):
        try:
            is_member = Membership.objects.get(team=pk, user=request.user.id)
        except Membership.DoesNotExist:
            return response.Response({"detail": "You are not a member of this team."}, status=status.HTTP_400_BAD_REQUEST)
        
        members = Membership.objects.filter(team=pk)
        
        if members.exists():
            serializer = UserDataSerializer([member.user for member in members], many=True)
            return response.Response({'members': serializer.data}, status=status.HTTP_200_OK)
        else:
            return response.Response({"detail": "No members found for this team."}, status=status.HTTP_404_NOT_FOUND)
    
# Add member by invite code
class AddMemberWithInviteCodeView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = InviteCodeSerializer
    
    @swagger_auto_schema(
        operation_description="Add Member",
        responses={
            201: openapi.Response("Successfully added member to team"),
            400: openapi.Response("Invalid request"),
        },
        request_body=InviteCodeSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            membership = serializer.save()
            response_data = {
                'user_pk': membership.user.pk,
                'user': membership.user.username,
                'team_pk': membership.team.pk,
                'team': membership.team.name,
                'isStaff': membership.isStaff,
                'isVerify': membership.isVerify
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

# Update Remove member from team
class RetrieveUpdateRemoveMemberView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()
    
    def get_object(self, pk):
        try:
            return Membership.objects.get(pk=pk)
        except Membership.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST

    def get(self, request, pk):
        membership = self.get_object(pk)
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)

    def delete(self, request, pk):
        membership = self.get_object(pk)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        membership = self.get_object(pk)
        serializer = MembershipSerializer(membership, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create Exercise
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
    
# Get Update Delete Exercise by id
class DetailExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.all()
    
    
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

            # Check if the request.user is the owner of the exercise
            if exercise.owner == request.user:
                serializer = ExerciseSerializer(exercise, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return response.Response(serializer.data, status=status.HTTP_200_OK)
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response({"detail": "You are not the owner of this exercise."}, status=status.HTTP_403_FORBIDDEN)

        except Exercise.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
            
    
    def delete(self, request, pk):
        try:
            exercise = Exercise.objects.get(id=pk)

            # Check if the request.user is the owner of the exercise
            if exercise.owner == request.user:
                exercise.delete()
                return response.Response(status=status.HTTP_200_OK)
            else:
                return response.Response({"detail": "You are not the owner of this exercise."}, status=status.HTTP_403_FORBIDDEN)

        except Exercise.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
# Get lists of exercise
class ListExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MembershipSerializer
    queryset = Exercise.objects.all()
    
    def get(self, request, pk):
        # Check is member of team
        try:
            members = Membership.objects.get(team=pk, user=request.user.id)
        except Membership.DoesNotExist:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        
        # Get workbook of team
        workbooks = Workbook.objects.filter(team=pk)
        if not workbooks.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = []
        for workbook in workbooks:
            # Check if submit exercise
            try:
                print(request.user.id, pk, workbook.exercise.pk)
                submission = Submission.objects.filter(user=request.user.id, team=pk, exercise=workbook.exercise.pk)
                
                if submission.exists():
                    isDone = submission[0].isDone
                else:
                    isDone = False

            except (Submission.DoesNotExist, IndexError):
                isDone = False
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
                                'isDone': isDone
                            },
                         })
        return response.Response(data, status=status.HTTP_200_OK)
    
# Get list of user that submit exercises filter by teamId and exerciseId
class ListSubmissionView(generics.GenericAPIView):
    '''
    Which Team
    Which exercise
    want User that submit exercise and get score
    '''
    permission_classes=(permissions.IsAuthenticated)
    serializer_class = SubmissionSerializer
    
    def get(self, request, teamId, exerciseId):
        # Get submission of team filtered by exerciseId and teamId
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

# Get list of exercise that submiss by student filter by teamId and userId
class SubmissionView(generics.GenericAPIView):
    '''
    ดูว่าส่ง exercises อะไรไปแล้วบ้าง user
    '''
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    
    def get(self, request, pk):
        try:
            submissions = Submission.objects.filter(user=request.user.pk, team=pk)
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
 
#  Assessment Code Here 
# ต้องตั้งชื่อไฟล์เป็น model.py source code ---> model.py
# unittest ต้องตรงกัน
class FileSubmissionView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = [MultiPartParser]
    serializer_class = FileUploadSerializer
    queryset = Exercise.objects.all()
    
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
            # uploaded_file = serializer.validated_data['file']
            # file_name = uploaded_file.name
            # file_name = default_storage.save(uploaded_file.name, uploaded_file)
            # print("Uploaded file name:", file_name)
            
            uploaded_file = serializer.validated_data['file']
            file_name = uploaded_file.name

            # Change the file extension to .py
            file_name_without_ext, file_ext = os.path.splitext(file_name)
            if file_ext.lower() == '.txt':
                file_name = file_name_without_ext + '.py'

            file_name = default_storage.save(file_name, uploaded_file)
            print("Uploaded file name:", file_name)
            
            exercise = Exercise.objects.get(pk=pk)
            # filename = 'grader_tests'
            
            code = exercise.source_code
            config = exercise.config_code
            unittest = exercise.unittest
            if config.strip() == '' or unittest.strip() == '':
                return Response({'error': 'configcode or unittest error'}, status=status.HTTP_400_BAD_REQUEST)
            
            with open('model' + '.py', 'w') as outfile:
                outfile.write(code)
            with open('test_config' + '.yaml', 'w') as outfile:
                outfile.write(config)
            with open('grader_tests.py', 'w') as outfile:
                outfile.write(unittest)
                
            results = 'results.json'
                
            cmd = ['python3', '-m', 'graderutils.main', 'test_config.yaml', '--develop-mode']
            with open(results, 'w') as outfile:
                subprocess.run(cmd, stdout=outfile)
            with open(results, 'r') as infile:
                data = json.load(infile)
            
            try:
                os.remove('model.py')
            except FileNotFoundError:
                print('model.py not found')

            try:
                os.remove('test_config.yaml')
            except FileNotFoundError:
                print('test_config.yaml not found')

            try:
                os.remove('grader_tests.py')
            except FileNotFoundError:
                print('grader_tests.py not found')

            try:
                os.remove(file_name)
            except FileNotFoundError:
                print(f'{file_name.name} not found')

            try:
                os.remove(results)
            except FileNotFoundError:
                print(f'{results} not found')
            
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# New Assessment
class SubmitExerciseView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_id="upload_file",
        operation_description="Upload a file",
        manual_parameters=[openapi.Parameter(
            name="file",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description="Document"
        )],
    )
    def post(self, request, pk, format=None):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            file_name = default_storage.save(uploaded_file.name, uploaded_file)

            exercise = Exercise.objects.get(pk=pk)

            with TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, file_name)
                default_storage.save(file_path, uploaded_file)

                data = process_uploaded_file(temp_dir, exercise)

                default_storage.delete(file_name)

            if data:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'configcode or unittest error'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MultiFileUploadView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
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

# Create workbook  
class CreateWorkbooksView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkbookSerializer
    
    def post(self, request):
        exercise_id = request.data.get("exercise")
        team_id = request.data.get("team")
        old_workbook = Workbook.objects.filter(exercise=exercise_id, team=team_id)

        if old_workbook.exists():
            return response.Response({'error': 'already exists'},status=status.HTTP_400_BAD_REQUEST)
            
        serializer = WorkbookSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

# Update Delete Get workbook by id
class RetrieveUpdateDeleteWorkbookView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkbookSerializer
    queryset = Workbook.objects.all()
    
    def get(self, request, pk):
        try:
            workbook = Workbook.objects.get(pk=pk)
            serializer = WorkbookSerializer(workbook)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Workbook.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            workbook = Workbook.objects.get(id=pk)
            serializer = WorkbookSerializer(workbook, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Workbook.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            workbook = Workbook.objects.get(id=pk)
            workbook.delete()
            return response.Response(status=status.HTTP_200_OK)
        except Workbook.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

    
class GetExerciseByIdView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ExerciseSerializer
    
    def get(self, request, exerciseId, teamId):
        try:
            exercise = Exercise.objects.get(pk=exerciseId)
            workbook = Workbook.objects.get(exercise=exerciseId, team=teamId)
            serializer = ExerciseSerializer(exercise)
            
            serialized_data = serializer.data
            serialized_data['due'] = workbook.dueTime
            return response.Response(serialized_data, status=status.HTTP_200_OK)
        except Exercise.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        except Workbook.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)


# Create exercise and workbook
# class CreateExerciseAndWorkbook(generics.GenericAPIView):
#     permission_classes = (permissions.IsAuthenticated, )
    
#     def post(self, request):
#         pass
    
# see score
# class RetrieveScoreView(generics.GenericAPIView):
#     permission_classes = (permissions.IsAuthenticated, )
    
#     def get(self, request):
#         pass
    
