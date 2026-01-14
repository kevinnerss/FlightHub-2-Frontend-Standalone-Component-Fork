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
        ("rail", "铁路"),
        ("contactline", "接触网"),
        ("bridge", "桥梁"),
        ("protected_area", "保护区"),
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
        ordering = ['parent__id', 'name']  # 🔥 添加默认排序，避免分页警告

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
    # 高度信息（从算法返回的 GPS 信息中提取）
    high = models.FloatField(null=True, blank=True, verbose_name="高度（米）")

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
    # 🔥 [新增] 司空任务关联字段
    dji_task_uuid = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="司空任务UUID")
    dji_task_name = models.CharField(max_length=200, null=True, blank=True, verbose_name="司空任务名称")
    dji_status = models.CharField(max_length=50, default="unknown", verbose_name="司空状态")
    
    # 🔥 [新增] 设备与航线关联 (用于多机多任务区分)
    device_sn = models.CharField(max_length=100, null=True, blank=True, verbose_name="执行设备SN")
    # wayline_id 已经作为外键存在 (wayline 字段)，无需重复定义

    # 🔥 [新增] 用于“防抖动”判断
    last_image_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name="最后一张图接收时间")
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

    # 4. 🔥 新增：详细动作信息 (包含经纬度、高度、Yaw)
    # 格式: [{"uuid": "...", "lat": 12.3, "lon": 11.1, "height": 100, "gimbal_yaw": 90}, ...]
    action_details = models.JSONField(default=list, blank=True, null=True, verbose_name="动作详情")

    # 5. 来源记录 (方便排查问题)
    source_url = models.CharField(max_length=1000, blank=True, null=True, verbose_name="KMZ下载链接")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    class Meta:
        verbose_name = "航线指纹库"
        verbose_name_plural = "航线指纹库"

    def __str__(self):
        cat_name = self.detect_category.name if self.detect_category else "无类型"
        return f"[{cat_name}] {self.wayline.name} ({len(self.action_uuids)} IDs)"


class DronePosition(models.Model):
    """
    无人机位置信息表：存储无人机实时位置数据
    用于分析无人机飞行轨迹和状态
    """
    # 设备标识
    device_sn = models.CharField(max_length=100, verbose_name="设备序列号", db_index=True)
    device_model = models.CharField(max_length=100, blank=True, null=True, verbose_name="设备型号")
    
    # 位置信息（核心数据）
    latitude = models.DecimalField(max_digits=11, decimal_places=8, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, verbose_name="经度")
    altitude = models.FloatField(verbose_name="海拔高度(米)")
    relative_height = models.FloatField(null=True, blank=True, verbose_name="相对起飞点高度(米)")
    
    # 飞行状态
    heading = models.FloatField(null=True, blank=True, verbose_name="航向角(度)")
    speed_horizontal = models.FloatField(null=True, blank=True, verbose_name="水平速度(m/s)")
    speed_vertical = models.FloatField(null=True, blank=True, verbose_name="垂直速度(m/s)")
    
    # 电池和信号
    battery_percent = models.IntegerField(null=True, blank=True, verbose_name="电池电量(%)")
    signal_quality = models.IntegerField(null=True, blank=True, verbose_name="信号质量")
    
    # 原始数据（保存完整JSON便于后续分析）
    raw_data = models.JSONField(blank=True, null=True, verbose_name="原始MQTT数据")
    
    # MQTT 元信息
    mqtt_topic = models.CharField(max_length=500, blank=True, null=True, verbose_name="MQTT主题")
    
    # 时间戳
    timestamp = models.DateTimeField(verbose_name="数据时间戳", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="记录创建时间")
    
    class Meta:
        verbose_name = "无人机位置记录"
        verbose_name_plural = "无人机位置记录"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device_sn', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device_sn} - {self.timestamp} - ({self.latitude}, {self.longitude}, {self.altitude}m)"


class FlightTaskInfo(models.Model):
    """
    飞行任务记录表：记录通过 /openapi/v0.1/flight-task 接口创建的任务
    task_uuid 对应 media 下的一级文件夹名
    """
    task_uuid = models.CharField(max_length=100, unique=True, verbose_name="任务UUID")
    name = models.CharField(max_length=200, verbose_name="任务名称")
    sn = models.CharField(max_length=100, blank=True, null=True, verbose_name="设备SN")
    wayline_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="航线ID")
    
    # 存储创建任务时的完整参数，方便回溯
    params = models.JSONField(blank=True, null=True, verbose_name="任务参数")
    
    # 状态字段，可以记录任务的执行状态
    status = models.CharField(max_length=50, default="created", verbose_name="任务状态")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "飞行任务记录"
        verbose_name_plural = "飞行任务记录"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.task_uuid})"


class DockStatus(models.Model):
    """
    机场状态表：存储机场实时状态信息
    根据MQTT消息动态更新
    """
    # 机场标识
    dock_sn = models.CharField(max_length=100, unique=True, verbose_name="机场序列号", db_index=True)
    dock_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="机场名称")

    # 位置信息
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="纬度")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="经度")
    height = models.FloatField(null=True, blank=True, verbose_name="海拔高度(米)")

    # 环境状态
    environment_temperature = models.FloatField(null=True, blank=True, verbose_name="环境温度(℃)")
    temperature = models.FloatField(null=True, blank=True, verbose_name="机场内部温度(℃)")
    humidity = models.IntegerField(null=True, blank=True, verbose_name="湿度(%)")
    wind_speed = models.FloatField(null=True, blank=True, verbose_name="风速(m/s)")
    rainfall = models.FloatField(null=True, blank=True, verbose_name="降雨量")

    # 机场硬件状态
    mode_code = models.IntegerField(null=True, blank=True, verbose_name="模式代码")
    cover_state = models.IntegerField(null=True, blank=True, verbose_name="舱盖状态(0-关闭/1-打开)")
    putter_state = models.IntegerField(null=True, blank=True, verbose_name="推杆状态")
    supplement_light_state = models.IntegerField(null=True, blank=True, verbose_name="补光灯状态")
    emergency_stop_state = models.IntegerField(null=True, blank=True, verbose_name="急停状态")

    # 电源信息
    electric_supply_voltage = models.IntegerField(null=True, blank=True, verbose_name="供电电压(V)")
    working_voltage = models.IntegerField(null=True, blank=True, verbose_name="工作电压(mV)")
    working_current = models.IntegerField(null=True, blank=True, verbose_name="工作电流(mA)")

    # 备用电池
    backup_battery_voltage = models.IntegerField(null=True, blank=True, verbose_name="备用电池电压(mV)")
    backup_battery_temperature = models.FloatField(null=True, blank=True, verbose_name="备用电池温度(℃)")
    backup_battery_switch = models.IntegerField(null=True, blank=True, verbose_name="备用电池开关")

    # 无人机状态
    drone_in_dock = models.IntegerField(null=True, blank=True, verbose_name="无人机在舱内(0-否/1-是)")
    drone_charge_state = models.IntegerField(null=True, blank=True, verbose_name="无人机充电状态")
    drone_battery_percent = models.IntegerField(null=True, blank=True, verbose_name="无人机电量(%)")
    drone_sn = models.CharField(max_length=100, blank=True, null=True, verbose_name="机场内无人机SN")
    airport_push = models.CharField(max_length=500, blank=True, null=True, verbose_name="机场推流地址")
    drone_push = models.CharField(max_length=500, blank=True, null=True, verbose_name="无人机推流地址")

    # 网络状态
    network_state_type = models.IntegerField(null=True, blank=True, verbose_name="网络类型")
    network_quality = models.IntegerField(null=True, blank=True, verbose_name="网络质量")
    network_rate = models.IntegerField(null=True, blank=True, verbose_name="网络速率")

    # 存储信息
    storage_total = models.BigIntegerField(null=True, blank=True, verbose_name="总存储空间(KB)")
    storage_used = models.BigIntegerField(null=True, blank=True, verbose_name="已用存储空间(KB)")

    # 任务统计
    job_number = models.IntegerField(null=True, blank=True, verbose_name="任务次数")
    acc_time = models.BigIntegerField(null=True, blank=True, verbose_name="累计工作时长(秒)")
    activation_time = models.BigIntegerField(null=True, blank=True, verbose_name="激活时间戳")

    # 状态信息
    alarm_state = models.IntegerField(null=True, blank=True, verbose_name="告警状态")
    is_online = models.BooleanField(default=False, verbose_name="在线状态")

    # 原始数据
    raw_osd_data = models.JSONField(blank=True, null=True, verbose_name="原始OSD数据")

    # 时间戳
    last_update_time = models.DateTimeField(null=True, blank=True, verbose_name="最后更新时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="记录更新时间")

    class Meta:
        verbose_name = "机场状态"
        verbose_name_plural = "机场状态"
        ordering = ['-last_update_time']

    def __str__(self):
        return f"{self.dock_name or self.dock_sn} - {'在线' if self.is_online else '离线'}"
