# Cloudflare-IP
# Cloudflare-IP: Công cụ Khám Phá Địa chỉ IP Thực sự của Cloudflare

Cloudflare-IP là một công cụ Python mạnh mẽ được thiết kế tỉ mỉ để phân tích địa chỉ IP thực sự của các trang web được bảo vệ bởi Cloudflare và các giải pháp thay thế khác. Cloudflare là một dịch vụ nâng cao hiệu suất và bảo mật web được sử dụng phổ biến. Nhiệm vụ cốt lõi của Cloudflare-IP là xác định chính xác địa chỉ IP thực của máy chủ web được ẩn sau tấm chắn bảo vệ của Cloudflare. Quét tên miền phụ được sử dụng như một kỹ thuật chính để đạt được mục tiêu này. Công cụ này là một nguồn tài nguyên quý báu cho các chuyên gia kiểm thử thâm nhập, chuyên gia bảo mật và quản trị viên web đang tìm cách đánh giá bảo mật toàn diện và xác định lỗ hổng có thể bị che giấu bởi biện pháp bảo mật của Cloudflare.

## Các Tính Năng Chính:

1. **Phát Hiện IP Thực:**
   - Cloudflare-IP xuất sắc trong việc phân tích địa chỉ IP thực của các máy chủ web sử dụng dịch vụ của Cloudflare. Thông tin này quan trọng để thực hiện các thử nghiệm thâm nhập toàn diện và đảm bảo tính bảo mật của tài sản web.

2. **Quét Tên Miền Phụ:**
   - Quét tên miền phụ được sử dụng như một phần quan trọng trong quá trình xác định địa chỉ IP thực. Hỗ trợ xác định máy chủ thực sự lưu trữ trang web và các tên miền phụ liên quan.

3. **Lịch Sử Địa Chỉ IP:**
   - Truy xuất thông tin địa chỉ IP lịch sử cho một tên miền cụ thể. Sử dụng dịch vụ ViewDNS để hiển thị chi tiết như địa chỉ IP, vị trí, chủ sở hữu và ngày ghi nhận cuối cùng.

4. **Phân Tích Chứng Chỉ SSL:**
   - Trích xuất và phân tích chứng chỉ SSL liên quan đến miền mục tiêu. Cung cấp thông tin về cơ sở hạ tầng lưu trữ và có thể tiết lộ địa chỉ IP thực sự.

5. **API SecurityTrails (Tùy Chọn):**
   - Nếu bạn thêm khóa API SecurityTrails vào tệp `config.ini`, bạn có thể truy xuất thông tin IP lịch sử từ SecurityTrails.

6. **Quét Theo Luồng:**
   - Sử dụng phân luồng để nâng cao hiệu quả và giảm thời gian quét. Cho phép quét một danh sách lớn các tên miền phụ mà không làm chậm quá trình.

7. **Báo Cáo Chi Tiết:**
   - Cung cấp kết quả toàn diện với tổng số tên miền phụ đã quét, tổng số tên miền phụ đã tìm thấy và thời gian quét.

Cloudflare-IP là một công cụ mạnh mẽ giúp bạn đánh giá bảo mật trang web, phát hiện các lỗ hổng tiềm ẩn và bảo vệ tài sản web của bạn bằng cách tiết lộ địa chỉ IP thực.

## Cách Sử Dụng:

Chạy Cloudflare-IP với một đối số dòng lệnh duy nhất:

```bash
git clone https://github.com/bibo318/Cloudflare-IP.git
cd Cloudflare-IP
pip3 install -r requirements.txt

# For Termux (Android) Users
# Sử dụng lệnh sau nếu gặp sự cố khi cài đặt cryptography từ require.txt
pkg install python-cryptography

python Cloudflare-IP.py example.com
 
