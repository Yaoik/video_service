from rest_framework import serializers
from .models import HLSVideo



class HLSVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HLSVideo
        fields = ['uuid', 'video', 'status', 'url']
        read_only_fields = ['uuid', ]