from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.conf import settings

import boto3
from botocore.client import Config

from telemetry_app.models import InspectTask


class Command(BaseCommand):
    help = "删除 MinIO 中已过期的巡检任务媒体文件"

    def handle(self, *args, **options):
        now = datetime.now(timezone.utc)

        tasks = InspectTask.objects.filter(expire_at__lt=now, is_cleaned=False)
        if not tasks.exists():
            self.stdout.write(self.style.SUCCESS("没有需要清理的任务"))
            return

        s3 = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name=settings.MINIO_REGION,
            config=Config(signature_version="s3v4"),
        )

        for task in tasks:
            self.stdout.write(f"清理 InspectTask {task.id} ...")
            bucket = task.bucket
            for prefix in task.prefix_list:
                continuation_token = None
                while True:
                    kwargs = {
                        "Bucket": bucket,
                        "Prefix": prefix,
                        "MaxKeys": 1000,
                    }
                    if continuation_token:
                        kwargs["ContinuationToken"] = continuation_token

                    resp = s3.list_objects_v2(**kwargs)
                    contents = resp.get("Contents", [])
                    if not contents:
                        break

                    delete_params = {
                        "Bucket": bucket,
                        "Delete": {
                            "Objects": [{"Key": obj["Key"]} for obj in contents],
                            "Quiet": True,
                        },
                    }
                    s3.delete_objects(**delete_params)

                    if resp.get("IsTruncated"):
                        continuation_token = resp.get("NextContinuationToken")
                    else:
                        break

            task.is_cleaned = True
            task.save(update_fields=['is_cleaned'])
            self.stdout.write(self.style.SUCCESS(f"任务 {task.id} 清理完成"))