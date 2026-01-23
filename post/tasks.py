from celery import shared_task
from django.utils import timezone
from .models import Post


@shared_task
def publish_scheduled_posts():
    posts_to_publish = Post.objects.filter(
        is_posted=False,
        planned_post_time__lte=timezone.now()
    )

    count = posts_to_publish.update(is_posted=True)
    return f"Published {count} posts"
