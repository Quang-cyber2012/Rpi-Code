import datetime
from smbus2 import SMBus

# Địa chỉ I2C của module RTC
RTC_ADDRESS = 0x68

# Hàm chuyển đổi số thập phân sang định dạng BCD (Hex) để RTC hiểu
def dec_to_bcd(val):
    return ((val // 10) << 4) + (val % 10)

def sync_system_to_rtc():
    # 1. Lấy thời gian hệ thống hiện tại
    now = datetime.datetime.now()
    
    # 2. Chuyển đổi các giá trị sang BCD
    second = dec_to_bcd(now.second)
    minute = dec_to_bcd(now.minute)
    hour   = dec_to_bcd(now.hour)   # Mặc định chế độ 24h
    day    = dec_to_bcd(now.day)
    month  = dec_to_bcd(now.month)
    year   = dec_to_bcd(now.year % 100) # Chỉ lấy 2 số cuối của năm (ví dụ: 26)
    weekday = dec_to_bcd(now.isoweekday()) # 1=Thứ 2, 7=Chủ Nhật

    # 3. Chuẩn bị chuỗi byte để nạp liên tục (Block Write) vào RTC từ thanh ghi 0x00
    # Thứ tự thanh ghi DS3231/DS1307: Giây (00), Phút (01), Giờ (02), Thứ (03), Ngày (04), Tháng (05), Năm (06)
    time_bytes = [second, minute, hour, weekday, day, month, year]

    # 4. Thực hiện ghi trực tiếp xuống I2C bus 1 với độ trễ thấp nhất
    try:
        with SMBus(1) as bus:
            bus.write_i2c_block_data(RTC_ADDRESS, 0x00, time_bytes)
        print(f"✅ Đã nạp RTC thành công lúc: {now.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    except Exception as e:
        print(f"❌ Lỗi kết nối I2C: {e}. Vui lòng kiểm tra xem RTC có bị 'UU' không.")

if __name__ == "__main__":
    sync_system_to_rtc()
