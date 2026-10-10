from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Conversation

User = get_user_model()


def new_conversation(request):
    # List all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/new_conversation.html', {'users': users})


def initiate_chat(request, user_id):
    # Ensure the current user is authenticated (use @login_required if desired)
    other_user = get_object_or_404(User, id=user_id)

    # Look for an existing conversation with exactly these two participants
    conversation = Conversation.objects.filter(
        participants=request.user).filter(participants=other_user).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('chat:conversation_detail', conversation_id=conversation.id)


def inbox(request):
    # Get all conversations that include the current user
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'chat/inbox.html', {'conversations': conversations})


def room(request, room_name='general'):
    return render(request, 'chat/room.html', {
        'room_name': room_name,
    })


def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, id=conversation_id, participants=request.user)
    return render(request, 'chat/conversation_detail.html', {'conversation': conversation})


def profile_detail(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(request, 'users/profile_detail.html', {
        'profile_user': profile_user,
    })
