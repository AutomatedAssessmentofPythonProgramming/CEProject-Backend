from .models import Team, Exercise, Membership
from .serializers import TeamSerializer, ExerciseSerializer
from rest_framework import permissions
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_flex_fields import is_expanded

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
    
    