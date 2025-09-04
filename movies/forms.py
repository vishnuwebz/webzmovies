from django import forms
from .models import Review, UserProfile, Movie, Genre
from django.contrib.auth.models import User

# ==========================
# Review Form
# ==========================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

# ==========================
# Minimal User Signup Form
# ==========================
class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match 🫠")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # securely hash password
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)  # create linked profile
        return user

# ==========================
# Admin Movie Form
# ==========================
class AdminMovieForm(forms.ModelForm):
    release_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "input"})
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": "8", "class": "select"})
    )
    trailer_url = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={"placeholder": "https://www.youtube.com/watch?v=VIDEO_ID", "class": "input"}
        )
    )

    class Meta:
        model = Movie
        fields = ["title", "release_date", "telegram_link", "poster", "synopsis", "genres", "trailer_url"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input"}),
            "telegram_link": forms.URLInput(attrs={"placeholder": "https://t.me/...", "class": "input"}),
            "poster": forms.ClearableFileInput(attrs={"accept": "image/*", "class": "input"}),
            "synopsis": forms.Textarea(attrs={"rows": 6, "class": "textarea"}),
        }

# ==========================
# Admin Genre Form
# ==========================
class AdminGenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "input"})}

# ==========================
# Admin Review Form
# ==========================
class AdminReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "input"}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "textarea"}),
        }

# ==========================
# Admin User Search
# ==========================
class AdminUserSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search username/email", "class": "input"})
    )

# ==========================
# Profile Avatar form
# ==========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={"accept": "image/*", "class": "input"}),
        }