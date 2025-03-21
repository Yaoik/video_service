from rest_framework import serializers
from .models import Video
from hls.serializers import HLSVideoSerializer

class VideoSerializer(serializers.ModelSerializer):
    hls_videos = HLSVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = (
            'video_file',
            
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
            'hls_videos',
        )
        read_only_fields = (
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