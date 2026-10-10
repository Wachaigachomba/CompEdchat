from django.core.management.base import BaseCommand
from wachai.models import Post

class Command(BaseCommand):
    help = 'Deletes posts whose authors no longer exist'

    def handle(self, *args, **kwargs):
        orphaned_posts = Post.objects.filter(author__isnull=True)
        count = orphaned_posts.count()
        orphaned_posts.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned posts."))