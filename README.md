# Bookstore - Website Bán Sách

## Cài đặt

### 1. Clone project
```bash
git clone <repo-url>
cd bookstore
```

### 2. Tạo virtual environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Copy file .env
```bash
copy .env.example .env
```

### 5. Chạy migrations
```bash
python manage.py migrate
```

### 6. Tạo tài khoản admin
```bash
python manage.py createsuperuser
```

### 7. Chạy server
```bash
python manage.py runserver
```

### 8. Cài đặt Tailwind CSS
```bash
npm install
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
```

## Cấu trúc dự án
```
bookstore/
├── manage.py
├── bookstore/          # Project configuration
├── apps/
│   ├── accounts/       # Authentication & user profiles
│   ├── catalog/        # Books, categories, authors
│   ├── cart/           # Shopping cart
│   ├── orders/         # Orders & checkout
│   └── core/           # Shared utilities
├── templates/          # HTML templates
├── static/             # Static files (CSS, JS, images)
├── media/              # User-uploaded files
└── locale/             # Translations (vi, en)
```
