from django.urls import path
from .views import (PostListView,
                    PostDetailView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView
                    )
from users.views import Reply
from . import views
from .views import ReplyCreateView
from django.conf import settings
from django.conf.urls.static import static
from .views import latest_posts
from .views import calendar_view
from datetime import datetime
from django.shortcuts import redirect

urlpatterns = [
    path('', PostListView.as_view(), name='wachai-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/reply/', ReplyCreateView.as_view(), name='post-reply'),
    path('about/', views.about, name='wachai-about'),
    path('latest-posts/', latest_posts, name='latest_posts'),
   # path('calendar/', lambda request: redirect(f'/calendar/{datetime.now().year}/{datetime.now().month}/'), name='calendar-current'),
    path('calendar/<int:year>/<int:month>/', calendar_view, name='calendar'),
 
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
