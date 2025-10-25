from django.db import models


class AlarmType(models.Model):
    """告警类型表"""
    name = models.CharField(max_length=50, unique=True, verbose_name="类型名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="类型代码")
    description = models.TextField(blank=True, null=True, verbose_name="描述")

    class Meta:
        verbose_name = "告警类型"
        verbose_name_plural = "告警类型"

    def __str__(self):
        return self.name


class Alarm(models.Model):
    """告警信息表"""

    # 关联字段
    type = models.ForeignKey(AlarmType, on_delete=models.CASCADE, verbose_name="告警类型")

    # 位置信息
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="经度")

    # 告警详情
    content = models.TextField(verbose_name="告警详情")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="告警图片链接")

    # 状态和时间
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('PROCESSING', '处理中'),
        ('COMPLETED', '已完成'),
        ('IGNORED', '已忽略'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="完成状况"
    )
    handler = models.CharField(max_length=50, blank=True, null=True, verbose_name="处理人")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更改时间")

    class Meta:
        verbose_name = "告警信息"
        verbose_name_plural = "告警信息"
        ordering = ['-created_at']  # 默认按创建时间倒序排列

    def __str__(self):
        return f"Alarm {self.id} - {self.type.name}"