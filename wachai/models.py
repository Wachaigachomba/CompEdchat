from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from PIL import Image


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            # Define the max dimensions for the image (adjust as needed)
            max_size = (1, 1)
            # Resize only if the image is larger than the max size
            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(self.image.path)


class Reply(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(
        upload_to='reply_images/', blank=True, null=True)  # New field
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Reply by {self.author} on {self.post.title}'

    def get_absolute_url(self):
        # Redirect to the post's detail view after creating a reply
        return self.post.get_absolute_url()
