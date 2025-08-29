# myapp/urls.py
from django.urls import path
from .views import generate_story,home,stories
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('generate-story/', generate_story, name='generate'),
    path('', home, name= "index"),
    path("stories",stories,name ="stories")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
