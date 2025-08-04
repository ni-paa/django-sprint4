from django.db.models import Count, QuerySet
from django.utils import timezone


class PostQuerySet(QuerySet):
    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date')

    def with_related(self):
        return self.select_related(
            'category', 'location', 'author'
        )

    def annotate_comments(self):
        return self.annotate(
            comment_count=Count('comments')
        )
