# 📚 Bookstore - Nền Tảng Bán Sách Trực Tuyến

Bookstore là một website thương mại điện tử chuyên cung cấp sách và truyện, được phát triển bằng **Django 5.1.2** kết hợp với **Tailwind CSS**. Website được thiết kế với giao diện hiện đại, tốc độ phản hồi nhanh, cùng với các tính năng quản lý giỏ hàng và thanh toán trực tuyến chuyên nghiệp.

![Bookstore Preview](/static/images/hero-bg.jpg) <!-- Thay ảnh này bằng screenshot website của bạn sau khi up GitHub -->

## ✨ Tính Năng Nổi Bật

- 🎨 **Giao diện hiện đại (UI/UX):** Responsive toàn diện, thiết kế bằng Tailwind CSS, hiệu ứng mượt mà.
- 🛍️ **Quản lý Giỏ hàng & Đơn hàng:** Thêm, sửa, xóa sản phẩm trong giỏ, áp dụng mã giảm giá (Coupon).
- 💳 **Thanh toán Trực tuyến:** Tích hợp cổng thanh toán **VNPay** và phương thức COD, chuyển khoản truyền thống.
- 👤 **Hệ thống Tài khoản (Authentication):** Đăng ký, đăng nhập, quản lý sổ địa chỉ, theo dõi trạng thái đơn hàng.
- ⭐ **Đánh giá & Nhận xét:** Người dùng có thể để lại đánh giá (1-5 sao) cho sách sau khi mua.
- 🚀 **Tối ưu Hiệu suất:** Tích hợp **Redis** để Caching dữ liệu, giúp website tải siêu tốc.
- 🌐 **Đa ngôn ngữ & Tiền tệ:** Hỗ trợ xử lý định dạng tiền tệ Việt Nam (VND).

## 🛠️ Công Nghệ Sử Dụng

- **Backend:** Python 3, Django 5.1.2
- **Frontend:** HTML5, Tailwind CSS
- **Database:** SQLite (Môi trường Dev) / PostgreSQL (Môi trường Prod)
- **Caching:** Redis
- **Thanh toán:** VNPay Sandbox/Production API

## 🚀 Hướng Dẫn Cài Đặt (Local Development)

### 1. Clone dự án và tạo môi trường ảo (Virtual Environment)
```bash
git clone <repo-url>
cd bookstore

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
.\venv\Scripts\activate
# Trên Linux/Mac:
source venv/bin/activate
```

### 2. Cài đặt thư viện (Dependencies)
```bash
pip install -r requirements.txt
```

### 3. Cấu hình Biến môi trường
Copy file `.env.example` thành `.env` và tùy chỉnh các thông số (đặc biệt là Database, Email SMTP, VNPay).
```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

### 4. Khởi tạo Cơ sở dữ liệu và Dữ liệu mẫu (Seed Data)
Dự án được trang bị sẵn script để tạo dữ liệu sách mẫu, danh mục và tác giả.
```bash
python manage.py makemigrations
python manage.py migrate

# Chạy script tạo dữ liệu mẫu (Tùy chọn)
python manage.py runscript seed
```

### 5. Tạo tài khoản Siêu Quản Trị (Admin)
```bash
python manage.py createsuperuser
```

### 6. Khởi động Server
```bash
python manage.py runserver
```
Truy cập: `http://127.0.0.1:8000/` để xem website và `http://127.0.0.1:8000/admin/` để vào trang quản trị.

### 7. Dành cho Frontend Developer (Tailwind CSS)
Nếu bạn muốn chỉnh sửa giao diện Tailwind, bạn cần chạy Node.js watcher:
```bash
npm install
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
```

## 📦 Triển Khai (Deployment)

Để đưa website lên môi trường thực tế (Production), vui lòng tham khảo tài liệu [DEPLOYMENT.md](./DEPLOYMENT.md) để biết thêm về cách cài đặt Redis, gunicorn, cấu hình Nginx, bảo mật và kết nối API VNPay thật.

---

*Được phát triển với ❤️ bởi đội ngũ Bán Sách.*
