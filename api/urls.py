from django.urls import path
from .views import ( TeamViewSet,
                     ExerciseViewSet,
                     ListTeamView,
                     CreateTeamView,
                     DetailTeamView,
                     TeamMemberView
                    )

urlpatterns = [
    # path('teams/', TeamViewSet.as_view({'get': 'list'}), name='team-list'),
    # path('teams/<int:pk>', TeamViewSet.as_view({'get': 'retrieve'}), name='team-detail'),
    # path('exercises/', ExerciseViewSet.as_view({'get': 'list'}), name='exercise-list'),
    # path('exercises/<int:pk>', ExerciseViewSet.as_view({'get': 'retrieve'}), name='excercise-detail'),
    path('team-list/', ListTeamView.as_view(), name='teams-list'),
    path('team/', CreateTeamView.as_view(), name='team-create'),
    path('team/<int:pk>', DetailTeamView.as_view(), name='team-detail'),
    path('team/<int:pk>/members/', TeamMemberView.as_view(), name='team-member'),
]
