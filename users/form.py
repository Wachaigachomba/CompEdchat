from django import forms
# from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from wachai.models import Reply  # Import the Reply model
from django.conf import settings
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit
from wachai.models import Post  # added recent

User = get_user_model()


# added recent
class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'video']


class PasswordResetPhoneForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        max_length=13,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+254 7XX XXX XXX",
            "value": "+254 "
        })
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        # Normalize the phone number: remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")
        # Ensure the phone number starts with +254
        if not phone.startswith("+254"):
            # Remove any leading zeros and prepend +254
            phone = "+254" + phone.lstrip("0")
        # Check if a user with the normalized phone number exists in the profile
        if not User.objects.filter(profile__phone_number=phone).exists():
            raise forms.ValidationError("Phone number not registered.")
        return phone


class VerifyResetCodeForm(forms.Form):
    phone_number = forms.CharField(widget=forms.HiddenInput())
    reset_code = forms.CharField(
        max_length=6,
        required=True,
        label="Reset Code",
        help_text="Enter the 6-digit code sent to your phone."
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="New Password"
    )


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image']  # Include the field(s) you want
        widgets = {
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 4, 'style': 'resize: vertical;'}),
        }


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email',
                  'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Remove default help texts for password fields
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""

        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Div(
                Field('username', css_class='mx-2', wrapper_class='form-group'),
                Field('email', css_class='mx-2', wrapper_class='form-group'),
                Field('phone_number', css_class='mx-2', wrapper_class='form-group'),
                Field('password1', css_class='mx-2', wrapper_class='form-group'),
                Field('password2', css_class='mx-2', wrapper_class='form-group'),
                css_class='w-100'
            ),
            Submit('submit', 'Register', css_class='btn btn-outline-info ml-2')
        )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['phone_number', 'image']
