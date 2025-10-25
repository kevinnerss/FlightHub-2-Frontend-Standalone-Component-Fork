from rest_framework import serializers
from .models import Alarm, AlarmType

class AlarmTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlarmType
        fields = '__all__'

class AlarmSerializer(serializers.ModelSerializer):
    # 使用 StringRelatedField 显示类型名称，而不是 ID
    type_name = serializers.CharField(source='type.name', read_only=True)

    class Meta:
        model = Alarm
        fields = [
            'id', 'type', 'type_name', 'latitude', 'longitude',
            'content', 'image_url', 'status', 'handler',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']