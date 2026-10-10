import calendar
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  View
                                  )
from wachai.models import Post, Reply
from users.form import ReplyForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from users.form import PostCreateForm
from django.contrib.messages.views import SuccessMessageMixin


def home(request):
    if not request.user.is_authenticated:
        # Redirect to login page if not logged in
        return render(request, 'users/login.html')
    #calendar_url = reverse('calendar', kwargs={'year': datetime.now().year, 'month': datetime.now().month}) 

    context = {
        'posts': Post.objects.all(),
        'year': datetime.now().year,  
        'month': datetime.now().month  
    }
    return render(request, 'wachai/home.html', context)


class ReplyCreateView(CreateView):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.save()
        # Redirect to post
        return HttpResponseRedirect(post.get_absolute_url())


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'wachai/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    login_url = 'login'  # Redirect to login page if not logged in
    paginate_by = 4


# added


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = ReplyForm()  # Add reply form to context
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'wachai/post_detail.html'
    login_url = 'login'  # Redirect to login page if not logged in


# added


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = ReplyForm()  # Add reply form to context
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.save()
            # Reload page after submitting reply
            return redirect(post.get_absolute_url())


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm  # Use the updated form with media fields

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    login_url = 'login'  # Redirect to login page if not logged in

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
    
def latest_posts(request):
    posts = Post.objects.order_by('-date_posted')[:10]  # Fetch latest 10 posts
    return render(request, 'wachai/latest_posts.html', {'posts': posts})


def calendar_view(request, year, month):
    try:
        year, month = int(year), int(month)  # Convert to integers
        today = datetime.today()

        # Generate the HTML calendar
        cal = calendar.HTMLCalendar().formatmonth(year, month)

        # Highlight today's date if it's in the current month
        if year == today.year and month == today.month:
            current_day = f'>{today.day}<'
            highlighted_day = f' style="background-color: #ffcc00; color: black; font-weight: bold;">{today.day}<'
            cal = cal.replace(current_day, highlighted_day)

        # Add Bootstrap styling to the table
        cal = cal.replace('<table border="0"', '<table class="table table-bordered table-hover"')

        return render(request, 'wachai/calendar.html', {
            'calendar': cal,
            'month': month,
            'year': year
        })

    except ValueError:
        return render(request, '404.html')  # Show error page if invalid values are passed

def about(request):
    return render(request, 'wachai/about.html', {'title': 'About'})
