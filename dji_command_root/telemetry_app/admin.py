from django.contrib import admin
from .models import (
    Wayline, AlarmCategory, Alarm, InspectTask, InspectImage,
    UserProfile, ComponentConfig, MediaFolderConfig, WaylineImage,
    WaylineFingerprint, DronePosition
)


@admin.register(DronePosition)
class DronePositionAdmin(admin.ModelAdmin):
    """无人机位置信息管理"""
    list_display = [
        'device_sn', 'device_model', 'timestamp', 
        'latitude', 'longitude', 'altitude', 
        'battery_percent', 'created_at'
    ]
    list_filter = ['device_sn', 'device_model', 'timestamp']
    search_fields = ['device_sn', 'device_model', 'mqtt_topic']
    ordering = ['-timestamp']
    readonly_fields = ['created_at', 'raw_data']
    
    fieldsets = (
        ('设备信息', {
            'fields': ('device_sn', 'device_model')
        }),
        ('位置信息', {
            'fields': ('latitude', 'longitude', 'altitude', 'relative_height')
        }),
        ('飞行状态', {
            'fields': ('heading', 'speed_horizontal', 'speed_vertical')
        }),
        ('设备状态', {
            'fields': ('battery_percent', 'signal_quality')
        }),
        ('元数据', {
            'fields': ('mqtt_topic', 'timestamp', 'created_at', 'raw_data'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """禁止手动添加（只能由系统自动记录）"""
        return False


# 可选：注册其他模型到后台
@admin.register(Wayline)
class WaylineAdmin(admin.ModelAdmin):
    list_display = ['wayline_id', 'name', 'status', 'detect_type', 'created_at']
    list_filter = ['status', 'detect_type']
    search_fields = ['wayline_id', 'name']


@admin.register(AlarmCategory)
class AlarmCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'wayline', 'match_keyword']
    list_filter = ['parent']
    search_fields = ['name', 'code']


@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'wayline', 'latitude', 'longitude', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['content']


@admin.register(InspectTask)
class InspectTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'external_task_id', 'wayline', 'detect_status', 'created_at']
    list_filter = ['detect_status', 'is_cleaned']
    search_fields = ['external_task_id']


@admin.register(InspectImage)
class InspectImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'inspect_task', 'wayline', 'detect_status', 'created_at']
    list_filter = ['detect_status']
    search_fields = ['object_key']
