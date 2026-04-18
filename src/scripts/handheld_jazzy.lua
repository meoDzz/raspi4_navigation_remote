include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "base_link",               -- Đổi thành "base_link" nếu KHÔNG có IMU ổn định
  published_frame = "base_link",             -- Frame chính publish pose (thay nếu cần)
  odom_frame = "odom",                       -- Chỉ dùng nếu provide_odom_frame = true
  provide_odom_frame = false,                -- Tắt vì không có odom thật
  publish_frame_projected_to_2d = true,      -- Rất quan trọng cho 2D handheld
  use_odometry = false,                      -- Tắt odometry hoàn toàn
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,
  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

MAP_BUILDER.use_trajectory_builder_2d = true

TRAJECTORY_BUILDER_2D.min_range = 0.12
TRAJECTORY_BUILDER_2D.max_range = 3.5
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 3.
TRAJECTORY_BUILDER_2D.use_imu_data = false          -- Nếu có IMU tốt, bật true và publish /imu
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true  -- Bật để matching realtime tốt hơn khi không có odom
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(0.1)

-- Tinh chỉnh cho handheld (giảm drift khi di chuyển tay)
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 10.0   -- Tăng nếu drift tịnh tiến
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 40.0      -- Tăng để xoay chính xác hơn

-- Pose graph (loop closure)
POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.7
POSE_GRAPH.optimize_every_n_nodes = 30          -- Optimize thường xuyên hơn cho handheld
POSE_GRAPH.global_sampling_ratio = 0.003

return options
