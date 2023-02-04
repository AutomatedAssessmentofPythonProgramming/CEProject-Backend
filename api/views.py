from .models import Team, Exercise, Membership, Workbook
from authentication.models import User
from .serializers import (TeamSerializer, 
                          ExerciseSerializer, 
                          TeamMemberSerializer, 
                          MemberSerializer
                          )
from rest_flex_fields.views import FlexFieldsMixin
from rest_flex_fields import is_expanded
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from rest_framework.views import APIView
from rest_framework import permissions, response, status, generics
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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
    
    def get(self, request):
        try:
            # user = User.objects.get(id=request.user.id)
            # ถ้าไม่มี permissions.IsAuthenticated จะเกิด error ถ้าไม่ authentication ต้อง login ก่อน
            memberships = Membership.objects.filter(user=request.user.id)
            teams = []
            for membership in memberships:
                members = Membership.objects.filter(team=membership.team.id)
                teams.append({'id': membership.team.id, 
                              'name': membership.team.name,
                              'count': members.count()
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
            members = Membership.objects.filter(team=pk)
        except Membership.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        members_data = []
        for member in members:
            user_data = {
                'username': member.user.username,
                'email': member.user.email,
                'id': member.user.id
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
        try:
            workbooks = Workbook.objects.filter(team=pk)
        except Workbook.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)
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
                            },
                         })
        return response.Response(data, status=status.HTTP_200_OK)