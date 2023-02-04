from django.urls import path
from .views import ( TeamViewSet,
                     ExerciseViewSet,
                     ListTeamView,
                     CreateTeamView,
                     DetailTeamView,
                     TeamMemberView,
                     ExerciseView,
                     DetailExerciseView,
                     ListExerciseView,
                    )

urlpatterns = [
    # path('teams/', TeamViewSet.as_view({'get': 'list'}), name='team-list'),
    # path('teams/<int:pk>', TeamViewSet.as_view({'get': 'retrieve'}), name='team-detail'),
    # path('exercises/', ExerciseViewSet.as_view({'get': 'list'}), name='exercise-list'),
    # path('exercises/<int:pk>', ExerciseViewSet.as_view({'get': 'retrieve'}), name='excercise-detail'),
    path('teams-list/', ListTeamView.as_view(), name='teams-list'),
    path('team/', CreateTeamView.as_view(), name='team-create'),
    path('team/<int:pk>', DetailTeamView.as_view(), name='team-detail'),
    path('team/<int:pk>/members/', TeamMemberView.as_view(), name='team-member'),
    path('exercise/', ExerciseView.as_view(), name='exercise-create'),
    path('exercise/<int:pk>', DetailExerciseView.as_view(), name='exercise-detail'),
    path('exercise-list/<int:pk>', ListExerciseView.as_view(), name='exercise-list'),
]
