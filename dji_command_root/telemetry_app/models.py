from django.db import models
from django.contrib.auth.models import AbstractUser


class Wayline(models.Model):
    """
    航线表
    存储无人机飞行航线信息
    """
    wayline_id = models.CharField(max_length=50, unique=True, verbose_name="航线ID")
    name = models.CharField(max_length=100, verbose_name="航线名称")
    description = models.TextField(blank=True, null=True, verbose_name="航线描述")
    
    # 航线数据
    waypoints = models.JSONField(blank=True, null=True, verbose_name="航点数据")  # 存储航点坐标等信息
    length = models.FloatField(blank=True, null=True, verbose_name="航线长度(米)")
    estimated_duration = models.IntegerField(blank=True, null=True, verbose_name="预计飞行时间(秒)")
    
    # 状态信息
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('ACTIVE', '激活'),
        ('ARCHIVED', '已归档'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="航线状态"
    )
    
    # 创建者信息
    created_by = models.CharField(max_length=50, blank=True, null=True, verbose_name="创建人")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "航线信息"
        verbose_name_plural = "航线信息"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"航线 {self.wayline_id} - {self.name}"


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

    # 航线ID字段 - 改为外键关联
    wayline = models.ForeignKey(
        Wayline,
        on_delete=models.SET_NULL,  # 当航线被删除时，将告警的航线引用设为NULL
        null=True,
        blank=True,
        related_name='alarms',  # 允许从航线查询关联的所有告警
        verbose_name="关联航线"
    )

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


class WaylineImage(models.Model):
    """
    航线图片表
    存储每条航线的图片素材（可来源于告警或手动上传）
    """
    wayline = models.ForeignKey(
        Wayline,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="关联航线"
    )
    alarm = models.ForeignKey(
        'Alarm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wayline_images',
        verbose_name="关联告警"
    )
    image_url = models.URLField(max_length=500, verbose_name="图片链接")
    title = models.CharField(max_length=120, blank=True, null=True, verbose_name="标题")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    extra_data = models.JSONField(blank=True, null=True, verbose_name="扩展信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "航线图片"
        verbose_name_plural = "航线图片"
        ordering = ['-created_at']

    def __str__(self):
        return f"航线图片 {self.id} - {self.wayline.name if self.wayline else '未知航线'}"


class UserProfile(models.Model):
    """用户扩展信息表"""
    user = models.OneToOneField(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='profile', 
        verbose_name='关联用户'
    )
    name = models.CharField(max_length=100, verbose_name="真实姓名")
    role = models.CharField(max_length=20, default='user', verbose_name="角色")  # admin/user
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"用户 {self.user.username} - {self.name}"


class ComponentConfig(models.Model):
    """
    存储大疆二开组件公共参数（对应官方 demo）
    """
    serverUrl = models.CharField(max_length=255, blank=True, null=True, verbose_name="服务器地址")
    wssUrl = models.CharField(max_length=255, blank=True, null=True, verbose_name="WSS 地址")
    hostUrl = models.CharField(max_length=255, blank=True, null=True, verbose_name="Host 地址")
    prjId = models.CharField(max_length=255, blank=True, null=True, verbose_name="项目ID")
    projectToken = models.CharField(max_length=255, blank=True, null=True, verbose_name="组织密钥")
    userId = models.CharField(max_length=255, blank=True, null=True, verbose_name="用户ID")
    workspaceId = models.CharField(max_length=255, blank=True, null=True, verbose_name="工作区/组织ID")
    fh2_project_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="兼容字段-项目ID")
    extra_params = models.JSONField(blank=True, null=True, verbose_name="附加参数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "组件公共参数"
        verbose_name_plural = "组件公共参数"

    def __str__(self):
        return f"组件配置 {self.id}"


class MediaFolderConfig(models.Model):
    """
    Stores the path of the media folder used for serving images and videos.
    """
    folder_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="媒体文件夹路径")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "媒体文件夹配置"
        verbose_name_plural = "媒体文件夹配置"

    def __str__(self):
        return f"媒体文件夹配置 {self.id or ''}"
