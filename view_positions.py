#!/usr/bin/env python3
"""
无人机位置数据查看工具
快速查看最新记录的无人机位置信息
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/Users/yaoduanyang/Desktop/FlightHub-2-Frontend-Standalone-Component/dji_command_root')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dji_command_root.settings')
django.setup()

from telemetry_app.models import DronePosition
from django.db.models import Count, Avg, Max, Min
from datetime import datetime

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def show_latest_positions():
    """显示每台设备的最新位置"""
    print_header("最新位置信息")
    
    # 获取所有设备的最新时间戳
    latest_timestamps = DronePosition.objects.values('device_sn').annotate(
        latest_time=Max('timestamp')
    )
    
    if not latest_timestamps:
        print("暂无位置记录")
        return
    
    for item in latest_timestamps:
        position = DronePosition.objects.filter(
            device_sn=item['device_sn'],
            timestamp=item['latest_time']
        ).first()
        
        if position:
            print(f"\n设备: {position.device_sn}")
            if position.device_model:
                print(f"  型号: {position.device_model}")
            print(f"  位置: ({position.latitude}, {position.longitude})")
            print(f"  高度: {position.altitude}m", end="")
            if position.relative_height:
                print(f" (相对: {position.relative_height}m)", end="")
            print()
            
            if position.battery_percent:
                print(f"  电量: {position.battery_percent}%")
            if position.heading is not None:
                print(f"  航向: {position.heading}°")
            
            print(f"  时间: {position.timestamp}")

def show_statistics():
    """显示统计信息"""
    print_header("统计信息")
    
    total_records = DronePosition.objects.count()
    total_devices = DronePosition.objects.values('device_sn').distinct().count()
    
    print(f"\n总记录数: {total_records}")
    print(f"设备数量: {total_devices}")
    
    if total_records > 0:
        # 按设备统计
        device_stats = DronePosition.objects.values('device_sn', 'device_model').annotate(
            record_count=Count('id'),
            avg_altitude=Avg('altitude'),
            max_altitude=Max('altitude'),
            min_altitude=Min('altitude'),
            latest_time=Max('timestamp'),
            earliest_time=Min('timestamp')
        ).order_by('-record_count')
        
        print("\n设备详情:")
        for stat in device_stats:
            print(f"\n  设备: {stat['device_sn']}")
            if stat['device_model']:
                print(f"    型号: {stat['device_model']}")
            print(f"    记录数: {stat['record_count']}")
            print(f"    平均高度: {stat['avg_altitude']:.1f}m")
            print(f"    最大高度: {stat['max_altitude']:.1f}m")
            print(f"    最小高度: {stat['min_altitude']:.1f}m")
            print(f"    首次记录: {stat['earliest_time']}")
            print(f"    最新记录: {stat['latest_time']}")

def show_recent_records(limit=10):
    """显示最近的记录"""
    print_header(f"最近 {limit} 条记录")
    
    records = DronePosition.objects.order_by('-timestamp')[:limit]
    
    if not records:
        print("暂无记录")
        return
    
    print(f"\n{'时间':<20} {'设备':<15} {'经度':<12} {'纬度':<12} {'高度(m)':<10} {'电量%':<8}")
    print("-" * 90)
    
    for r in records:
        timestamp = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        device = r.device_sn[:12] + '...' if len(r.device_sn) > 12 else r.device_sn
        battery = f"{r.battery_percent}" if r.battery_percent else "N/A"
        
        print(f"{timestamp:<20} {device:<15} {r.longitude:<12.6f} {r.latitude:<12.6f} "
              f"{r.altitude:<10.1f} {battery:<8}")

def show_track(device_sn):
    """显示指定设备的轨迹"""
    print_header(f"设备轨迹: {device_sn}")
    
    positions = DronePosition.objects.filter(
        device_sn__icontains=device_sn
    ).order_by('timestamp')
    
    if not positions:
        print(f"未找到设备 {device_sn} 的记录")
        return
    
    print(f"\n找到 {positions.count()} 条记录\n")
    print(f"{'时间':<20} {'经度':<12} {'纬度':<12} {'高度(m)':<10} {'速度(m/s)':<12}")
    print("-" * 70)
    
    for p in positions:
        timestamp = p.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        speed = f"{p.speed_horizontal:.1f}" if p.speed_horizontal else "N/A"
        
        print(f"{timestamp:<20} {p.longitude:<12.6f} {p.latitude:<12.6f} "
              f"{p.altitude:<10.1f} {speed:<12}")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'latest':
            show_latest_positions()
        elif command == 'stats':
            show_statistics()
        elif command == 'recent':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_recent_records(limit)
        elif command == 'track':
            if len(sys.argv) < 3:
                print("错误: 请提供设备序列号")
                print("用法: python3 view_positions.py track <device_sn>")
                return
            show_track(sys.argv[2])
        elif command == 'all':
            show_statistics()
            show_latest_positions()
            show_recent_records(5)
        else:
            print(f"未知命令: {command}")
            print_usage()
    else:
        # 默认显示最新位置
        show_latest_positions()

def print_usage():
    """打印使用说明"""
    print("\n使用方法:")
    print("  python3 view_positions.py [command] [options]")
    print("\n命令:")
    print("  latest          - 显示每台设备的最新位置（默认）")
    print("  stats           - 显示统计信息")
    print("  recent [N]      - 显示最近 N 条记录（默认10）")
    print("  track <sn>      - 显示指定设备的飞行轨迹")
    print("  all             - 显示所有信息")
    print("\n示例:")
    print("  python3 view_positions.py latest")
    print("  python3 view_positions.py recent 20")
    print("  python3 view_positions.py track ABC123")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
