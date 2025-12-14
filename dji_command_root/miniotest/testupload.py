import boto3
from botocore.client import Config

# 配置 (和 settings.py 一致)
s3 = boto3.client(
    "s3",
    endpoint_url="http://127.0.0.1:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="StrongPassw0rd!",
    config=Config(signature_version="s3v4"),
)
BUCKET = "dji"

# ⭐ 关键：换个新名字，触发新任务
# 名字里带 "rail" 以匹配轨道检测配置
task_folder = "20251211_rail_list_protocol_test"

print(f"🚀 开始向 {task_folder} 上传模拟图片...")

# 上传 5 张图
# 根据 Mock 逻辑 (i % 3 == 0)，第 0 张和第 3 张会异常
for i in range(5):
    key = f"fh2/projects/{task_folder}/DJI_{i:03d}.jpg"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=b"fake_image_bytes",
        ContentType="image/jpeg"
    )
    print(f"   -> 上传: {key}")

print("✅ 上传完成！请观察 Django 控制台...")