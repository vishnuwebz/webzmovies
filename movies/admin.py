# movies/admin.py
from django.contrib import admin
from .models import Genre, Movie, Review, UserProfile

class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "release_date", "average_rating", "trailer_url"]  # NEW: Include trailer_url in list_display
    list_filter = ["genre", "release_date"]
    search_fields = ["title"]

class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "movie", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["user__username", "movie__title"]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "telegram_id", "phone_number"]
    list_filter = ["user"]
    search_fields = ["user__username", "telegram_id", "phone_number"]

admin.site.register(Genre)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserProfile, UserProfileAdmin)