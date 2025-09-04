from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.ManyToManyField(Genre)
    release_date = models.DateField()
    synopsis = models.TextField()
    poster = models.ImageField(upload_to='posters/')
    telegram_link = models.URLField()
    average_rating = models.FloatField(default=0)
    trailer_url = models.URLField(blank=True, null=True)  # NEW: Trailer addition - YouTube URL for the trailer

    def update_average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            total = sum([review.rating for review in reviews])
            self.average_rating = total / len(reviews)
        else:
            self.average_rating = 0
        self.save()

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.movie.update_average_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.movie.update_average_rating()

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    wishlist = models.ManyToManyField(Movie, related_name='wishlisted_by', blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # New field for profile photo

    def __str__(self):
        return self.user.username


# Signals moved to signals.py to avoid circular imports
# Keep this commented out or remove it
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     try:
#         instance.userprofile.save()
#     except UserProfile.DoesNotExist:
#         UserProfile.objects.create(user=instance)