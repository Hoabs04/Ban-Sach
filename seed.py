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
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@bookstore.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123456')
    admin_user = User.objects.filter(username='admin').first() or User.objects.filter(email=admin_email).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', admin_email, admin_password)
    else:
        admin_user.set_password(admin_password)
        admin_user.email = admin_email
        admin_user.is_superuser = True
        admin_user.is_staff = True

    admin_user.role = User.Role.ADMIN
    admin_user.first_name = 'Quản trị'
    admin_user.last_name = 'Hệ thống'
    admin_user.save()

    # Link allauth verified email
    from allauth.account.models import EmailAddress
    EmailAddress.objects.filter(user=admin_user).delete()
    EmailAddress.objects.create(
        user=admin_user,
        email=admin_email,
        verified=True,
        primary=True
    )
    print(f"Superuser configured: {admin_user.username} ({admin_email}) / {admin_password}")

    # Categories
    categories_data = [
        ('Văn học', 'Các tác phẩm văn học kinh điển và hiện đại'),
        ('Kinh tế', 'Sách về kinh tế, quản trị kinh doanh, đầu tư'),
        ('Kỹ năng sống', 'Sách phát triển bản thân, kỹ năng mềm'),
        ('Thiếu nhi', 'Truyện tranh, truyện cổ tích cho thiếu nhi'),
        ('Khoa học - Lịch sử', 'Sách về khoa học vũ trụ, lịch sử nhân loại và tri thức thế giới'),
        ('Tâm lý', 'Sách tâm lý học, chữa lành tâm hồn và thấu hiểu bản thân'),
    ]
    categories = {}
    for name, desc in categories_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
        categories[name] = cat

    # Authors
    authors_data = [
        'Nguyễn Nhật Ánh', 'Dale Carnegie', 'Tony Buổi Sáng', 'Paulo Coelho', 'Tô Hoài',
        'Rosie Nguyễn', 'José Mauro de Vasconcelos', 'Antoine de Saint-Exupéry',
        'Daniel Kahneman', 'Morgan Housel', 'Yuval Noah Harari', 'Robert T. Kiyosaki',
        'Thích Minh Niệm', 'Andrea Hirata'
    ]
    authors = {}
    for name in authors_data:
        author, _ = Author.objects.get_or_create(name=name)
        authors[name] = author

    # Publishers
    pubs_data = [
        'NXB Trẻ', 'NXB Kim Đồng', 'NXB Tổng hợp TP.HCM', 'NXB Hội Nhà Văn',
        'NXB Thế Giới', 'NXB Tri Thức'
    ]
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
            'short_description': 'Tác phẩm lãng mạn kinh điển của nhà văn Nguyễn Nhật Ánh.',
            'stock': 100,
            'is_featured': True,
            'cover_image': 'books/covers/mat-biec.jpg',
            'pages': 300,
            'publication_year': 2019,
            'format': 'paperback',
        },
        {
            'title': 'Đắc Nhân Tâm',
            'author_names': ['Dale Carnegie'],
            'pub_name': 'NXB Tổng hợp TP.HCM',
            'cat_names': ['Kỹ năng sống'],
            'price': Decimal('80000'),
            'original_price': Decimal('100000'),
            'description': 'Cuốn sách nổi tiếng nhất mọi thời đại về nghệ thuật giao tiếp.',
            'short_description': 'Nghệ thuật thu phục lòng người và dẫn lối thành công.',
            'stock': 50,
            'is_featured': True,
            'cover_image': 'books/covers/dac-nhan-tam.jpg',
            'pages': 320,
            'publication_year': 2020,
            'format': 'paperback',
        },
        {
            'title': 'Dế Mèn Phiêu Lưu Ký',
            'author_names': ['Tô Hoài'],
            'pub_name': 'NXB Kim Đồng',
            'cat_names': ['Văn học', 'Thiếu nhi'],
            'price': Decimal('45000'),
            'original_price': None,
            'description': 'Cuộc phiêu lưu kỳ thú của Dế Mèn.',
            'short_description': 'Tác phẩm thiếu nhi kinh điển của nền văn học Việt Nam.',
            'stock': 200,
            'is_featured': False,
            'cover_image': 'books/covers/de-men-phieu-luu-ky.jpg',
            'pages': 180,
            'publication_year': 2018,
            'format': 'paperback',
        },
        {
            'title': 'Nhà Giả Kim',
            'author_names': ['Paulo Coelho'],
            'pub_name': 'NXB Hội Nhà Văn',
            'cat_names': ['Văn học'],
            'price': Decimal('65000'),
            'original_price': Decimal('75000'),
            'description': 'Hành trình đi tìm kho báu của cậu bé chăn cừu.',
            'short_description': 'Cuốn sách bán chạy chỉ sau Kinh Thánh về hành trình theo đuổi ước mơ.',
            'stock': 80,
            'is_featured': True,
            'cover_image': 'books/covers/nha-gia-kim.jpg',
            'pages': 228,
            'publication_year': 2020,
            'format': 'paperback',
        },
        {
            'title': 'Trên Đường Băng',
            'author_names': ['Tony Buổi Sáng'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Kỹ năng sống', 'Kinh tế'],
            'price': Decimal('90000'),
            'original_price': Decimal('120000'),
            'description': 'Chuẩn bị hành trang cho người trẻ vào đời.',
            'short_description': 'Cẩm nang truyền cảm hứng hành động và hội nhập quốc tế cho giới trẻ.',
            'stock': 150,
            'is_featured': False,
            'cover_image': 'books/covers/tren-duong-bang.jpg',
            'pages': 304,
            'publication_year': 2019,
            'format': 'paperback',
        },
        {
            'title': 'Tuổi Trẻ Đáng Giá Bao Nhiêu?',
            'author_names': ['Rosie Nguyễn'],
            'pub_name': 'NXB Hội Nhà Văn',
            'cat_names': ['Kỹ năng sống'],
            'price': Decimal('75000'),
            'original_price': Decimal('90000'),
            'short_description': 'Cuốn sách truyền cảm hứng sống tích cực, chủ động cho người trẻ Việt.',
            'description': 'Cuốn sách là những bài học thực tế, lời khuyên chân thành của tác giả Rosie Nguyễn về việc tự học, trải nghiệm và định vị bản thân trong những năm tháng thanh xuân quý giá.',
            'stock': 120,
            'is_featured': True,
            'cover_image': 'books/covers/tuoi-tre-dang-gia-bao-nhieu.jpg',
            'pages': 292,
            'publication_year': 2018,
            'format': 'paperback',
        },
        {
            'title': 'Cây Cam Ngọt Của Tôi',
            'author_names': ['José Mauro de Vasconcelos'],
            'pub_name': 'NXB Hội Nhà Văn',
            'cat_names': ['Văn học'],
            'price': Decimal('85000'),
            'original_price': Decimal('108000'),
            'short_description': 'Một tác phẩm kinh điển của văn học Brazil khiến hàng triệu độc giả rơi nước mắt.',
            'description': 'Mở đầu bằng những thanh âm trong trẻo của tuổi thơ, Cây Cam Ngọt Của Tôi đưa người đọc theo chân Zezé – một cậu bé năm tuổi thông minh, tinh nghịch nhưng sinh ra trong gia đình nghèo khổ đông con.',
            'stock': 90,
            'is_featured': True,
            'cover_image': 'books/covers/cay-cam-ngot-cua-toi.jpg',
            'pages': 244,
            'publication_year': 2020,
            'format': 'paperback',
        },
        {
            'title': 'Hoàng Tử Bé',
            'author_names': ['Antoine de Saint-Exupéry'],
            'pub_name': 'NXB Kim Đồng',
            'cat_names': ['Văn học', 'Thiếu nhi'],
            'price': Decimal('55000'),
            'original_price': Decimal('70000'),
            'short_description': 'Kiệt tác văn học Pháp dành cho trẻ em và những người lớn từng là trẻ em.',
            'description': 'Cuộc gặp gỡ giữa viên phi công bị rơi máy bay trên sa mạc Sahara và cậu bé tóc vàng đến từ tiểu tinh cầu B612 mở ra những bài học triết lý sâu sắc về tình bạn, tình yêu và cuộc sống.',
            'stock': 150,
            'is_featured': True,
            'cover_image': 'books/covers/hoang-tu-be.jpg',
            'pages': 104,
            'publication_year': 2021,
            'format': 'paperback',
        },
        {
            'title': 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh',
            'author_names': ['Nguyễn Nhật Ánh'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Văn học', 'Thiếu nhi'],
            'price': Decimal('125000'),
            'original_price': Decimal('150000'),
            'short_description': 'Bản tình ca tuổi thơ đong đầy cảm xúc nơi miền quê nghèo miền Trung.',
            'description': 'Cuốn sách đưa người đọc trở về với tuổi thơ hồn nhiên bên cánh đồng làng, bờ ao, con suối qua 81 mẩu chuyện nhỏ của cậu bé Thiều.',
            'stock': 100,
            'is_featured': True,
            'cover_image': 'books/covers/toi-thay-hoa-vang-tren-co-xanh.jpg',
            'pages': 378,
            'publication_year': 2019,
            'format': 'paperback',
        },
        {
            'title': 'Tư Duy Nhanh Và Chậm',
            'author_names': ['Daniel Kahneman'],
            'pub_name': 'NXB Thế Giới',
            'cat_names': ['Kinh tế', 'Kỹ năng sống'],
            'price': Decimal('185000'),
            'original_price': Decimal('239000'),
            'short_description': 'Tuyệt tác của nhà tâm lý học đoạt giải Nobel Kinh tế Daniel Kahneman.',
            'description': 'Tư Duy Nhanh Và Chậm giải mã hai hệ thống định hình nhận thức và quyết định của chúng ta: Hệ thống 1 vận hành tự động, cảm tính; Hệ thống 2 vận hành chậm rãi, cẩn trọng và suy xét logic.',
            'stock': 65,
            'is_featured': False,
            'cover_image': 'books/covers/tu-duy-nhanh-va-cham.jpg',
            'pages': 612,
            'publication_year': 2021,
            'format': 'paperback',
        },
        {
            'title': 'Tâm Lý Học Về Tiền',
            'author_names': ['Morgan Housel'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Kinh tế', 'Kỹ năng sống'],
            'price': Decimal('135000'),
            'original_price': Decimal('168000'),
            'short_description': '19 câu chuyện sâu sắc về cách con người suy nghĩ và hành xử với tiền bạc.',
            'description': 'Thành công tài chính không hoàn toàn là một môn khoa học chính xác dựa trên bảng tính, mà là một kỹ năng mềm nơi hành vi của bạn quan trọng hơn nhiều so với những gì bạn biết.',
            'stock': 85,
            'is_featured': True,
            'cover_image': 'books/covers/tam-ly-hoc-ve-tien.jpg',
            'pages': 384,
            'publication_year': 2022,
            'format': 'paperback',
        },
        {
            'title': 'Lược Sử Loài Người',
            'author_names': ['Yuval Noah Harari'],
            'pub_name': 'NXB Tri Thức',
            'cat_names': ['Khoa học - Lịch sử', 'Văn học'],
            'price': Decimal('210000'),
            'original_price': Decimal('260000'),
            'short_description': 'Bản hùng ca đầy kinh ngạc về hành trình tiến hóa và làm chủ Trái Đất của loài người.',
            'description': 'Từ một loài vượn không có gì nổi bật ở vùng thảo nguyên Đông Phi, làm thế nào Homo Sapiens vươn lên thống trị hành tinh? Phân tích 3 cuộc cách mạng lớn trong lịch sử nhân loại.',
            'stock': 70,
            'is_featured': True,
            'cover_image': 'books/covers/luoc-su-loai-nguoi.jpg',
            'pages': 560,
            'publication_year': 2020,
            'format': 'hardcover',
        },
        {
            'title': 'Cha Giàu Cha Nghèo',
            'author_names': ['Robert T. Kiyosaki'],
            'pub_name': 'NXB Trẻ',
            'cat_names': ['Kinh tế'],
            'price': Decimal('95000'),
            'original_price': Decimal('125000'),
            'short_description': 'Cuốn sách tài chính cá nhân kinh điển thay đổi tư duy làm giàu của hàng triệu người.',
            'description': 'Thông qua những bài học tương phản giữa hai người cha, tác giả Robert Kiyosaki vạch ra sự khác biệt giữa tài sản và tiêu sản, cùng tầm quan trọng của giáo dục tài chính.',
            'stock': 110,
            'is_featured': False,
            'cover_image': 'books/covers/cha-giau-cha-ngheo.jpg',
            'pages': 336,
            'publication_year': 2019,
            'format': 'paperback',
        },
        {
            'title': 'Hiểu Về Trái Tim',
            'author_names': ['Thích Minh Niệm'],
            'pub_name': 'NXB Tổng hợp TP.HCM',
            'cat_names': ['Kỹ năng sống', 'Tâm lý'],
            'price': Decimal('115000'),
            'original_price': Decimal('145000'),
            'short_description': 'Hành trình chữa lành và thấu hiểu những cung bậc cảm xúc bên trong tâm hồn.',
            'description': 'Tập hợp 50 bài viết tương ứng với 50 trạng thái tâm lý của con người: Khổ đau, Hạnh phúc, Tình yêu, Tức giận, Tha thứ, Buông xả... giúp mỗi người tự chữa lành và sống an yên.',
            'stock': 95,
            'is_featured': True,
            'cover_image': 'books/covers/hieu-ve-trai-tim.jpg',
            'pages': 480,
            'publication_year': 2021,
            'format': 'paperback',
        },
        {
            'title': 'Chiến Binh Cầu Vồng',
            'author_names': ['Andrea Hirata'],
            'pub_name': 'NXB Hội Nhà Văn',
            'cat_names': ['Văn học', 'Thiếu nhi'],
            'price': Decimal('88000'),
            'original_price': Decimal('109000'),
            'short_description': 'Câu chuyện phi thường về nghị lực đến trường của 10 đứa trẻ nghèo trên đảo Belitong.',
            'description': 'Được mệnh danh là cuốn sách bán chạy nhất mọi thời đại của Indonesia, kể về hành trình kiên cường của cô giáo trẻ Muslimah và 10 học trò nghèo tại ngôi trường xập xệ.',
            'stock': 80,
            'is_featured': False,
            'cover_image': 'books/covers/chien-binh-cau-vong.jpg',
            'pages': 428,
            'publication_year': 2020,
            'format': 'paperback',
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
                'short_description': data.get('short_description', ''),
                'stock': data['stock'],
                'is_featured': data['is_featured'],
                'cover_image': data.get('cover_image', ''),
                'format': data.get('format', 'paperback'),
                'pages': data.get('pages', random.randint(150, 400)),
                'publication_year': data.get('publication_year', 2020),
                'language': 'Tiếng Việt',
            }
        )
        if not created and 'cover_image' in data:
            book.cover_image = data['cover_image']
            if data.get('short_description'):
                book.short_description = data['short_description']
            book.save()

        for author_name in data['author_names']:
            book.authors.add(authors[author_name])
        for cat_name in data['cat_names']:
            book.categories.add(categories[cat_name])

    print("Seed data successfully created / updated!")

if __name__ == '__main__':
    seed()
