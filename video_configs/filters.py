import django_filters
from .models import VideoConfig

class VideoConfigFilter(django_filters.FilterSet):
    hls_status = django_filters.CharFilter(method='filter_hls_status')  # Кастомный фильтр для hls_videos.status

    class Meta:
        model = VideoConfig
        fields = ['hls_status']

    def filter_hls_status(self, queryset, name, value):
        return queryset.filter(video__hls_videos__status=value).distinct()