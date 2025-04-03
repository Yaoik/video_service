from rest_framework import serializers
from .models import Video
from hls.serializers import HLSVideoSerializer
from users.serializer import UserSerializer
from rest_framework.request import Request



class VideoSerializer(serializers.ModelSerializer):
    hls_video = HLSVideoSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    video_filename = serializers.CharField(write_only=True)
    
    class Meta:
        model = Video
        fields = (
            'user',
            'video_file',
            'moderated',
            'video_filename',
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
            'video_file',
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
    
    def create(self, validated_data:dict):
        request:Request = self.context.get('request', None)
        video_filename = validated_data.pop('video_filename')
        metadata:dict = validated_data.pop('metadata', {})
        upload_size = validated_data.pop('size', None)
        
        video = Video(
            user=request.user,
            **validated_data
        )
        
        video.video_file.name = video_filename
        
        video.moderated = False
        
        if upload_size is not None:
            video.size = upload_size
        
        video.save()
        
        return video