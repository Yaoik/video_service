import django_filters
from django.db.models import Q
from .models import Title
from django.db.models import QuerySet

class TitleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    year = django_filters.NumberFilter()
    shikimori_id = django_filters.NumberFilter()
    
    class Meta:
        model = Title
        fields = ['shikimori_id', 'year']

    def filter_search(self, queryset:QuerySet[Title], name:str, value:str):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )