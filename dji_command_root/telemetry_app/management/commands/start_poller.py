# telemetry_app/management/commands/start_poller.py
from django.core.management.base import BaseCommand
from telemetry_app.views import minio_poller_worker2  # 引入最终适配版逻辑


class Command(BaseCommand):
    help = '启动 MinIO 自动扫描服务'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🕵️ [Poller] 独立扫描进程启动中...'))

        # 使用支持指纹识别和三级树结构的 worker
        minio_poller_worker2()