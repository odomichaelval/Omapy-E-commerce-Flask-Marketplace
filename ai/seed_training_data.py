"""
Generates realistic synthetic product listings to bootstrap AI training data.
Inserts via the existing create_product() function, so it uses the same
code path as a real vendor listing (no schema/DB changes needed).

Run once from your project root:
    python -m ai.seed_training_data
"""

import random
import sys
import os

# Allow running as a script from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import create_product, get_user_by_id

# CHANGE THIS to a real user id that exists in your users table
SEED_USER_ID = 14

# Cycle through existing static images so listings aren't broken visually
PLACEHOLDER_IMAGES = [f"/static/img/product-{i}.png" for i in range(1, 19)]

# category: list of (name, description, min_price, max_price)
CATEGORY_DATA = {
    "Accessories": [
        ("Leather Wallet", "Genuine leather bifold wallet with card slots and coin pocket.", 10, 30),
        ("Wireless Earbuds Case", "Protective silicone case for compact wireless earbuds.", 5, 15),
        ("Travel Backpack", "Durable 30L backpack with laptop compartment and rain cover.", 20, 60),
        ("Sunglasses", "UV-protection polarised sunglasses, unisex frame.", 8, 25),
        ("Phone Ring Holder", "Metal pop-out ring holder and kickstand for smartphones.", 3, 8),
        ("Belt", "Adjustable genuine leather belt with metal buckle.", 6, 18),
        ("Laptop Sleeve", "Padded neoprene sleeve fits up to 15-inch laptops.", 8, 20),
        ("Umbrella", "Compact windproof umbrella with auto open/close.", 7, 16),
        ("Watch Strap", "Stainless steel replacement watch strap, 22mm.", 5, 14),
        ("Card Holder", "Slim aluminium RFID-blocking card holder.", 6, 12),
    ],
    "Clothings": [
        ("Denim Jacket", "Classic blue denim jacket, button front, cotton blend.", 15, 45),
        ("Hoodie", "Fleece-lined pullover hoodie with kangaroo pocket.", 10, 30),
        ("Formal Shirt", "Slim-fit long sleeve formal shirt, easy-iron fabric.", 12, 25),
        ("Joggers", "Comfortable cotton joggers with elastic waistband.", 8, 20),
        ("Winter Coat", "Insulated waterproof winter coat with hood.", 30, 90),
        ("Summer Dress", "Floral print midi dress, lightweight fabric.", 10, 35),
        ("Chinos", "Slim-fit chino trousers, multiple colours available.", 12, 28),
        ("Puffer Jacket", "Lightweight packable puffer jacket.", 20, 55),
        ("Cardigan", "Knitted button-front cardigan, soft wool blend.", 10, 24),
        ("Tracksuit Set", "Matching zip-up jacket and joggers tracksuit set.", 15, 40),
    ],
    "Electronics": [
        ("Bluetooth Speaker", "Portable waterproof speaker with 12-hour battery.", 15, 45),
        ("Microwave Oven", "700W compact microwave with 5 power settings.", 30, 70),
        ("Electric Kettle", "1.7L rapid-boil kettle with auto shut-off.", 10, 25),
        ("Toaster", "2-slice toaster with variable browning control.", 8, 20),
        ("Air Fryer", "3.5L digital air fryer, oil-free cooking.", 25, 60),
        ("Vacuum Cleaner", "Bagless cylinder vacuum with HEPA filter.", 40, 100),
        ("Desk Fan", "Oscillating desk fan with 3 speed settings.", 10, 22),
        ("Iron", "Steam iron with non-stick soleplate.", 8, 20),
        ("Television", "43-inch LED smart television, full HD.", 90, 250),
        ("Router", "Dual-band wireless router, easy setup.", 15, 40),
    ],
    "Fashion": [
        ("Designer Handbag", "Faux leather structured handbag with gold hardware.", 20, 60),
        ("Silk Scarf", "Printed silk scarf, lightweight and versatile.", 8, 20),
        ("Statement Necklace", "Chunky gold-tone statement necklace.", 6, 18),
        ("Ankle Boots", "Faux suede ankle boots with block heel.", 15, 40),
        ("Beanie Hat", "Ribbed knit beanie, one size fits all.", 4, 10),
        ("Clutch Bag", "Evening clutch bag with detachable chain strap.", 10, 28),
        ("Sunhat", "Wide-brim woven sunhat, packable.", 6, 14),
        ("Fashion Belt", "Wide waist belt with statement buckle.", 8, 16),
        ("Hoop Earrings", "Gold-plated hoop earrings, hypoallergenic.", 4, 12),
        ("Cross-body Bag", "Compact cross-body bag with adjustable strap.", 10, 26),
    ],
    "Furniture": [
        ("Bookshelf", "5-tier wooden bookshelf, freestanding.", 25, 65),
        ("Office Chair", "Ergonomic mesh-back office chair with armrests.", 30, 90),
        ("Coffee Table", "Rustic wooden coffee table with lower shelf.", 20, 55),
        ("Bed Frame", "Double bed frame, solid wood slats.", 40, 120),
        ("Wardrobe", "2-door wardrobe with hanging rail and shelf.", 45, 130),
        ("TV Stand", "Modern TV stand with cable management.", 20, 50),
        ("Dining Chair", "Set of 2 upholstered dining chairs.", 25, 60),
        ("Bedside Table", "Compact bedside table with one drawer.", 10, 25),
        ("Bean Bag", "Large bean bag chair, machine washable cover.", 15, 35),
        ("Shoe Rack", "5-tier stackable shoe storage rack.", 8, 20),
    ],
    "Gadgets": [
        ("Fitness Tracker", "Waterproof fitness band with heart rate monitor.", 12, 30),
        ("Portable Charger", "10000mAh power bank, dual USB output.", 8, 18),
        ("Smart Plug", "Wi-Fi smart plug, works with voice assistants.", 6, 14),
        ("Webcam", "1080p HD webcam with built-in microphone.", 10, 25),
        ("Wireless Mouse", "Ergonomic wireless mouse, silent click.", 6, 15),
        ("Mechanical Keyboard", "RGB backlit mechanical gaming keyboard.", 20, 55),
        ("Ring Light", "10-inch LED ring light with phone holder.", 8, 20),
        ("Selfie Stick", "Bluetooth selfie stick with tripod stand.", 5, 12),
        ("USB Hub", "7-port USB 3.0 hub, compact design.", 6, 14),
        ("Smart Bulb", "Colour-changing Wi-Fi smart bulb.", 5, 12),
    ],
    "Laptops": [
        ("Dell Inspiron 15", "15.6-inch laptop, 8GB RAM, 256GB SSD.", 150, 350),
        ("Lenovo ThinkPad", "14-inch business laptop, 16GB RAM, 512GB SSD.", 200, 450),
        ("MacBook Air", "13-inch M1 MacBook Air, 8GB RAM, 256GB SSD.", 400, 700),
        ("Acer Aspire", "15.6-inch laptop, 4GB RAM, 128GB SSD, ideal for students.", 80, 200),
        ("Chromebook", "11.6-inch lightweight Chromebook, long battery life.", 60, 150),
        ("Gaming Laptop", "15.6-inch laptop with dedicated graphics, 16GB RAM.", 300, 600),
        ("MacBook Pro", "14-inch MacBook Pro, 16GB RAM, 512GB SSD.", 500, 900),
        ("HP Pavilion", "15.6-inch laptop, 8GB RAM, 512GB SSD.", 180, 380),
        ("Surface Laptop", "13.5-inch touchscreen laptop, 8GB RAM.", 250, 500),
        ("Asus VivoBook", "14-inch slim laptop, 8GB RAM, 256GB SSD.", 150, 320),
    ],
    "Smartphones": [
        ("iPhone 13", "128GB, unlocked, excellent battery health.", 250, 450),
        ("Samsung Galaxy S22", "128GB, unlocked, dual SIM.", 220, 420),
        ("Google Pixel 7", "128GB, unlocked, stock Android.", 200, 380),
        ("iPhone SE", "64GB, unlocked, compact size.", 100, 220),
        ("Samsung Galaxy A54", "128GB, unlocked, great camera.", 150, 280),
        ("OnePlus Nord", "128GB, unlocked, fast charging.", 130, 260),
        ("iPhone 14 Pro", "256GB, unlocked, ProMotion display.", 400, 700),
        ("Xiaomi Redmi Note", "128GB, unlocked, budget friendly.", 80, 160),
        ("Samsung Galaxy Z Flip", "256GB, unlocked, foldable design.", 300, 550),
        ("Google Pixel 6a", "128GB, unlocked, clean Android experience.", 120, 240),
    ],
    "Sports": [
        ("Yoga Mat", "Non-slip 6mm yoga mat with carry strap.", 8, 20),
        ("Dumbbell Set", "Adjustable dumbbell set, 2x10kg.", 20, 45),
        ("Running Shoes", "Lightweight cushioned running shoes.", 20, 50),
        ("Football Boots", "Firm ground football boots, various sizes.", 15, 40),
        ("Tennis Racket", "Lightweight aluminium tennis racket.", 15, 35),
        ("Cycling Helmet", "Adjustable ventilated cycling helmet.", 12, 28),
        ("Resistance Bands", "Set of 5 resistance bands, varying strength.", 6, 14),
        ("Basketball", "Official size indoor/outdoor basketball.", 8, 18),
        ("Skipping Rope", "Adjustable speed skipping rope.", 3, 8),
        ("Gym Bag", "Durable gym holdall with shoe compartment.", 10, 22),
    ],
    "Stationery": [
        ("Notebook Set", "Pack of 3 hardcover ruled notebooks.", 3, 8),
        ("Fountain Pen", "Smooth-writing fountain pen with ink cartridges.", 4, 12),
        ("Desk Organiser", "Multi-compartment desk organiser tray.", 5, 12),
        ("Highlighter Set", "Pack of 6 pastel highlighters.", 2, 6),
        ("Sticky Notes", "Assorted colour sticky notes, 6-pack.", 2, 5),
        ("Calculator", "Scientific calculator, ideal for students.", 6, 15),
        ("Backpack Pencil Case", "Large capacity pencil case with zip pockets.", 3, 8),
        ("Whiteboard", "Small magnetic whiteboard with marker.", 6, 14),
        ("Stapler Set", "Compact stapler with staples included.", 3, 7),
        ("Planner", "Weekly/monthly academic planner.", 4, 10),
    ],
}

CONDITIONS = ["New", "Used"]


def generate_and_insert(per_item_variants=1):
    total_inserted = 0
    img_index = 0

    for category, items in CATEGORY_DATA.items():
        for name, description, min_price, max_price in items:
            for _ in range(per_item_variants):
                condition = random.choice(CONDITIONS)
                price = random.randint(min_price, max_price)
                # Used items priced a bit lower than New, for realism
                if condition == "Used":
                    price = max(1, int(price * random.uniform(0.6, 0.85)))

                image = PLACEHOLDER_IMAGES[img_index % len(PLACEHOLDER_IMAGES)]
                img_index += 1

                create_product(
                    user_id=SEED_USER_ID,
                    product_name=name,
                    product_price=price,
                    product_category=category,
                    product_brand=condition,       # NOTE: this column currently holds condition
                    product_description=description,
                    product_image=image,
                    product_gallery1=image,
                    product_gallery2=image,
                    product_gallery3=image,
                )
                total_inserted += 1

    return total_inserted


if __name__ == "__main__":
    user = get_user_by_id(SEED_USER_ID)
    if not user:
        print(f"ERROR: user_id {SEED_USER_ID} does not exist. "
              f"Edit SEED_USER_ID in this script to a real user id.")
        sys.exit(1)

    confirm = input(
        f"About to insert ~{sum(len(v) for v in CATEGORY_DATA.values())} products "
        f"under user '{user['username']}' (id={SEED_USER_ID}). "
        f"Have you backed up database.db? (yes/no): "
    )
    if confirm.strip().lower() != "yes":
        print("Aborted. Back up database.db first, then re-run.")
        sys.exit(0)

    count = generate_and_insert(per_item_variants=1)
    print(f"Inserted {count} synthetic products across {len(CATEGORY_DATA)} categories.")