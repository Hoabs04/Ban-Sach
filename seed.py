import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings.dev')
django.setup()

from apps.catalog.models import Category, Author, Publisher, Book
from apps.accounts.models import User

def seed():
    # Create superuser
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    if not User.objects.filter(email=admin_email).exists():
        import secrets
        password = os.environ.get('ADMIN_PASSWORD') or secrets.token_urlsafe(12)
        User.objects.create_superuser('admin', admin_email, password)
        if os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('dev'):
            print(f"Created superuser {admin_email} / {password}")
            print("Vui lòng lưu lại mật khẩu này!")
        else:
            print(f"Created superuser {admin_email}. Mật khẩu đã được thiết lập.")

    # Categories
    categories_data = [
        ('Văn học', 'Các tác phẩm văn học kinh điển và hiện đại'),
        ('Kinh tế', 'Sách về kinh tế, quản trị kinh doanh, đầu tư'),
        ('Kỹ năng sống', 'Sách phát triển bản thân, kỹ năng mềm'),
        ('Thiếu nhi', 'Truyện tranh, truyện cổ tích cho thiếu nhi'),
    ]
    categories = {}
    for name, desc in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
        categories[name] = cat

    # Authors
    authors_data = ['Nguyễn Nhật Ánh', 'Dale Carnegie', 'Tony Buổi Sáng', 'Paulo Coelho', 'Tô Hoài']
    authors = {}
    for name in authors_data:
        author, _ = Author.objects.get_or_create(name=name)
        authors[name] = author

    # Publishers
    pubs_data = ['NXB Trẻ', 'NXB Kim Đồng', 'NXB Tổng hợp TP.HCM', 'NXB Hội Nhà Văn']
    pubs = {}
    for name in pubs_data:
        pub, _ = Publisher.objects.get_or_create(name=name)
        pubs[name] = pub

    # Books
    books_data = [
        {
            'title': 'Mắt Biếc',
            'author_names': ['Nguyễn Nhật Ánh'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Văn học'],
            'price': Decimal('110000'),
            'original_price': Decimal('150000'),
            'description': 'Một câu chuyện tình buồn và đẹp của Ngạn và Hà Lan.',
            'stock': 100,
            'is_featured': True,
        },
        {
            'title': 'Đắc Nhân Tâm',
            'author_names': ['Dale Carnegie'],
            'pub_name': 'NXB Tổng hợp TP.HCM',
            'cat_names': ['Kỹ năng sống'],
            'price': Decimal('80000'),
            'original_price': Decimal('100000'),
            'description': 'Cuốn sách nổi tiếng nhất mọi thời đại về nghệ thuật giao tiếp.',
            'stock': 50,
            'is_featured': True,
        },
        {
            'title': 'Dế Mèn Phiêu Lưu Ký',
            'author_names': ['Tô Hoài'],
            'pub_name': 'NXB Kim Đồng',
            'cat_names': ['Văn học', 'Thiếu nhi'],
            'price': Decimal('45000'),
            'original_price': None,
            'description': 'Cuộc phiêu lưu kỳ thú của Dế Mèn.',
            'stock': 200,
            'is_featured': False,
        },
        {
            'title': 'Nhà Giả Kim',
            'author_names': ['Paulo Coelho'],
            'pub_name': 'NXB Hội Nhà Văn',
            'cat_names': ['Văn học'],
            'price': Decimal('65000'),
            'original_price': Decimal('75000'),
            'description': 'Hành trình đi tìm kho báu của cậu bé chăn cừu.',
            'stock': 80,
            'is_featured': True,
        },
        {
            'title': 'Trên Đường Băng',
            'author_names': ['Tony Buổi Sáng'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Kỹ năng sống', 'Kinh tế'],
            'price': Decimal('90000'),
            'original_price': Decimal('120000'),
            'description': 'Chuẩn bị hành trang cho người trẻ vào đời.',
            'stock': 150,
            'is_featured': False,
        }
    ]

    for data in books_data:
        book, created = Book.objects.get_or_create(
            title=data['title'],
            defaults={
                'publisher': pubs[data['pub_name']],
                'price': data['price'],
                'original_price': data['original_price'],
                'description': data['description'],
                'stock': data['stock'],
                'is_featured': data['is_featured'],
                'format': 'paperback',
                'pages': random.randint(150, 400),
                'language': 'Tiếng Việt',
            }
        )
        if created:
            for author_name in data['author_names']:
                book.authors.add(authors[author_name])
            for cat_name in data['cat_names']:
                book.categories.add(categories[cat_name])

    print("Seed data successfully created!")

if __name__ == '__main__':
    seed()
