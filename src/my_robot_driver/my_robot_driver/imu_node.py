# # import rclpy
# # from rclpy.node import Node
# # from sensor_msgs.msg import Imu
# # from mpu6050 import mpu6050
# # import numpy as np

# # class ImuNode(Node):
# #     def __init__(self):
# #         super().__init__('imu_node')
        
# #         # 1. Khai báo Publisher phát lên topic /imu
# #         self.publisher_ = self.create_publisher(Imu, '/imu', 10)
        
# #         # 2. Khởi tạo cảm biến MPU6050 (Địa chỉ mặc định 0x68)
# #         try:
# #             self.sensor = mpu6050(0x68)
# #             self.get_logger().info("✅ MPU6050 đã sẵn sàng!")
# #         except Exception as e:
# #             self.get_logger().error(f"❌ Không tìm thấy IMU qua I2C: {e}")
# #             return

# #         # 3. Tạo Timer để đọc dữ liệu định kỳ (50Hz = 0.02s)
# #         self.timer_period = 0.02 
# #         self.timer = self.create_timer(self.timer_period, self.timer_callback)

# #     def timer_callback(self):
# #         try:
# #             # Đọc dữ liệu thô từ cảm biến
# #             accel_data = self.sensor.get_accel_data()
# #             gyro_data = self.sensor.get_gyro_data()

# #             msg = Imu()
            
# #             # --- HEADER ---
# #             msg.header.stamp = self.get_clock().now().to_msg()
# #             msg.header.frame_id = 'imu_link' # Phải khớp với TF trong robot

# #             # --- GIA TỐC TUYẾN TÍNH (m/s^2) ---
# #             # MPU6050 trả về đơn vị 'g', cần nhân với 9.80665
# #             msg.linear_acceleration.x = accel_data['x'] * 9.80665
# #             msg.linear_acceleration.y = accel_data['y'] * 9.80665
# #             msg.linear_acceleration.z = accel_data['z'] * 9.80665

# #             # --- VẬN TỐC GÓC (rad/s) ---
# #             # MPU6050 trả về độ/giây, cần đổi sang radian/giây
# #             msg.angular_velocity.x = np.radians(gyro_data['x'])
# #             msg.angular_velocity.y = np.radians(gyro_data['y'])
# #             msg.angular_velocity.z = np.radians(gyro_data['z'])

# #             # --- COVARIANCE (Độ nhiễu) ---
# #             # Cartographer cần các số này để biết mức độ tin cậy của cảm biến
# #             # Nếu để 0 hoàn toàn, một số thuật toán sẽ báo lỗi
# #             msg.linear_acceleration_covariance = [0.01, 0.0, 0.0, 
# #                                                   0.0, 0.01, 0.0, 
# #                                                   0.0, 0.0, 0.01]
            
# #             msg.angular_velocity_covariance = [0.01, 0.0, 0.0, 
# #                                                0.0, 0.01, 0.0, 
# #                                                0.0, 0.0, 0.01]
            
# #             # -1 báo hiệu rằng IMU này không cung cấp dữ liệu hướng (Orientation)
# #             msg.orientation_covariance = [-1.0] * 9 

# #             # Publish dữ liệu
# #             self.publisher_.publish(msg)

# #         except Exception as e:
# #             self.get_logger().warn(f"Mất kết nối với IMU: {e}")

# # def main(args=None):
# #     rclpy.init(args=args)
# #     imu_node = ImuNode()
# #     try:
# #         rclpy.spin(imu_node)
# #     except KeyboardInterrupt:
# #         pass
# #     finally:
# #         imu_node.destroy_node()
# #         rclpy.shutdown()

# # if __name__ == '__main__':
# #     main()


# import smbus2
# import time
# import math

# class MPU6050Raw:
#     def __init__(self, address=0x68):
#         self.bus = smbus2.SMBus(1) # Cổng I2C số 1 trên Pi
#         self.address = address
        
#         # Đánh thức MPU6050 (Mặc định nó ở chế độ ngủ khi vừa cấp điện)
#         # Ghi giá trị 0 vào thanh ghi PWR_MGMT_1 (0x6B)
#         self.bus.write_byte_data(self.address, 0x6B, 0)

#     def read_raw_data(self, addr):
#         # MPU6050 lưu dữ liệu 16-bit trong 2 thanh ghi 8-bit (High và Low)
#         high = self.bus.read_byte_data(self.address, addr)
#         low = self.bus.read_byte_data(self.address, addr + 1)
        
#         # Kết hợp 2 byte lại
#         value = (high << 8) | low
        
#         # Xử lý số có dấu (2's complement) cho hệ 16-bit
#         if value > 32768:
#             value = value - 65536
#         return value

#     def get_data(self):
#         # 0x3B là địa chỉ bắt đầu của cụm thanh ghi Gia tốc (Accel X, Y, Z)
#         acc_x = self.read_raw_data(0x3B)
#         acc_y = self.read_raw_data(0x3C)
#         acc_z = self.read_raw_data(0x3E)
        
#         # 0x43 là địa chỉ bắt đầu của cụm thanh ghi Con quay (Gyro X, Y, Z)
#         gyro_x = self.read_raw_data(0x43)
#         gyro_y = self.read_raw_data(0x45)
#         gyro_z = self.read_raw_data(0x47)

#         # Chuyển đổi sang đơn vị vật lý (với cấu hình mặc định)
#         # Gia tốc: Chia cho 16384.0 (dải +/- 2g)
#         # Con quay: Chia cho 131.0 (dải +/- 250 deg/s)
#         return {
#             'accel': {
#                 'x': acc_x / 16384.0,
#                 'y': acc_y / 16384.0,
#                 'z': acc_z / 16384.0
#             },
#             'gyro': {
#                 'x': gyro_x / 131.0,
#                 'y': gyro_y / 131.0,
#                 'z': gyro_z / 131.0
#             }
#         }

# # --- Test thử ---
# if __name__ == "__main__":
#     imu = MPU6050Raw()
#     while True:
#         data = imu.get_data()
#         print(f"Accel X: {data['accel']['x']:.2f}g | Gyro Z: {data['gyro']['z']:.2f} deg/s")
#         time.sleep(0.1)



import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import smbus2
import numpy as np
import time

class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node')
        self.publisher_ = self.create_publisher(Imu, '/imu', 10)
        
        # Thiết lập I2C thuần
        self.bus = smbus2.SMBus(1)
        self.address = 0x68
        self.bus.write_byte_data(self.address, 0x6B, 0) # Wake up

        # Các biến phục vụ lọc và hiệu chuẩn
        self.alpha = 0.2  # Hệ số lọc (Low-pass filter)
        self.gyro_bias = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.accel_bias = {'x': 0.0, 'y': 0.0, 'z': 0.0} # THÊM BIAS CHO GIA TỐC
        self.last_gyro = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.last_accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        # Bắt đầu hiệu chuẩn ngay khi bật
        self.calibrate_imu()
        
        self.timer = self.create_timer(0.02, self.publish_imu) # 50Hz

    def read_raw(self, addr):
        high = self.bus.read_byte_data(self.address, addr)
        low = self.bus.read_byte_data(self.address, addr + 1)
        val = (high << 8) | low
        return val - 65536 if val > 32768 else val

    def calibrate_imu(self):
        self.get_logger().info("Đang hiệu chuẩn IMU (Cả Gyro & Accel)... ĐỪNG DI CHUYỂN ROBOT!")
        samples = 1000
        gx, gy, gz = 0, 0, 0
        ax, ay, az = 0.0, 0.0, 0.0
        
        for _ in range(samples):
            # Đọc Gyro thô
            gx += self.read_raw(0x43)
            gy += self.read_raw(0x45)
            gz += self.read_raw(0x47)
            
            # Đọc Accel thô và đổi sang m/s^2 luôn để tính tổng
            ax += (self.read_raw(0x3B) / 16384.0) * 9.80665
            ay += (self.read_raw(0x3D) / 16384.0) * 9.80665
            az += (self.read_raw(0x3F) / 16384.0) * 9.80665
            
            time.sleep(0.01)
        
        # Lưu lại Bias trung bình cho Gyro
        self.gyro_bias['x'] = (gx / samples) / 131.0
        self.gyro_bias['y'] = (gy / samples) / 131.0
        self.gyro_bias['z'] = (gz / samples) / 131.0
        
        # Lưu lại Bias trung bình cho Accel (Bao gồm cả trọng lực và độ nghiêng)
        self.accel_bias['x'] = ax / samples
        self.accel_bias['y'] = ay / samples
        self.accel_bias['z'] = az / samples
        
        self.get_logger().info("Hiệu chuẩn xong! Đã đưa toàn bộ dữ liệu ban đầu về 0.")

    def publish_imu(self):
        # 1. Đọc dữ liệu mới và TRỪ ĐI BIAS (Ép về 0)
        raw_accel = {
            'x': ((self.read_raw(0x3B) / 16384.0) * 9.80665) - self.accel_bias['x'],
            'y': ((self.read_raw(0x3D) / 16384.0) * 9.80665) - self.accel_bias['y'],
            'z': ((self.read_raw(0x3F) / 16384.0) * 9.80665) - self.accel_bias['z']
        }
        
        raw_gyro = {
            'x': np.radians((self.read_raw(0x43) / 131.0) - self.gyro_bias['x']),
            'y': np.radians((self.read_raw(0x45) / 131.0) - self.gyro_bias['y']),
            'z': np.radians((self.read_raw(0x47) / 131.0) - self.gyro_bias['z'])
        }

        # 2. Áp dụng Bộ lọc thông thấp (Low-pass Filter)
        filtered_accel = {}
        filtered_gyro = {}
        for axis in ['x', 'y', 'z']:
            filtered_accel[axis] = self.alpha * raw_accel[axis] + (1 - self.alpha) * self.last_accel[axis]
            filtered_gyro[axis] = self.alpha * raw_gyro[axis] + (1 - self.alpha) * self.last_gyro[axis]

        # Lưu lại cho lần lọc kế tiếp
        self.last_accel = filtered_accel
        self.last_gyro = filtered_gyro

        # 3. Đóng gói ROS message
        msg = Imu()

        # Ma trận Covariance để Cartographer không bị lỗi chia cho 0
        msg.linear_acceleration_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        msg.angular_velocity_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        msg.orientation_covariance = [-1.0] * 9 # Báo hiệu không có dữ liệu quaternion (hướng)

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'
        
        msg.linear_acceleration.x = filtered_accel['x']
        msg.linear_acceleration.y = filtered_accel['y']
        msg.linear_acceleration.z = filtered_accel['z'] + 9.81
        
        msg.angular_velocity.x = filtered_gyro['x']
        msg.angular_velocity.y = filtered_gyro['y']
        msg.angular_velocity.z = filtered_gyro['z']

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()