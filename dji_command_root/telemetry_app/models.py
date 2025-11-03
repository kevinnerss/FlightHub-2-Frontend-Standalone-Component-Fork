from django.db import models


class AlarmCategory(models.Model):
    """
    告警类型表 (层级结构)
    使用 'parent' 字段实现无限层级分类
    """
    name = models.CharField(max_length=50, verbose_name="类型名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="类型代码")
    description = models.TextField(blank=True, null=True, verbose_name="描述")

    # 关键字段：父类型
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_categories',
        verbose_name="父类型"
    )

    class Meta:
        verbose_name = "告警类型"
        verbose_name_plural = "告警类型"
        # 确保同一父类型下的名称是唯一的
        unique_together = ('parent', 'name')

    def __str__(self):
        # 显示层级路径，例如: "接触网 -> 断线"
        path = [self.name]
        p = self.parent
        while p:
            path.insert(0, p.name)
            p = p.parent
        return ' -> '.join(path)


class Alarm(models.Model):
    """告警信息表"""

    # 关联字段
    # 1. 字段名从 'type' 改为 'category' (避免 'type' 成为 Python 关键字)
    # 2. on_delete 改为 PROTECT，防止删除一个类型时，其下的所有告警信息也丢失
    category = models.ForeignKey(
        AlarmCategory,
        on_delete=models.PROTECT,
        verbose_name="告警类型",
        null=True,  # 允许数据库中的值为 NULL
        blank=True  # 允许在 Django Admin 或表单中该字段为空
    )

    # 位置信息
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="经度")

    # 告警详情
    content = models.TextField(verbose_name="告警通用描述")  # 通用描述
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="告警图片链接")

    # 关键字段：存储特定类型的额外数据
    # 例如: {"pole_number": "T1001", "voltage": "25kV"}
    # 或:   {"track_id": "G10-S2", "mileage": "K100+200"}
    specific_data = models.JSONField(blank=True, null=True, verbose_name="特定详情")

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
        ordering = ['-created_at']

    def __str__(self):
        return f"Alarm {self.id} - {self.category.name}"