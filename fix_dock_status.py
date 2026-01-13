#!/usr/bin/env python3
"""
机场状态数据保存逻辑修复脚本
问题: MQTT发送两种OSD消息,交替覆盖导致环境数据丢失
解决: 只更新非空字段,保留已有数据
"""

mqtt_fix_code = '''
    def save_dock_status(self, data, gateway_sn):
        """
        解析机场 OSD 数据并保存到数据库
        🔧 修复: 只更新非空字段,避免用空值覆盖已有数据
        """
        try:
            dock_data = data.get("data", {})

            # 🏭 获取机场显示名称
            dock_display_name = get_dock_display_name(gateway_sn)

            # 🔍 先尝试获取现有记录
            try:
                existing_dock = DockStatus.objects.get(dock_sn=gateway_sn)
            except DockStatus.DoesNotExist:
                existing_dock = None

            # 📦 构建更新字典 - 只包含非空值
            defaults_dict = {
                'is_online': True,
                'last_update_time': timezone.now(),
            }

            # 🏭 如果映射表中有名称,则更新 dock_name
            if dock_display_name:
                defaults_dict['dock_name'] = dock_display_name

            # 🌡️ 环境数据 - 只在有值时更新
            if 'environment_temperature' in dock_data and dock_data['environment_temperature'] is not None:
                defaults_dict['environment_temperature'] = dock_data['environment_temperature']
            if 'temperature' in dock_data and dock_data['temperature'] is not None:
                defaults_dict['temperature'] = dock_data['temperature']
            if 'humidity' in dock_data and dock_data['humidity'] is not None:
                defaults_dict['humidity'] = dock_data['humidity']
            if 'wind_speed' in dock_data and dock_data['wind_speed'] is not None:
                defaults_dict['wind_speed'] = dock_data['wind_speed']
            if 'rainfall' in dock_data and dock_data['rainfall'] is not None:
                defaults_dict['rainfall'] = dock_data['rainfall']

            # ⚡ 电源数据
            if 'electric_supply_voltage' in dock_data and dock_data['electric_supply_voltage'] is not None:
                defaults_dict['electric_supply_voltage'] = dock_data['electric_supply_voltage']
            if 'working_voltage' in dock_data and dock_data['working_voltage'] is not None:
                defaults_dict['working_voltage'] = dock_data['working_voltage']
            if 'working_current' in dock_data and dock_data['working_current'] is not None:
                defaults_dict['working_current'] = dock_data['working_current']

            # 🔋 备用电池信息
            backup_battery = dock_data.get('backup_battery', {})
            if isinstance(backup_battery, dict):
                if 'voltage' in backup_battery and backup_battery['voltage'] is not None:
                    defaults_dict['backup_battery_voltage'] = backup_battery['voltage']
                if 'temperature' in backup_battery and backup_battery['temperature'] is not None:
                    defaults_dict['backup_battery_temperature'] = backup_battery['temperature']
                if 'switch' in backup_battery and backup_battery['switch'] is not None:
                    defaults_dict['backup_battery_switch'] = backup_battery['switch']

            # 🔧 硬件状态
            if 'cover_state' in dock_data and dock_data['cover_state'] is not None:
                defaults_dict['cover_state'] = dock_data['cover_state']
            if 'supplement_light_state' in dock_data and dock_data['supplement_light_state'] is not None:
                defaults_dict['supplement_light_state'] = dock_data['supplement_light_state']
            if 'emergency_stop_state' in dock_data and dock_data['emergency_stop_state'] is not None:
                defaults_dict['emergency_stop_state'] = dock_data['emergency_stop_state']
            if 'putter_state' in dock_data and dock_data['putter_state'] is not None:
                defaults_dict['putter_state'] = dock_data['putter_state']

            # 📊 模式和告警
            if 'mode_code' in dock_data and dock_data['mode_code'] is not None:
                defaults_dict['mode_code'] = dock_data['mode_code']
            if 'alarm_state' in dock_data and dock_data['alarm_state'] is not None:
                defaults_dict['alarm_state'] = dock_data['alarm_state']

            # 💾 存储信息
            storage_data = dock_data.get('storage', {})
            if isinstance(storage_data, dict):
                total_info = storage_data.get('total')
                used_info = storage_data.get('used')
                if total_info is not None:
                    defaults_dict['storage_total'] = total_info
                if used_info is not None:
                    defaults_dict['storage_used'] = used_info

            # 📈 任务统计
            if 'job_number' in dock_data and dock_data['job_number'] is not None:
                defaults_dict['job_number'] = dock_data['job_number']
            if 'acc_time' in dock_data and dock_data['acc_time'] is not None:
                defaults_dict['acc_time'] = dock_data['acc_time']
            if 'activation_time' in dock_data and dock_data['activation_time'] is not None:
                defaults_dict['activation_time'] = dock_data['activation_time']

            # 🚁 无人机信息
            sub_device = dock_data.get('sub_device', {})
            if isinstance(sub_device, dict) and 'device_sn' in sub_device and sub_device['device_sn']:
                defaults_dict['drone_sn'] = sub_device['device_sn']

            if 'drone_in_dock' in dock_data and dock_data['drone_in_dock'] is not None:
                defaults_dict['drone_in_dock'] = dock_data['drone_in_dock']

            drone_charge_state_data = dock_data.get('drone_charge_state', {})
            if isinstance(drone_charge_state_data, dict):
                if 'state' in drone_charge_state_data and drone_charge_state_data['state'] is not None:
                    defaults_dict['drone_charge_state'] = drone_charge_state_data['state']
                if 'capacity_percent' in drone_charge_state_data and drone_charge_state_data['capacity_percent'] is not None:
                    capacity = drone_charge_state_data['capacity_percent']
                    # 过滤掉无效值 32767
                    if capacity != 32767:
                        defaults_dict['drone_battery_percent'] = capacity

            # 📡 网络状态
            network_state = dock_data.get('network_state', {})
            if isinstance(network_state, dict):
                if 'type' in network_state and network_state['type'] is not None:
                    defaults_dict['network_state_type'] = network_state['type']
                if 'quality' in network_state and network_state['quality'] is not None:
                    defaults_dict['network_quality'] = network_state['quality']
                if 'rate' in network_state and network_state['rate'] is not None:
                    defaults_dict['network_rate'] = network_state['rate']

            # 💾 保存原始数据以便调试
            defaults_dict['raw_osd_data'] = dock_data

            # 🔄 更新或创建记录
            _, created = DockStatus.objects.update_or_create(
                dock_sn=gateway_sn,
                defaults=defaults_dict
            )

            action = "新建" if created else "更新"
            print(f"{'✅' if created else '🔄'} {action}机场记录: {gateway_sn}")

        except Exception as e:
            import traceback
            print(f"❌ 保存机场状态失败: {e}")
            print(traceback.format_exc())
'''

print("=" * 80)
print("🔧 机场状态数据保存逻辑修复脚本")
print("=" * 80)
print()
print("📋 问题说明:")
print("  DJI机场每秒发送2种不同的OSD消息:")
print("  1️⃣  环境状态消息: 包含温度、湿度、风速等")
print("  2️⃣  电源状态消息: 包含电压、电流、任务统计等")
print()
print("  原逻辑会用第2种消息的空值覆盖第1种消息的环境数据")
print("  导致前端显示环境数据为空")
print()
print("🔧 修复方案:")
print("  改为只更新非空字段,保留已有数据不被覆盖")
print()
print("=" * 80)
print()
print("请将以下代码复制到远程服务器,替换 start_mqtt.py 中的 save_dock_status 方法")
print()
print(mqtt_fix_code)
