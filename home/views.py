from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth.decorators import user_passes_test
from .forms import NewsForm
from .models import News


def staff_member_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@staff_member_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user  # تعیین نویسنده به کاربر جاری
            news.save()
            return redirect('news_list')  # پس از ایجاد خبر، به صفحه لیست اخبار بروید
    else:
        form = NewsForm()
    return render(request, 'news/create_news.html', {'form': form})

@staff_member_required
def edit_news(request, news_id):
    news = get_object_or_404(News, id=news_id)

    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect('news_list')  # پس از ویرایش، به صفحه لیست اخبار بروید
    else:
        form = NewsForm(instance=news)

    return render(request, 'news/edit_news.html', {'form': form, 'news': news})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to the home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def profile_view(request):
    return render(request, 'profile.html')  # Profile page



def search_view(request):
    query = request.GET.get('q', '')
    # Perform the search logic here
    return render(request, 'search_results.html', {'query': query})

def home_view(request):
    news_items = News.objects.filter(is_active=True).order_by('-published_at')
    return render(request, 'index.html', {'news_items': news_items})
    # return render(request, 'index.html')


def news_list(request):
    news_items = News.objects.filter(is_active=True).order_by('-published_at')
    return render(request, 'news/news_list.html', {'news_items': news_items})
