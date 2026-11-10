import os
import sys

# Đảm bảo đường dẫn thư mục hiện tại có trong sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from factory import create_app
    from extensions import db
    from models import Product, Order, OrderItem
except (ImportError, ValueError):
    from api_session_8.factory import create_app
    from api_session_8.extensions import db
    from api_session_8.models import Product, Order, OrderItem

def seed_database():
    """Tạo lại bảng và nạp dữ liệu mẫu phong phú vào dev.db"""
    app = create_app()

    with app.app_context():
        print("--> Đang dọn dẹp và khởi tạo lại cấu trúc bảng...")
        db.drop_all()
        db.create_all()

        print("--> Đang nạp danh sách Sản phẩm mẫu (Products)...")
        products = [
            Product(
                sku="IPHONE-15-PRO",
                name="iPhone 15 Pro 256GB - Titan Tự Nhiên",
                description="Chip A17 Pro, Khung viền Titan, Camera 48MP siêu nét",
                price_cents=109900,  # $1,099.00
                qty_in_stock=25,
            ),
            Product(
                sku="SAMS-S24-ULTRA",
                name="Samsung Galaxy S24 Ultra 512GB",
                description="Galaxy AI, Snapdragon 8 Gen 3, Bút S-Pen tích hợp",
                price_cents=129900,  # $1,299.00
                qty_in_stock=18,
            ),
            Product(
                sku="MACBOOK-M3-14",
                name="MacBook Pro 14 inch M3 Pro",
                description="18GB RAM, 512GB SSD, Màn hình Liquid Retina XDR",
                price_cents=199900,  # $1,999.00
                qty_in_stock=12,
            ),
            Product(
                sku="DELL-XPS-15",
                name="Dell XPS 15 9530 Core i7",
                description="Intel Core i7-13700H, 16GB RAM, RTX 4050, Màn hình OLED 3.5K",
                price_cents=169900,  # $1,699.00
                qty_in_stock=10,
            ),
            Product(
                sku="SONY-WH1000XM5",
                name="Tai nghe chống ồn Sony WH-1000XM5",
                description="Chống ồn chủ động đỉnh cao, thời lượng pin 30 giờ liên tục",
                price_cents=39900,   # $399.00
                qty_in_stock=30,
            ),
            Product(
                sku="AIRPODS-PRO-2",
                name="Apple AirPods Pro 2 (Cổng sạc Type-C)",
                description="Khử tiếng ồn gấp 2 lần, Spatial Audio, Chống nước IP54",
                price_cents=24900,   # $249.00
                qty_in_stock=40,
            ),
            Product(
                sku="IPAD-AIR-M2",
                name="iPad Air 11 inch M2 Wi-Fi 128GB",
                description="Hiệu năng M2 đột phá, hỗ trợ Apple Pencil Pro",
                price_cents=59900,   # $599.00
                qty_in_stock=15,
            ),
            Product(
                sku="LOGI-MX-M3S",
                name="Chuột không dây Logitech MX Master 3S",
                description="Cảm biến 8K DPI Darkfield, cuộn MagSpeed siêu nhanh, yên tĩnh",
                price_cents=9900,    # $99.00
                qty_in_stock=50,
            ),
            Product(
                sku="LG-27GP850",
                name="Màn hình Gaming LG UltraGear 27 inch 2K 165Hz",
                description="Nano IPS 1ms, HDR400, tương thích G-Sync / FreeSync",
                price_cents=34900,   # $349.00
                qty_in_stock=14,
            ),
        ]

        db.session.add_all(products)
        db.session.commit()
        print(f"    ✓ Đã tạo thành công {len(products)} sản phẩm.")

        print("--> Đang nạp danh sách Đơn hàng mẫu (Orders & OrderItems)...")
        # Đơn hàng 1
        order1 = Order(
            customer_name="Nguyễn Văn An",
            customer_email="an.nguyen@example.com",
            status="COMPLETED",
            total_amount_cents=(109900 * 1) + (24900 * 1),  # iPhone 15 Pro + AirPods Pro 2
        )
        item1_1 = OrderItem(order=order1, product=products[0], quantity=1, unit_price_cents=109900)
        item1_2 = OrderItem(order=order1, product=products[5], quantity=1, unit_price_cents=24900)
        # Giảm tồn kho
        products[0].qty_in_stock -= 1
        products[5].qty_in_stock -= 1

        # Đơn hàng 2
        order2 = Order(
            customer_name="Trần Thị Bích",
            customer_email="bich.tran@example.com",
            status="COMPLETED",
            total_amount_cents=(199900 * 1) + (9900 * 1),  # MacBook Pro M3 + Chuột Logitech
        )
        item2_1 = OrderItem(order=order2, product=products[2], quantity=1, unit_price_cents=199900)
        item2_2 = OrderItem(order=order2, product=products[7], quantity=1, unit_price_cents=9900)
        products[2].qty_in_stock -= 1
        products[7].qty_in_stock -= 1

        # Đơn hàng 3
        order3 = Order(
            customer_name="Lê Hoàng Long",
            customer_email="long.le@example.com",
            status="PROCESSING",
            total_amount_cents=(39900 * 2),  # 2 tai nghe Sony XM5
        )
        item3_1 = OrderItem(order=order3, product=products[4], quantity=2, unit_price_cents=39900)
        products[4].qty_in_stock -= 2

        # Đơn hàng 4
        order4 = Order(
            customer_name="Doãn Duy Lợi",
            customer_email="loi.dd@example.com",
            status="COMPLETED",
            total_amount_cents=(129900 * 1) + (59900 * 1) + (34900 * 1),
        )
        item4_1 = OrderItem(order=order4, product=products[1], quantity=1, unit_price_cents=129900)
        item4_2 = OrderItem(order=order4, product=products[6], quantity=1, unit_price_cents=59900)
        item4_3 = OrderItem(order=order4, product=products[8], quantity=1, unit_price_cents=34900)
        products[1].qty_in_stock -= 1
        products[6].qty_in_stock -= 1
        products[8].qty_in_stock -= 1

        db.session.add_all([order1, order2, order3, order4])
        db.session.add_all([item1_1, item1_2, item2_1, item2_2, item3_1, item4_1, item4_2, item4_3])
        db.session.commit()
        print(f"    ✓ Đã tạo thành công 4 đơn hàng kèm 8 chi tiết mặt hàng (OrderItems).")

        print("\n=== HOÀN TẤT NẠP DỮ LIỆU VÀO dev.db ===")
        print(f"Tổng số sản phẩm trong kho : {Product.query.count()}")
        print(f"Tổng số đơn hàng           : {Order.query.count()}")
        print(f"Tổng số mục hàng trong đơn : {OrderItem.query.count()}")
        print("File database lưu tại      : api_session_8/instance/dev.db")

if __name__ == "__main__":
    seed_database()

