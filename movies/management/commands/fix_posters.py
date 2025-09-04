from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Fix Movie.poster paths so they point correctly to Cloudinary"

    def handle(self, *args, **options):
        fixed_count = 0
        for movie in Movie.objects.all():
            if movie.poster:
                poster_str = str(movie.poster)

                # Case 1: Already Cloudinary but stored with dwt5oh4jd/ prefix
                if poster_str.startswith("dwt5oh4jd/"):
                    cleaned = poster_str.split("posters/", 1)[-1]
                    movie.poster.name = f"posters/{cleaned}"
                    movie.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Fixed (prefix): {movie.title} -> {movie.poster.name}"
                        )
                    )
                    fixed_count += 1

                # Case 2: Stored with /media/ prefix
                elif poster_str.startswith("media/"):
                    cleaned = poster_str.split("media/", 1)[-1]
                    movie.poster.name = cleaned
                    movie.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Fixed (media path): {movie.title} -> {movie.poster.name}"
                        )
                    )
                    fixed_count += 1

        if fixed_count == 0:
            self.stdout.write(self.style.WARNING("⚠️ No poster paths needed fixing"))
        else:
            self.stdout.write(self.style.SUCCESS(f"🎉 Fixed {fixed_count} poster(s)!"))
