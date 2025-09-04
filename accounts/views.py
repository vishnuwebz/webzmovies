from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Optional: handle newsletter checkbox
            if form.cleaned_data.get("newsletter"):
                # Save newsletter subscription logic
                pass

            login(request, user)
            return redirect("profile")  # redirect after signup
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})
