import random
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AbstractUser
from .form import (UserRegisterForm,
                   UserUpdateForm,
                   ProfileUpdateForm,
                   PasswordResetPhoneForm,
                   VerifyResetCodeForm)
from django.contrib.auth import logout
from django.core.cache import cache  # Store the reset code temporarily
from .sms_service import send_sms  # Function to send SMS
from django.contrib.auth import update_session_auth_hash
from wachai.models import Post, Reply
from .form import ReplyForm
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


def phone_password_reset(request):
    if request.method == "POST":
        form = PasswordResetPhoneForm(request.POST)
        if form.is_valid():
            # The form's clean_phone_number method normalizes the number.
            phone = form.cleaned_data["phone_number"]
            try:
                user = User.objects.get(profile__phone_number=phone)
            except User.DoesNotExist:
                messages.error(request, "No user is associated with that phone number.")
                return redirect("phone_password_reset")

            # Generate a 6-digit code
            reset_code = str(random.randint(100000, 999999))
            # Store the code in the cache (expires in 5 minutes)
            cache.set(f"reset_code_{phone}", reset_code, timeout=300)
            # Send the reset code via SMS
            send_sms(phone, f"Your password reset code is: {reset_code}")
            # Save phone number in the session to use in the confirmation view
            request.session["phone_number"] = phone
            messages.success(request, "Reset code sent to your phone.")
            # Redirect to the verification view
            return redirect("phone_reset_confirm")
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = PasswordResetPhoneForm()
    return render(request, "users/reset_password_phone.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from .form import VerifyResetCodeForm

User = get_user_model()

def phone_reset_confirm(request):
    phone = request.session.get("phone_number")
    if not phone:
        messages.error(request, "Phone number not found. Please try again.")
        return redirect("phone_password_reset")

    if request.method == "POST":
        form = VerifyResetCodeForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data["reset_code"]
            new_password = form.cleaned_data["new_password"]
            stored_code = cache.get(f"reset_code_{phone}")
            if stored_code and input_code == stored_code:
                try:
                    user = User.objects.get(profile__phone_number=phone)
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
                    return redirect("phone_password_reset")
                # Set the new password
                user.set_password(new_password)
                user.save()
                # Update session hash if the user is logged in
                update_session_auth_hash(request, user)
                # Delete the code from the cache
                cache.delete(f"reset_code_{phone}")
                messages.success(request, "Your password has been reset successfully.")
                return redirect("login")
            else:
                messages.error(request, "Invalid or expired reset code.")
    else:
        # Pre-populate the hidden phone number field in the form
        form = VerifyResetCodeForm(initial={"phone_number": phone})
    return render(request, "users/reset_password_code.html", {"form": form})


@login_required
def add_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.post = post
            reply.save()
            # Redirect back to the post
            return redirect('post-detail', pk=post_id)
    else:
        form = ReplyForm()
    return render(request, 'wachai/reply_form.html', {'form': form, 'post': post})


def manual_logout(request):
    print("Logout function triggered!")  # Debugging line
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Your account has been created! you are now able to login')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # Optionally, ensure a profile exists (if not using signals)
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
    return render(request, 'users/profile.html', context)
