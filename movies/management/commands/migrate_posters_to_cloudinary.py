from django.core.management.base import BaseCommand
from movies.models import Movie
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = "Migrate existing movie posters to Cloudinary"

    def handle(self, *args, **kwargs):
        for movie in Movie.objects.all():
            poster_path = str(movie.poster)
            if poster_path and not poster_path.startswith("http"):
                local_path = os.path.join("media", poster_path)
                if os.path.exists(local_path):
                    self.stdout.write(f"Uploading {local_path}...")
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="webzmovies/posters/",
                        overwrite=True
                    )
                    movie.poster = result["secure_url"]
                    movie.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"✔ Uploaded {movie.title} to Cloudinary"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"⚠ File not found: {local_path}"
                    ))
