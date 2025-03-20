from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'uuid', 'user', 'video', 'name', 'video_size', 'video_duration', 'hls_playlist', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uuid', 'user', 'video_size', 'video_duration', 'hls_playlist', 'status', 'created_at', 'updated_at']
