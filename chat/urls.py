from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('new/', views.new_conversation, name='new_conversation'),
    # For one-on-one chat initiation:
    path('initiate/<int:user_id>/', views.initiate_chat, name='initiate_chat'),
    # Conversation detail view:
    path('conversation/<int:conversation_id>/',
         views.conversation_detail, name='conversation_detail'),
    path('room/<str:room_name>/', views.room, name='room'),
]
