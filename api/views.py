from rest_framework import generics
from .models import Team, Exercise
from .serializers import TeamSerializer, ExerciseSerializer
from rest_framework import permissions

class TeamList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class TeamDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class ExerciseList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

class ExerciseDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer