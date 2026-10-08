import time
from datetime import datetime
from smbus2 import SMBus

# Cấu hình I2C cho DS3231
I2C_BUS = 1
RTC_ADDRESS = 0x68
START_REG = 0x00

def dec_to_bcd(val):
    """Chuyển đổi số thập phân sang mã BCD"""
    return ((val // 10) << 4) + (val % 10)

def set_rtc_time():
    # 1. Lấy thời gian hệ thống hiện tại ngay trước khi ghi
    now = datetime.now()
    
    # 2. Quy đổi sang các giá trị tương ứng của DS3231
    second = dec_to_bcd(now.second)
    minute = dec_to_bcd(now.minute)
    hour   = dec_to_bcd(now.hour)    # Chế độ 24h mặc định
    
    # Thứ trong tuần: Python quy định Thứ 2 = 0 -> CN = 6
    # DS3231 thường quy định: CN = 1, Thứ 2 = 2, ..., Thứ 7 = 7
    dow = dec_to_bcd(((now.weekday() + 1) % 7) + 1)
    
    day   = dec_to_bcd(now.day)
    month = dec_to_bcd(now.month)
    year  = dec_to_bcd(now.year % 100) # Chỉ lấy 2 chữ số cuối (ví dụ: 26)

    # Tập hợp block dữ liệu gồm 7 byte liên tục từ Giây -> Năm
    time_block = [second, minute, hour, dow, day, month, year]

    # 3. Ghi đồng thời cả block dữ liệu vào RTC qua I2C nhằm giảm trễ tối đa
    with SMBus(I2C_BUS) as bus:
        bus.write_i2c_block_data(RTC_ADDRESS, START_REG, time_block)
        
    print(f" Đã nạp xong thời gian hệ thống vào RTC: {now.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    set_rtc_time()
