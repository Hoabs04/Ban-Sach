# Hướng dẫn Triển khai (Deployment Guide)

Tài liệu này tổng hợp các bước cuối cùng và các lưu ý quan trọng để đưa website Bán Sách lên môi trường Production thực tế một cách an toàn và trơn tru.

---

## 1. Cài đặt và Khởi động Redis

Hiện tại, hệ thống đã được tối ưu để sử dụng **Redis** làm cache (giúp tăng tốc độ tải trang chủ và giảm tải database). Trong file `prod.py`, hệ thống sẽ cố gắng kết nối tới `redis://127.0.0.1:6379/1`. Nếu Redis chưa chạy, ứng dụng sẽ báo lỗi `ConnectionError`.

**Trên máy chủ Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```
Sau khi cài đặt xong, Redis sẽ tự động chạy ở cổng mặc định `6379`. Bạn không cần cấu hình gì thêm.

---

## 2. Cấu hình VNPay Môi trường Thực tế (Production)

Hiện tại, mã nguồn đang sử dụng URL của VNPay Sandbox (`https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`) và thiết lập nhận các mã dummy nếu trong `.env` chưa có thông tin. 

Khi ký kết hợp đồng thật với VNPay và chuyển sang môi trường **Production**, bạn cần thực hiện:

1. Đổi đường dẫn `VNPAY_URL` trong `bookstore/settings/base.py` (hoặc trong `.env` tuỳ bạn khai báo) thành URL thật của VNPay:
   `https://pay.vnpay.vn/vpcpay.html`

2. Lấy **TMN_CODE** và **HASH_SECRET** thật do VNPay cung cấp cho doanh nghiệp của bạn, sau đó điền vào file `.env`:
   ```env
   VNPAY_TMN_CODE=ma_tmn_code_that_cua_ban
   VNPAY_HASH_SECRET_KEY=chuoi_ky_tu_bi_mat_cua_ban
   ```

3. Đảm bảo `VNPAY_RETURN_URL` trong file `base.py` trỏ đúng về domain thật của bạn (ví dụ: `https://domaincuaban.com/orders/vnpay_return/`), đồng thời khai báo IP thật của máy chủ (Web Server) cho phía VNPay để họ cấp quyền (White-list IP).

---

## 3. Các Checklist Cuối Cùng (Production Hardening)

Trước khi thực sự chạy câu lệnh chạy production (như gunicorn/uwsgi), hãy rà soát danh sách sau:

1. **Database:** Cài đặt PostgreSQL, tạo DB và khai báo chuỗi `DATABASE_URL` trong file `.env`. (Đừng quên bỏ comment `psycopg2-binary` trong `requirements.txt`).
2. **Secret Key:** Khai báo một `SECRET_KEY` cực kỳ phức tạp và bảo mật trong `.env`.
3. **Debug:** Chắc chắn rằng biến `DEBUG=False` (Settings trong file `prod.py` đã tự động ép kiểu này, nhưng cẩn thận vẫn tốt hơn).
4. **Static Files:** Chạy lệnh Gom file tĩnh (CSS/JS/Hình ảnh) để WhiteNoise có thể tối ưu hoá băng thông:
   ```bash
   python manage.py collectstatic --noinput
   ```
5. **Chạy Server:** Dùng Gunicorn hoặc Waitress để chạy ứng dụng. Ví dụ với Gunicorn:
   ```bash
   gunicorn bookstore.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```
6. **HTTPS:** Cài đặt chứng chỉ SSL (Let's Encrypt) thông qua Nginx/Apache. Code của chúng ta đã được bật sẵn các chế độ chặn `SECURE_SSL_REDIRECT = True` trong `prod.py` để tự động ép người dùng dùng HTTPS an toàn nhất.

---

## 4. Danh Sách Thông Tin Chủ Shop Cần Tự Thay Đổi

Trước khi khai trương website, chủ shop cần tự rà soát và chỉnh sửa các thông tin cá nhân hóa sau:

1. **Email SMTP (Gửi tự động):** 
   Vào file `.env`, thay đổi `EMAIL_HOST_USER` và `EMAIL_HOST_PASSWORD` thành Gmail và *Mật khẩu ứng dụng* của shop. Update `DEFAULT_FROM_EMAIL` thành email hiển thị với khách hàng.

2. **ALLOWED_HOSTS:**
   Trong file `.env`, sửa giá trị `ALLOWED_HOSTS=localhost,127.0.0.1` thành tên miền thật của bạn (ví dụ: `ALLOWED_HOSTS=nhasachcuaban.com,www.nhasachcuaban.com`).

3. **Thay Đổi Mật Khẩu Admin:**
   Nếu bạn đã chạy `python manage.py runscript seed` để tạo dữ liệu mẫu, hệ thống có thể đã tạo sẵn một tài khoản Admin. Hãy đăng nhập vào trang `/admin`, đổi mật khẩu của tài khoản Admin ngay lập tức, hoặc xóa tài khoản cũ và tạo tài khoản siêu quản trị mới:
   ```bash
   python manage.py createsuperuser
   ```

4. **Thông Tin Liên Hệ Ở Chân Trang (Footer) và Trang Giới Thiệu:**
   Bạn cần vào phần Code HTML ở các file:
   - `templates/includes/footer.html` (Địa chỉ, số điện thoại, email, link Facebook, Tiktok...)
   - `templates/core/about.html` (Bài viết giới thiệu về nhà sách của bạn)
   - `templates/core/shipping_policy.html` & `return_policy.html` (Chính sách riêng của shop)
   
5. **Logo & Favicon:**
   Thay thế các file logo tạm thời bằng logo thật của shop (thường nằm ở `static/images/logo.png` hoặc bạn có thể tải thẳng lên qua trang Admin nếu bạn đã cấu hình DB chứa logo).

Chúc bạn vận hành dự án thành công và đạt doanh thu bùng nổ! 🚀
