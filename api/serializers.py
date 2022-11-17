from rest_framework import serializers
from .models import Team, Exercise

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team 
        fields = ['id', 'name', 'detail', 'created']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'instruction', 'created', 'source_code'] 