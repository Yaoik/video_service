import django_filters
from django.db.models import Q
from .models import Video
from django.db.models import QuerySet

class VideoFilter(django_filters.FilterSet):
    metadata = django_filters.CharFilter(method='filter_metadata')

    class Meta:
        model = Video
        fields = []
    
    def filter_metadata(self, queryset:QuerySet[Video], name:str, value:str):
        # value приходит в формате "key:value"
        if ':' in value:
            key, val = value.split(':', 1)
            return queryset.filter(**{f'metadata__{key}': val})
        return queryset.filter(metadata__icontains=value)