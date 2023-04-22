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
                     ListSubmissionView,
                     SubmissionView,
                     FileSubmissionView,
                     MultiFileUploadView,
                     CreateWorkbooksView,
                     RetrieveUpdateDeleteWorkbookView,
                     AddMemberWithInviteCodeView,
                     GetExerciseByIdView
                    )

urlpatterns = [
    path('team-list/', ListTeamView.as_view(), name='teams-list'),
    path('team/', CreateTeamView.as_view(), name='team-create'),
    path('team/<int:pk>', DetailTeamView.as_view(), name='team-detail'),
    path('team/<int:pk>/members/', TeamMemberView.as_view(), name='team-member'),
    path('team/<int:pk>/exercises/', ListExerciseView.as_view(), name='exercise-list'),
    path('exercise/', ExerciseView.as_view(), name='exercise-create'),
    path('exercise/<int:pk>', DetailExerciseView.as_view(), name='exercise-detail'),
    path('submissions-list/<int:pk>', SubmissionView.as_view(), name='submission-list'),
    path('exercise/<int:pk>/submit', FileSubmissionView.as_view(), name='upload-file'),
    # path('multi-upload-file/', MultiFileUploadView.as_view(), name='multi-upload-file'),
    path('workbook/', CreateWorkbooksView.as_view(), name='create-workbook'),
    path('workbook/<int:pk>', RetrieveUpdateDeleteWorkbookView.as_view(), name='workbook-detail'),
    path('add-member/', AddMemberWithInviteCodeView.as_view(), name='add-member'),
    path('submission/<int:exerciseId>/team/<int:teamId>', ListSubmissionView.as_view(), name='manage-submission'),
    
    path('exercise/<int:exerciseId>/<int:teamId>', GetExerciseByIdView.as_view(), name='get-exercisebyid'),
]
