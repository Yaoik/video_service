from rest_framework import serializers
from .models import Video
from hls.serializers import HLSVideoSerializer
from titles.models import Title
from users.serializer import UserSerializer



class VideoSerializer(serializers.ModelSerializer):
    hls_video = HLSVideoSerializer(many=False, read_only=True)
    title = serializers.SlugRelatedField(
            slug_field='shikimori_id',
            queryset=Title.objects.all(),
            required=False,
            allow_null=True,
        )
    user = UserSerializer(many=False, read_only=True)
    
    class Meta:
        model = Video
        fields = (
            'title',
            'user',
            'video_file',
            'moderated',
            
            'episode_number',
            'metadata',
            
            'size', 
            'duration', 
            'width', 
            'height', 
            'bitrate', 
            'frame_rate', 
            'codec', 
            'frame_count', 
            'audio_codec', 
            'sample_rate', 
            'channels', 
            'audio_bitrate', 
            'hls_video',
        )
        read_only_fields = (
            'moderated',
            'size', 
            'duration', 
            'width', 
            'height', 
            'bitrate', 
            'frame_rate', 
            'codec', 
            'frame_count', 
            'audio_codec', 
            'sample_rate', 
            'channels', 
            'audio_bitrate', 
        )