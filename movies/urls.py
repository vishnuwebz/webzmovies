from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = "movies"

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('add_to_wishlist/<int:movie_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),  # New URL for settings
    path('profile/delete/', views.delete_account, name='delete_account'),  # New URL for delete confirmation


    # --- custom admin ---
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('dashboard/analytics/', views.analytics, name='admin_analytics'),  # Updated to dashboard/analytics/

    # Movies
    path("dashboard/movies/", views.admin_movies, name="admin_movies"),
    path("dashboard/movies/add/", views.admin_movie_add, name="admin_add_movie"),
    path("dashboard/movies/<int:pk>/edit/", views.admin_movie_edit, name="admin_edit_movie"),
    path("dashboard/movies/<int:pk>/delete/", views.admin_movie_delete, name="admin_movie_delete"),

    # Genres
    path("dashboard/genres/", views.admin_genres, name="admin_genres"),
    path("dashboard/genres/add/", views.admin_genre_add, name="admin_genre_add"),
    path("dashboard/genres/<int:pk>/edit/", views.admin_genre_edit, name="admin_genre_edit"),
    path("dashboard/genres/<int:pk>/delete/", views.admin_genre_delete, name="admin_genre_delete"),

    # Reviews
    path("dashboard/reviews/", views.admin_reviews, name="admin_reviews"),
    path("dashboard/reviews/<int:pk>/delete/", views.admin_review_delete, name="admin_delete_review"),

    # User management
    path("dashboard/users/", views.admin_users, name="admin_users"),
    path("dashboard/users/add/", views.admin_user_add, name="admin_user_add"),
    path("dashboard/users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("dashboard/users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),

    path("telegram/callback/", views.telegram_callback, name="telegram_callback"),

    path("phone-signup/", views.phone_signup, name="phone_signup"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),

    # Custom password reset routes
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', success_url=reverse_lazy('movies:password_reset_done')), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name="password_reset_complete"),

    path('play-online/', views.play_online, name='play_online'),
]