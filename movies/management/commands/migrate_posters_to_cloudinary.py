# movies/management/commands/migrate_posters_to_cloudinary.py

from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = "Migrate all existing movie posters from local media to Cloudinary"

    def handle(self, *args, **options):
        # Loop through movies
        for movie in Movie.objects.all():
            if movie.poster and not str(movie.poster.url).startswith("http"):
                local_path = movie.poster.path  # path on disk (media/posters/...)

                if os.path.exists(local_path):
                    self.stdout.write(self.style.NOTICE(f"Uploading {local_path}..."))

                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        local_path,
                        folder="webzmovies/posters",  # ✅ keeps your posters organized
                        public_id=f"movie_{movie.id}",  # unique id per movie
                        overwrite=True
                    )

                    # Update the model with new Cloudinary URL
                    movie.poster = result["secure_url"]
                    movie.save(update_fields=["poster"])

                    self.stdout.write(self.style.SUCCESS(f"✅ Uploaded: {movie.title}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ File not found: {local_path}"))

        self.stdout.write(self.style.SUCCESS("🎉 Migration complete!"))
