from datetime import timedelta
from functools import wraps
import hashlib, hmac, random

from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.conf import settings

from .forms import (
    ReviewForm,
    CustomUserCreationForm,
    AdminMovieForm,
    AdminGenreForm,
    AdminReviewForm,
    AdminUserSearchForm,
    ProfileForm,  # New import
)
from .models import Movie, Review, UserProfile, Genre
from django.http import HttpResponse
def healthz(request):
    return HttpResponse("OK", status=200)
# =================== PUBLIC VIEWS ===================

def home(request):
    movies = Movie.objects.all().order_by('-release_date')[:10]
    movie_of_the_day = random.choice(movies) if movies.exists() else None
    return render(request, 'home.html', {'movies': movies, 'movie_of_the_day': movie_of_the_day})


def movie_list(request):
    movies = Movie.objects.all().order_by('-release_date')
    genre_filter = request.GET.get('genre', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'newest')

    if genre_filter:
        movies = movies.filter(genre__name__icontains=genre_filter)
    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query) |
            Q(synopsis__icontains=search_query) |
            Q(genre__name__icontains=search_query)
        ).distinct()

    if sort_by == 'rating':
        movies = movies.order_by('-average_rating')
    elif sort_by == 'title':
        movies = movies.order_by('title')
    elif sort_by == 'oldest':
        movies = movies.order_by('release_date')
    else:
        movies = movies.order_by('-release_date')

    all_genres = Genre.objects.all()
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movie_list.html', {
        'movies': page_obj,
        'all_genres': all_genres,
        'selected_genre': genre_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('movies:movie_detail', movie_id=movie.id)
    else:
        form = ReviewForm()
    return render(request, 'movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'form': form,
    })


@login_required
def wishlist(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    movies = profile.wishlist.all()
    return render(request, "wishlist.html", {"wishlist_movies": movies})


@login_required
def add_to_wishlist(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, pk=movie_id)
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if movie in profile.wishlist.all():
            profile.wishlist.remove(movie)
            return JsonResponse({"status": "removed", "message": f"{movie.title} removed from wishlist"})
        else:
            profile.wishlist.add(movie)
            return JsonResponse({"status": "added", "message": f"{movie.title} added to wishlist"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def remove_from_wishlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if movie in profile.wishlist.all():
        profile.wishlist.remove(movie)
        message = f'Removed {movie.title} from your wishlist'
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({'success': True, 'message': message})
        else:
            messages.success(request, message)
    return redirect('wishlist')


# ========================== AUTH ==========================

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Account created successfully 🎉")
            return redirect("movies:home")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! 👋")
            return redirect("movies:home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("movies:home")



@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    return render(request, 'profile.html', {'profile': profile, 'reviews': reviews, 'avg_rating': avg_rating})


# =================== TELEGRAM AUTH ===================

def telegram_callback(request):
    data = request.GET.dict()
    auth_data = data.copy()
    hash_value = auth_data.pop("hash", None)

    if not hash_value:
        return redirect("movies:signup")

    secret = hashlib.sha256("8158802654:AAHmSwp5-BHKYTtc6ZHNTXn0xprzSntXLCc".encode()).digest()
    check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])

    h = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if h != hash_value:
        return redirect("movies:signup")

    telegram_id = data.get("id")
    username = data.get("username") or f"user_{telegram_id}"

    user, created = User.objects.get_or_create(username=f"tg_{telegram_id}", defaults={"first_name": username})
    if created:
        user.set_unusable_password()
        user.save()

    login(request, user)
    return redirect("movies:home")


# =================== PHONE SIGNUP (EMAIL OTP) ===================

def phone_signup(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if not email or not phone:
            messages.error(request, "Both phone and email are required.")
            return redirect("movies:phone_signup")

        otp = random.randint(100000, 999999)

        request.session["otp"] = str(otp)
        request.session["email"] = email
        request.session["phone"] = phone

        send_mail(
            subject="Your WEBZMOVIES OTP",
            message=f"Your OTP for WEBZMOVIES signup is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, f"OTP has been sent to {email}. Please check your inbox.")
        return redirect("movies:verify_otp")

    return render(request, "phone_signup.html")


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        email = request.session.get("email")
        phone = request.session.get("phone")

        if entered_otp == session_otp:
            if User.objects.filter(username=phone).exists():
                messages.info(request, "User already exists. Please login.")
                return redirect("movies:login")

            user = User.objects.create_user(
                username=phone,
                email=email,
                password="defaultpassword123"
            )
            messages.success(request, "Account created successfully! Please login.")
            return redirect("movies:login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("movies:verify_otp")

    return render(request, "verify_otp.html")


# =================== ADMIN HELPERS ===================

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden("You do not have permission to access the admin dashboard.")
        return view_func(request, *args, **kwargs)
    return _wrapped


# =================== ADMIN DASHBOARD ===================

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
from .models import Movie, Genre, Review, User
from collections import defaultdict

def is_staff_user(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    stats = {
        "movie_count": Movie.objects.count(),
        "genre_count": Genre.objects.count(),
        "review_count": Review.objects.count(),
        "user_count": User.objects.count(),
        "avg_rating": Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0,
    }
    latest_reviews = Review.objects.select_related("movie", "user").order_by("-created_at")[:8]
    top_movies = Movie.objects.annotate(rc=Count("review")).order_by("-rc", "-release_date")[:8]
    movies = Movie.objects.order_by('-release_date')[:5]  # Recent 5 movies

    return render(request, "admin_dashboard.html", {
        "stats": stats,
        "latest_reviews": latest_reviews,
        "top_movies": top_movies,
        "movies": movies,
    })

@login_required
@user_passes_test(is_staff_user)
def analytics(request):
    # Total movies by genre
    genre_stats = Movie.objects.values('genre__name').annotate(movie_count=Count('id')).order_by('-movie_count')

    # Average rating by month (last 6 months) - SQLite compatible
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=180)
    monthly_ratings = Review.objects.filter(created_at__range=(start_date, end_date)) \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(avg_rating=Avg('rating')) \
        .order_by('month')

    # User activity (reviews per user)
    user_activity = User.objects.annotate(review_count=Count('review')).order_by('-review_count')[:5]

    context = {
        'genre_stats': genre_stats,
        'monthly_ratings': monthly_ratings,
        'user_activity': user_activity,
    }
    return render(request, 'analytics.html', context)
# =================== ADMIN MOVIES ===================

@staff_required
def admin_movies(request):
    q = request.GET.get("q", "").strip()
    genre_id = request.GET.get("genre")
    movies = Movie.objects.all().prefetch_related("genre")

    if q:
        movies = movies.filter(Q(title__icontains=q) | Q(synopsis__icontains=q))
    if genre_id:
        movies = movies.filter(genre__id=genre_id)

    movies = movies.order_by("-release_date", "title").distinct()
    paginator = Paginator(movies, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "admin_movies.html", {
        "page_obj": page_obj,
        "genres": Genre.objects.order_by("name"),
        "q": q,
        "genre_id": genre_id,
    })


@staff_required
def admin_movie_add(request):
    if request.method == "POST":
        form = AdminMovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save()
            messages.success(request, f"Movie “{movie.title}” added.")
            return redirect("movies:admin_movies")
    else:
        form = AdminMovieForm()
    return render(request, "admin_add_movie.html", {"form": form, "genres": Genre.objects.all()})


@staff_required
def admin_movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = AdminMovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, f"Movie “{movie.title}” updated.")
            return redirect("movies:admin_movies")
    else:
        form = AdminMovieForm(instance=movie)
    return render(request, "admin_edit_movie.html", {"form": form, "movie": movie})


@staff_required
def admin_movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        title = movie.title
        movie.delete()
        messages.success(request, f"Movie “{title}” deleted.")
        return redirect("movies:admin_movies")
    return render(request, "admin_confirm_delete.html", {
        "object": movie,
        "object_type": "Movie",
        "cancel_url": "movies:admin_movies",
    })


# =================== ADMIN GENRES ===================

@staff_required
def admin_genres(request):
    genres = Genre.objects.order_by("name")
    paginator = Paginator(genres, 30)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "admin_genres.html", {"page_obj": page_obj})


@staff_required
def admin_genre_add(request):
    if request.method == "POST":
        form = AdminGenreForm(request.POST)
        if form.is_valid():
            g = form.save()
            messages.success(request, f"Genre “{g.name}” added.")
            return redirect("movies:admin_genres")
    else:
        form = AdminGenreForm()
    return render(request, "admin_add_genre.html", {"form": form})


@staff_required
def admin_genre_edit(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        form = AdminGenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            messages.success(request, f"Genre “{genre.name}” updated.")
            return redirect("movies:admin_genres")
    else:
        form = AdminGenreForm(instance=genre)
    return render(request, "admin_edit_genre.html", {"form": form, "genre": genre})


@staff_required
def admin_genre_delete(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    if request.method == "POST":
        name = genre.name
        genre.delete()
        messages.success(request, f"Genre “{name}” deleted.")
        return redirect("movies:admin_genres")
    return render(request, "admin_confirm_delete.html", {
        "object": genre,
        "object_type": "Genre",
        "cancel_url": "movies:admin_genres",
    })


# =================== ADMIN REVIEWS ===================

@staff_required
def admin_reviews(request):
    q = request.GET.get("q", "").strip()
    reviews = Review.objects.select_related("movie", "user").order_by("-created_at")
    if q:
        reviews = reviews.filter(
            Q(movie__title__icontains=q) |
            Q(user__username__icontains=q) |
            Q(comment__icontains=q)
        )
    paginator = Paginator(reviews, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "admin_reviews.html", {"page_obj": page_obj, "q": q})


@staff_required
def admin_review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("movies:admin_reviews")
    return render(request, "admin_confirm_delete.html", {
        "object": review,
        "object_type": "Review",
        "cancel_url": "movies:admin_reviews",
    })


# =================== ADMIN USERS ===================

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "is_staff", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


@staff_required
def admin_users(request):
    form = AdminUserSearchForm(request.GET or None)
    users = User.objects.all().order_by("-is_superuser", "-is_staff", "username")
    if form.is_valid():
        q = form.cleaned_data.get("q") or ""
        if q:
            users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))
    paginator = Paginator(users, 30)
    page_obj = paginator.get_page(request.GET.get("page"))
    profiles = {p.user_id: p for p in UserProfile.objects.filter(user__in=[u.id for u in page_obj.object_list])}
    return render(request, "admin_users.html", {
        "page_obj": page_obj,
        "profiles": profiles,
        "form": form
    })


@staff_required
def admin_user_add(request):
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully!")
            return redirect("movies:admin_users")
    else:
        form = AdminUserForm()
    return render(request, "admin_add_user.html", {"form": form})


@staff_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully!")
            return redirect("movies:admin_users")
    else:
        form = AdminUserForm(instance=user)
    return render(request, "admin_edit_user.html", {"form": form, "user": user})


@staff_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        uname = user.username
        user.delete()
        messages.success(request, f"User “{uname}” deleted.")
        return redirect("movies:admin_users")
    return render(request, "admin_confirm_delete.html", {
        "object": user,
        "object_type": "User",
        "cancel_url": "movies:admin_users",
    })


# =================== PROFILE SETTINGS ===================

@login_required
def profile_settings(request):
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('movies:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_settings.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('movies:home')
    return render(request, 'confirm_delete_account.html')


# =================== ONLINE PLAYER ===================


import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from urllib.parse import urlparse, parse_qs
import re

@login_required
def play_online(request):
    embed_url = None
    video_type = None
    error_message = None
    if request.method == 'POST':
        video_link = request.POST.get('video_link', '').strip()
        if video_link:
            parsed_url = urlparse(video_link)
            hostname = parsed_url.hostname.lower()

            # YouTube
            if 'youtube.com' in hostname or 'youtu.be' in hostname:
                video_type = 'iframe'
                if parsed_url.path.startswith('/embed/'):
                    video_id = parsed_url.path.split('/embed/')[1].split('?')[0]
                elif 'youtu.be' in hostname:
                    video_id = parsed_url.path[1:].split('?')[0]
                else:
                    query_params = parse_qs(parsed_url.query)
                    video_id = query_params.get('v', [None])[0]
                if video_id:
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                else:
                    error_message = "Could not extract a valid video ID from the YouTube link. Use 'Share' > 'Copy Link'."

            # Vimeo
            elif 'vimeo.com' in hostname:
                video_type = 'iframe'
                video_id = parsed_url.path.split('/')[1].split('?')[0]
                if video_id:
                    embed_url = f"https://player.vimeo.com/video/{video_id}"

            # Dailymotion
            elif 'dailymotion.com' in hostname:
                video_type = 'iframe'
                video_id = parsed_url.path.split('/video/')[1].split('_')[0]
                if video_id:
                    embed_url = f"https://www.dailymotion.com/embed/video/{video_id}"

            # Twitch
            elif 'twitch.tv' in hostname:
                video_type = 'iframe'
                video_id = parsed_url.path.split('/')[1]
                if video_id:
                    embed_url = f"https://player.twitch.tv/?channel={video_id}&parent=localhost"  # Adjust parent for production

            # Facebook
            elif 'facebook.com' in hostname and '/video.php' in parsed_url.path:
                video_type = 'iframe'
                video_id = parse_qs(parsed_url.query).get('v', [None])[0]
                if video_id:
                    embed_url = f"https://www.facebook.com/video/embed?video_id={video_id}"

            # TikTok
            elif 'tiktok.com' in hostname:
                video_type = 'iframe'
                video_id = parsed_url.path.split('/video/')[1].split('?')[0]
                if video_id:
                    embed_url = f"https://www.tiktok.com/embed/v2/{video_id}"

            # Instagram
            elif 'instagram.com' in hostname and '/reel/' in parsed_url.path:
                video_type = 'iframe'
                video_id = parsed_url.path.split('/reel/')[1].split('?')[0]
                if video_id:
                    # Attempt to use Instagram oEmbed (requires API setup)
                    try:
                        response = requests.get(
                            f"https://graph.facebook.com/v20.0/instagram_oembed",
                            params={"url": video_link, "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN"}
                        )
                        data = response.json()
                        if 'html' in data:
                            embed_url = data['html']  # oEmbed provides the iframe HTML
                        else:
                            error_message = "Instagram embedding requires an API token. Fallback not available."
                    except Exception:
                        error_message = "Instagram embedding failed. Please use a supported platform or check API setup."

            # Direct video (e.g., .mp4, .webm, .ogg)
            elif any(parsed_url.path.endswith(ext) for ext in ['.mp4', '.webm', '.ogg']):
                video_type = 'direct'
                embed_url = video_link

            if not embed_url and not error_message:
                error_message = (
                    "Unsupported or invalid video link. Supported platforms include YouTube, Vimeo, Dailymotion, Twitch, "
                    "Facebook, TikTok, Instagram, or direct video URLs (e.g., .mp4). Ensure you copy the link correctly: "
                    "For YouTube, click 'Share' > 'Copy Link'; for Instagram/TikTok, use the share option and copy the URL."
                )

    return render(request, 'play_online.html', {
        'embed_url': embed_url,
        'video_type': video_type,
        'error_message': error_message
    })