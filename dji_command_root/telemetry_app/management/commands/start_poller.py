# telemetry_app/management/commands/start_poller.py
from django.core.management.base import BaseCommand
from telemetry_app.views import minio_poller_worker  # 引入你写好的逻辑


class Command(BaseCommand):
    help = '启动 MinIO 自动扫描服务'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🕵️ [Poller] 独立扫描进程启动中...'))

        # 直接调用你的死循环函数
        # 注意：这里不需要 threading，因为这个进程就是专门干这件事的
        minio_poller_worker()