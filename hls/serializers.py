from rest_framework import serializers
from .models import HLSVideo



class HLSVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HLSVideo
        fields = ['uuid', 'video', 'status', 'url', 'width', 'height']
        read_only_fields = ['uuid', ]