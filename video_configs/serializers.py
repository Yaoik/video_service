from rest_framework import serializers
from uploads.serializers import VideoSerializer
from .models import VideoConfig

class VideoConfigSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VideoConfig
        fields = ['uuid', 'title', 'user', 'created_at', 'updated_at', 'video']
        read_only_fields = ['uuid', 'user', 'created_at', 'updated_at']

    def create(self, validated_data:dict):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)