from django.contrib import admin
from django.urls import path, include
# from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from api.views import TeamViewSet, ExerciseViewSet

router = DefaultRouter()
router.register('team', TeamViewSet, basename='Team')
router.register('exercise', ExerciseViewSet, basename='Exercise')
# router.register('exercise', ExerciseViewSet, basename='Exercise')
# router.register(r'product', ProductViewSet, basename='Product')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]

# urlpatterns = format_suffix_patterns(urlpatterns)