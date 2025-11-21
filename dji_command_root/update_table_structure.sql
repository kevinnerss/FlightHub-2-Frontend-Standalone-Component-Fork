-- 修改telemetry_app_wayline表结构以适应航线信息.md的数据格式

-- 添加缺失的字段
ALTER TABLE telemetry_app_wayline
ADD COLUMN track_id VARCHAR(50) NULL,
ADD COLUMN drone_sn VARCHAR(50) NULL;

-- 保留现有的字段，但可能需要调整某些字段的长度或类型
-- wayline_id已经存在，将用于存储wayline_uuid
-- name已经存在
-- length将用于存储flight_distance
-- estimated_duration将用于存储flight_duration
-- waypoints将用于存储track.points数组

-- 可选：添加索引以提高查询性能
CREATE INDEX idx_telemetry_app_wayline_wayline_id ON telemetry_app_wayline(wayline_id);
CREATE INDEX idx_telemetry_app_wayline_track_id ON telemetry_app_wayline(track_id);
CREATE INDEX idx_telemetry_app_wayline_drone_sn ON telemetry_app_wayline(drone_sn);

-- 可选：更新现有数据的状态为COMPLETED（如果需要）
UPDATE telemetry_app_wayline SET status = 'COMPLETED' WHERE status IS NULL;