import datetime
from smbus2 import SMBus

# 1. Hàm chuyển thập phân (Dec) sang mã Hex/BCD cho chip RTC
def dec_to_bcd(val):
    return ((val // 10) << 4) | (val % 10)

# 2. TỰ ĐỘNG lấy thời gian hiện tại của hệ thống (giống lệnh `date`)
dt = datetime.datetime.now()

second = dt.second
minute = dt.minute
hour = dt.hour
day = dt.day
month = dt.month
year = dt.year % 100            # Chỉ lấy 2 số cuối của năm (ví dụ: 2026 -> 26)
weekday = dt.isoweekday()       # Thứ trong tuần (1 = Thứ 2, 7 = Chủ Nhật)

# 3. Địa chỉ I2C của Module RTC (Mặc định thường là 0x68 cho DS3231/DS1307)
RTC_ADDRESS = 0x68  

try:
    with SMBus(1) as bus:
        # Đóng gói dữ liệu dạng Hex/BCD theo đúng thứ tự các thanh ghi RTC
        rtc_data = [
            dec_to_bcd(second),   # Thanh ghi 0x00: Giây
            dec_to_bcd(minute),   # Thanh ghi 0x01: Phút
            dec_to_bcd(hour),     # Thanh ghi 0x02: Giờ
            dec_to_bcd(weekday),  # Thanh ghi 0x03: Thứ trong tuần
            dec_to_bcd(day),      # Thanh ghi 0x04: Ngày
            dec_to_bcd(month),    # Thanh ghi 0x05: Tháng
            dec_to_bcd(year)      # Thanh ghi 0x06: Năm
        ]
        
        # Ghi toàn bộ cấu trúc thời gian Hex vào RTC từ thanh ghi số 0
        bus.write_i2c_block_data(RTC_ADDRESS, 0x00, rtc_data)
        
        print("--- ĐỒNG BỘ THÀNH CÔNG ---")
        print(f"Thời gian hệ thống vừa lấy: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mã Hex (BCD) nạp vào RTC  : {[hex(x) for x in rtc_data]}")

except Exception as e:
    print(f"❌ Lỗi: Không thể kết nối hoặc ghi dữ liệu I2C: {e}")
