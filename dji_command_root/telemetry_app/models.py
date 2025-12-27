from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ----------------------------------------------------------------------
# 1. 基础模型：航线、用户、配置
# ----------------------------------------------------------------------

class Wayline(models.Model):
    """
    航线表：存储无人机飞行航线信息
    """
    wayline_id = models.CharField(max_length=50, unique=True, verbose_name="航线ID")
    name = models.CharField(max_length=100, verbose_name="航线名称")
    description = models.TextField(blank=True, null=True, verbose_name="航线描述")

    waypoints = models.JSONField(blank=True, null=True, verbose_name="航点数据")
    length = models.FloatField(blank=True, null=True, verbose_name="航线长度(米)")
    estimated_duration = models.IntegerField(blank=True, null=True, verbose_name="预计飞行时间(秒)")

    # 这个字段可以保留作为参考，但实际自动逻辑将由 AlarmCategory 控制
    DETECT_TYPE_CHOICES = [
        ("rail", "轨道"),
        ("insulator", "绝缘子"),
        ("bridge", "桥梁"),
        ("catenary", "接触网"),
    ]
    detect_type = models.CharField(
        max_length=20,
        choices=DETECT_TYPE_CHOICES,
        default="rail",
        verbose_name="默认检测类型",
    )

    STATUS_CHOICES = [('DRAFT', '草稿'), ('ACTIVE', '激活'), ('ARCHIVED', '已归档')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT', verbose_name="航线状态")
    created_by = models.CharField(max_length=50, blank=True, null=True, verbose_name="创建人")
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
    告警类型表 (兼任：自动任务配置中心)

    【核心逻辑】：
    1. 根节点 (Parent=None): 代表 4 大检测种类 (轨道/绝缘子/接触网/桥梁)。
       - 需配置 'wayline' 和 'match_keyword'。
       - MinIO 轮询发现文件夹包含 'match_keyword' 时，自动创建任务并绑定到 'wayline'。
    2. 子节点 (Parent!=None): 代表具体的病害类型 (如: 断裂/异物)。
    """
    name = models.CharField(max_length=50, verbose_name="类型名称")

    # 传给算法的标识，例如: "RAIL", "INSULATOR", "BROKEN_LINE"
    code = models.CharField(max_length=50, unique=True, verbose_name="类型代码/算法标识")

    description = models.TextField(blank=True, null=True, verbose_name="描述")

    # ⭐ 新增字段 1: 绑定航线 (仅配置类根节点需要填)
    wayline = models.ForeignKey(
        'Wayline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bound_categories',
        verbose_name="绑定航线 (配置用)"
    )

    # ⭐ 新增字段 2: 文件夹匹配关键字
    # 例如填 "rail_line_north"，当 MinIO 文件夹包含此词时，自动应用此类型
    match_keyword = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="MinIO匹配关键字 (配置用)"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_categories',
        verbose_name="父类型"
    )

    class Meta:
        verbose_name = "告警类型/检测配置"
        verbose_name_plural = "告警类型/检测配置"
        unique_together = ('parent', 'name')

    def __str__(self):
        # 显示层级路径，例如: "接触网 -> 断线"
        path = [self.name]
        p = self.parent
        while p:
            path.insert(0, p.name)
            p = p.parent
        return f"{' -> '.join(path)} ({self.code})"


class Alarm(models.Model):
    """告警信息表 (业务结果)"""
    wayline = models.ForeignKey(Wayline, on_delete=models.SET_NULL, null=True, blank=True, related_name='alarms',
                                verbose_name="关联航线")
    category = models.ForeignKey(AlarmCategory, on_delete=models.PROTECT, verbose_name="告警类型", null=True,
                                 blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="经度")
    content = models.TextField(verbose_name="告警通用描述")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="告警图片链接")
    specific_data = models.JSONField(blank=True, null=True, verbose_name="特定详情(算法结果)")
    source_image = models.OneToOneField(
        "InspectImage",  # 注意引用 InspectImage 类
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alarm_detail',
        verbose_name="原始底图引用"
    )
    STATUS_CHOICES = [('PENDING', '待处理'), ('PROCESSING', '处理中'), ('COMPLETED', '已完成'), ('IGNORED', '已忽略')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="完成状况")
    handler = models.CharField(max_length=50, blank=True, null=True, verbose_name="处理人")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更改时间")

    class Meta:
        verbose_name = "告警信息"
        verbose_name_plural = "告警信息"
        ordering = ['-created_at']

    def __str__(self):
        return f"Alarm {self.id} - {self.category.name if self.category else '未知'}"


# ----------------------------------------------------------------------
# 2. 巡检任务与图片 (过程数据)
# ----------------------------------------------------------------------

class InspectTask(models.Model):
    """
    巡检任务：一次无人机飞行任务对应的一批图片
    """
    wayline = models.ForeignKey(Wayline, null=True, blank=True, on_delete=models.SET_NULL, related_name="inspect_tasks",
                                verbose_name="关联航线")

    # ⭐ 变更：检测类型改为关联 AlarmCategory
    detect_category = models.ForeignKey(
        AlarmCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="检测类型(配置)"
    )

    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,  # 如果删了父任务，子任务一起删
        null=True,
        blank=True,
        related_name='sub_tasks',  # 反向查询：parent.sub_tasks.all()
        verbose_name="所属父任务"
    )
    external_task_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="外部任务ID")
    bucket = models.CharField(max_length=100, default="dji", verbose_name="桶名称")
    prefix_list = models.JSONField(verbose_name="MinIO前缀列表")

    started_at = models.DateTimeField(null=True, blank=True, verbose_name="任务开始时间")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="任务结束时间")
    expire_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")

    DETECT_STATUS_CHOICES = [("pending", "待检测"), ("processing", "检测中"), ("done", "已完成"), ("failed", "失败")]
    detect_status = models.CharField(max_length=20, choices=DETECT_STATUS_CHOICES, default="pending",
                                     verbose_name="检测状态")
    is_cleaned = models.BooleanField(default=False, verbose_name="媒体是否已清理")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "巡检任务"
        verbose_name_plural = "巡检任务"

    def __str__(self):
        return f"Task {self.external_task_id}"


class InspectImage(models.Model):
    """巡检图片 (单张)"""
    inspect_task = models.ForeignKey(InspectTask, on_delete=models.CASCADE, related_name="images",
                                     verbose_name="所属巡检任务")
    wayline = models.ForeignKey(Wayline, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="关联航线")
    object_key = models.CharField(max_length=512, verbose_name="MinIO对象Key")

    DETECT_STATUS_CHOICES = [("pending", "待检测"), ("processing", "检测中"), ("done", "已完成"), ("failed", "失败")]
    detect_status = models.CharField(max_length=20, choices=DETECT_STATUS_CHOICES, default="pending",
                                     verbose_name="检测状态")
    result = models.JSONField(null=True, blank=True, verbose_name="检测结果")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "巡检图片"
        verbose_name_plural = "巡检图片"


# ----------------------------------------------------------------------
# 3. 辅助模型 (用户、组件配置、媒体库)
# ----------------------------------------------------------------------

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile', verbose_name='关联用户')
    name = models.CharField(max_length=100, verbose_name="真实姓名")
    role = models.CharField(max_length=20, default='user', verbose_name="角色")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ComponentConfig(models.Model):
    serverUrl = models.CharField(max_length=255, blank=True, null=True)
    wssUrl = models.CharField(max_length=255, blank=True, null=True)
    hostUrl = models.CharField(max_length=255, blank=True, null=True)
    prjId = models.CharField(max_length=255, blank=True, null=True)
    projectToken = models.CharField(max_length=255, blank=True, null=True)
    userId = models.CharField(max_length=255, blank=True, null=True)
    workspaceId = models.CharField(max_length=255, blank=True, null=True)
    fh2_project_id = models.CharField(max_length=255, blank=True, null=True)
    extra_params = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MediaFolderConfig(models.Model):
    folder_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WaylineImage(models.Model):
    # 简单的航线素材图片 (区别于 InspectImage)
    wayline = models.ForeignKey(Wayline, on_delete=models.CASCADE, related_name='images')
    alarm = models.ForeignKey(Alarm, on_delete=models.SET_NULL, null=True, blank=True, related_name='wayline_images')
    image_url = models.URLField(max_length=500)
    title = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    extra_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# models.py (添加到文件末尾)

class WaylineFingerprint(models.Model):
    """
    航线指纹表：存储已匹配航线的关键指纹信息
    只有匹配上关键字（如“轨道”、“桥梁”）的航线才会生成此记录
    """
    # 1. 关联航线 (一对一)
    wayline = models.OneToOneField(
        'Wayline',
        on_delete=models.CASCADE,
        related_name='fingerprint',
        verbose_name="关联航线"
    )

    # 2. 🔥 新增：绑定的检测类型
    # 存的是匹配成功的那个分类（比如：Name=轨道检测, Code=rail 的那个对象）
    detect_category = models.ForeignKey(
        'AlarmCategory',
        on_delete=models.SET_NULL,  # 如果分类被删了，指纹保留但类型变空
        null=True,
        blank=True,
        related_name='fingerprints',
        verbose_name="绑定的检测类型"
    )

    # 3. 指纹数据 (ActionUUID 列表)
    # 格式: ["270f6508-...", "5bd5b4c2-..."]
    action_uuids = models.JSONField(default=list, verbose_name="指纹UUID列表")

    # 4. 来源记录 (方便排查问题)
    source_url = models.CharField(max_length=1000, blank=True, null=True, verbose_name="KMZ下载链接")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        verbose_name = "航线指纹库"
        verbose_name_plural = "航线指纹库"

    def __str__(self):
        cat_name = self.detect_category.name if self.detect_category else "无类型"
        return f"[{cat_name}] {self.wayline.name} ({len(self.action_uuids)} IDs)"