from rest_framework import serializers
from .models import Title
from uploads.serializers import VideoSerializer

class TitleSerializer(serializers.ModelSerializer):
    episodes = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = (
            'shikimori_id',
            'title',
            'year',
            'description',
            'episodes',
        )
        read_only_fields = fields