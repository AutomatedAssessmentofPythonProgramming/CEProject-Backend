from django.urls import path
from .views import ( TeamViewSet,
                     ExerciseViewSet,
                    )

urlpatterns = [
    path('teams/', TeamViewSet.as_view({'get': 'list'}), name='team-list'),
    path('teams/<int:pk>', TeamViewSet.as_view({'get': 'retrieve'}), name='team-detail'),
    path('exercises/', ExerciseViewSet.as_view({'get': 'list'}), name='exercise-list'),
    path('exercises/<int:pk>', ExerciseViewSet.as_view({'get': 'retrieve'}), name='excercise-detail'),
]

# urlpatterns = [
#     path('teams/', views.TeamList.as_view(), name='team-list'),
#     path('teams/<int:pk>', views.TeamDetail.as_view(), name='team-detail'),
#     path('exercises/', views.ExerciseList.as_view(), name='exercise-list'),
#     path('exercises/<int:pk>', views.ExerciseDetail.as_view(), name='exercise-detail'),
#     # path('members/', views.MemberList.as_view(), name='member-list')
# ]

# router = DefaultRouter()
# router.register('team', TeamViewSet, basename='Team')
# router.register('exercise', ExerciseViewSet, basename='Exercise')