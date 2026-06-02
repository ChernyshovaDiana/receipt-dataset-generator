!pip install qrcode[pil]
import os
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import qrcode

class ReceiptGenerator:

    def get_optimal_item_count(self, shop_name, target_height, max_items=20):
        target_height = int(target_height)

        height_configs = {
            "ШЕСТЕРОЧКА": (540, 24),
            "МАГНАТ": (395, 42),
            "АШАНЧИК": (317, 24),
            "АПТЕКА 37.7": (616, 14),
            "РИГЛАЙФ": (616, 14),
            "АЛЛЕНТА": (498, 28),
            "ПЕРЕКРЕСТКИ": (434, 16),
            "ВИЛЛАЗБУКА": (597, 16),
            "ВКУСОЛЕНД": (267, 16),
            "ЗДОРОВУМ": (616, 14),
            "ФАРМТЭК": (616, 14),
            "МОНЕТИКА": (361, 16),
            "СТАРТ": (371, 24),
            "ДВОЙКА": (325, 16),
            "СЕМЬ ДОРОГ": (472, 40),
        }

        config = height_configs.get(shop_name, (500, 25))
        base_height, item_height = config

        best_items = 1
        best_height = base_height + (1 * item_height)

        for num_items in range(2, max_items + 1):
            height = base_height + (num_items * item_height)
            if height <= target_height:
                best_items = num_items
                best_height = height
            else:
                break

        return best_items, best_height

    def __init__(self, output_dir="generated_receipts_dataset"):
        self.base_dir = Path(output_dir).absolute()
        self.images_dir = self.base_dir / "images"
        self.metadata_dir = self.base_dir / "metadata"

        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Папка для чеков: {self.base_dir}")
        self.receipt_counter = 1
        self.smena_counter = random.randint(1, 999)
        self.hotline_number = "8-800-555-35-35"

        self.shops = [
            {"name": "ШЕСТЕРОЧКА", "address": "Москва, ул. Ленина, д. 15", "tax_id": "7705123456", "phone": "84951234567", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Москва, ул. Тверская, д. 22", "tax_id": "7705123457", "phone": "84951234568", "type": "grocery", "tax_system": "УСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Москва, пр-т Мира, д. 88", "tax_id": "7705123458", "phone": "84951234569", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Санкт-Петербург, Невский пр-т, д. 45", "tax_id": "7705123459", "phone": "84951234570", "type": "grocery", "tax_system": "УСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Санкт-Петербург, Московский пр-т, д. 112", "tax_id": "7705123460", "phone": "84951234571", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Казань, ул. Баумана, д. 25", "tax_id": "7705123461", "phone": "84951234572", "type": "grocery", "tax_system": "ЕНВД", "alignment": "center", "features": ["discount_card"]},
            {"name": "ШЕСТЕРОЧКА", "address": "Нижний Новгород, ул. Большая Покровская, д. 33", "tax_id": "7705123462", "phone": "84951234573", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "МАГНАТ", "address": "Казань, ул. Баумана, д. 8", "tax_id": "1658123456", "phone": "88432345678", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "МАГНАТ", "address": "Казань, ул. Кремлевская, д. 12", "tax_id": "1658123457", "phone": "88432345679", "type": "grocery", "tax_system": "УСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "МАГНАТ", "address": "Казань, пр-т Победы, д. 100", "tax_id": "1658123458", "phone": "88432345680", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "МАГНАТ", "address": "Самара, ул. Ленина, д. 55", "tax_id": "1658123459", "phone": "88432345681", "type": "grocery", "tax_system": "ЕНВД", "alignment": "center", "features": ["bonus_card"]},
            {"name": "МАГНАТ", "address": "Самара, Московское шоссе, д. 88", "tax_id": "1658123460", "phone": "88432345682", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "МАГНАТ", "address": "Тольятти, ул. Автостроителей, д. 20", "tax_id": "1658123461", "phone": "88432345683", "type": "grocery", "tax_system": "УСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "АШАНЧИК", "address": "Новосибирск, ул. Кирова, д. 33", "tax_id": "5409123456", "phone": "83833456789", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["club_card"]},
            {"name": "АШАНЧИК", "address": "Новосибирск, Красный пр-т, д. 67", "tax_id": "5409123457", "phone": "83833456790", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["club_card"]},
            {"name": "АШАНЧИК", "address": "Красноярск, пр-т Мира, д. 45", "tax_id": "5409123458", "phone": "83833456791", "type": "grocery", "tax_system": "УСН", "alignment": "center", "features": ["club_card"]},
            {"name": "АШАНЧИК", "address": "Красноярск, ул. Ленина, д. 102", "tax_id": "5409123459", "phone": "83833456792", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["club_card"]},
            {"name": "АШАНЧИК", "address": "Томск, пр-т Кирова, д. 33", "tax_id": "5409123460", "phone": "83833456793", "type": "grocery", "tax_system": "ЕНВД", "alignment": "center", "features": ["club_card"]},
            {"name": "АШАНЧИК", "address": "Томск, ул. Нахимова, д. 12", "tax_id": "5409123461", "phone": "83833456794", "type": "grocery", "tax_system": "ОСН", "alignment": "center", "features": ["club_card"]},
            {"name": "АПТЕКА 37.7", "address": "Москва, ул. Новый Арбат, д. 12", "tax_id": "7704123456", "phone": "84991237890", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "АПТЕКА 37.7", "address": "Москва, ул. Пятницкая, д. 45", "tax_id": "7704123457", "phone": "84991237891", "type": "pharmacy", "tax_system": "УСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "АПТЕКА 37.7", "address": "Санкт-Петербург, ул. Садовая, д. 28", "tax_id": "7704123458", "phone": "84991237892", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "АПТЕКА 37.7", "address": "Екатеринбург, ул. Ленина, д. 55", "tax_id": "7704123459", "phone": "84991237893", "type": "pharmacy", "tax_system": "ЕНВД", "alignment": "center", "features": ["discount_card"]},
            {"name": "АПТЕКА 37.7", "address": "Екатеринбург, ул. Малышева, д. 33", "tax_id": "7704123460", "phone": "84991237894", "type": "pharmacy", "tax_system": "УСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "АПТЕКА 37.7", "address": "Челябинск, ул. Кирова, д. 45", "tax_id": "7704123461", "phone": "84991237895", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["discount_card"]},
            {"name": "РИГЛАЙФ", "address": "Санкт-Петербург, Московский пр-т, д. 101", "tax_id": "7815123456", "phone": "88123456789", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Санкт-Петербург, Невский пр-т, д. 55", "tax_id": "7815123457", "phone": "88123456790", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Краснодар, ул. Красная, д. 88", "tax_id": "7815123458", "phone": "88123456791", "type": "pharmacy", "tax_system": "УСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Краснодар, ул. Ставропольская, д. 45", "tax_id": "7815123459", "phone": "88123456792", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Волгоград, пр-т Ленина, д. 67", "tax_id": "7815123460", "phone": "88123456793", "type": "pharmacy", "tax_system": "ЕНВД", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Волгоград, ул. Мира, д. 12", "tax_id": "7815123461", "phone": "88123456794", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Пермь, ул. Ленина, д. 33", "tax_id": "7815123462", "phone": "88123456795", "type": "pharmacy", "tax_system": "УСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Пермь, Комсомольский пр-т, д. 55", "tax_id": "7815123463", "phone": "88123456796", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Уфа, ул. Ленина, д. 77", "tax_id": "7815123464", "phone": "88123456797", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Уфа, пр-т Октября, д. 44", "tax_id": "7815123465", "phone": "88123456798", "type": "pharmacy", "tax_system": "ЕНВД", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Тамбов, ул. Интернациональная, д. 25", "tax_id": "7815123466", "phone": "88123456799", "type": "pharmacy", "tax_system": "УСН", "alignment": "center", "features": ["bonus_card"]},
            {"name": "РИГЛАЙФ", "address": "Тамбов, ул. Советская, д. 60", "tax_id": "7815123467", "phone": "88123456800", "type": "pharmacy", "tax_system": "ОСН", "alignment": "center", "features": ["bonus_card"]},


            {"name": "АЛЛЕНТА", "address": "Казань, пр-т Буденновский, д. 20", "tax_id": "6144123456", "phone": "88631234567", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": []},
            {"name": "АЛЛЕНТА", "address": "Казань, ул. Большая Садовая, д. 35", "tax_id": "6144123457", "phone": "88631234568", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": []},
            {"name": "АЛЛЕНТА", "address": "Казань, ул. Пушкинская, д. 12", "tax_id": "6144123458", "phone": "88631234569", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": []},
            {"name": "АЛЛЕНТА", "address": "Казань, пр-т Михаила Нагибина, д. 65", "tax_id": "6144123459", "phone": "88631234570", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": []},
            {"name": "ПЕРЕКРЕСТКИ", "address": "Нижний Новгород, ул. Советская, д. 25", "tax_id": "5250123456", "phone": "88315678901", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["hotline"]},
            {"name": "ПЕРЕКРЕСТКИ", "address": "Нижний Новгород, пр. Гагарина, д. 44", "tax_id": "5250123457", "phone": "88315678902", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["hotline"]},
            {"name": "ПЕРЕКРЕСТКИ", "address": "Нижний Новгород, ул. Большая Покровская, д. 18", "tax_id": "5250123458", "phone": "88315678903", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["hotline"]},
            {"name": "ПЕРЕКРЕСТКИ", "address": "Нижний Новгород, ул. Рождественская, д. 30", "tax_id": "5250123459", "phone": "88315678904", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["hotline"]},
            {"name": "ВИЛЛАЗБУКА", "address": "Москва, ул. Тверская, д. 10", "tax_id": "7712345678", "phone": "84997890123", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["bonus_program"]},
            {"name": "ВИЛЛАЗБУКА", "address": "Москва, ул. Арбат, д. 20", "tax_id": "7712345679", "phone": "84997890124", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["bonus_program"]},
            {"name": "ВИЛЛАЗБУКА", "address": "Москва, Ленинградский пр-т, д. 55", "tax_id": "7712345680", "phone": "84997890125", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["bonus_program"]},
            {"name": "ВИЛЛАЗБУКА", "address": "Москва, ул. Пятницкая, д. 8", "tax_id": "7712345681", "phone": "84997890126", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["bonus_program"]},
            {"name": "ВКУСОЛЕНД", "address": "Москва, Кутузовский пр-т, д. 48", "tax_id": "7734123456", "phone": "84991234567", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["club_card"]},
            {"name": "ВКУСОЛЕНД", "address": "Москва, ул. Новый Арбат, д. 15", "tax_id": "7734123457", "phone": "84991234568", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["club_card"]},
            {"name": "ВКУСОЛЕНД", "address": "Москва, пр-т Вернадского, д. 78", "tax_id": "7734123458", "phone": "84991234569", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["club_card"]},
            {"name": "ВКУСОЛЕНД", "address": "Москва, ул. Профсоюзная, д. 123", "tax_id": "7734123459", "phone": "84991234570", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["club_card"]},
            {"name": "ЗДОРОВУМ", "address": "Казань, ул. Кремлевская, д. 25", "tax_id": "1615123456", "phone": "88437890123", "type": "pharmacy", "tax_system": "ЕНВД", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ЗДОРОВУМ", "address": "Казань, ул. Баумана, д. 7", "tax_id": "1615123457", "phone": "88437890124", "type": "pharmacy", "tax_system": "ОСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ЗДОРОВУМ", "address": "Казань, ул. Чистопольская, д. 42", "tax_id": "1615123458", "phone": "88437890125", "type": "pharmacy", "tax_system": "УСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ЗДОРОВУМ", "address": "Казань, пр-т Победы, д. 100", "tax_id": "1615123459", "phone": "88437890126", "type": "pharmacy", "tax_system": "ОСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ФАРМТЭК", "address": "Екатеринбург, ул. Ленина, д. 33", "tax_id": "6678123456", "phone": "83437890125", "type": "pharmacy", "tax_system": "УСН", "alignment": "compact", "features": ["bonus_card"]},
            {"name": "ФАРМТЭК", "address": "Екатеринбург, ул. Малышева, д. 51", "tax_id": "6678123457", "phone": "83437890126", "type": "pharmacy", "tax_system": "ОСН", "alignment": "compact", "features": ["bonus_card"]},
            {"name": "ФАРМТЭК", "address": "Екатеринбург, ул. Куйбышева, д. 89", "tax_id": "6678123458", "phone": "83437890127", "type": "pharmacy", "tax_system": "ЕНВД", "alignment": "compact", "features": ["bonus_card"]},
            {"name": "ФАРМТЭК", "address": "Екатеринбург, пр-т Ленина, д. 24", "tax_id": "6678123459", "phone": "83437890128", "type": "pharmacy", "tax_system": "ОСН", "alignment": "compact", "features": ["bonus_card"]},
            {"name": "МОНЕТИКА", "address": "Самара, ул. Советская, д. 67", "tax_id": "5409123458", "phone": "83833456791", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": []},
            {"name": "МОНЕТИКА", "address": "Новосибирск, Красный пр-т, д. 112", "tax_id": "5409123459", "phone": "83833456792", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": []},
            {"name": "МОНЕТИКА", "address": "Новосибирск, ул. Гоголя, д. 45", "tax_id": "5409123460", "phone": "83833456793", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": []},
            {"name": "МОНЕТИКА", "address": "Новосибирск, ул. Кирова, д. 88", "tax_id": "5409123461", "phone": "83833456794", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": []},
            {"name": "СТАРТ", "address": "Санкт-Петербург, Невский пр-т, д. 88", "tax_id": "7815123458", "phone": "88123456791", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["sport_bonus"]},
            {"name": "СТАРТ", "address": "Санкт-Петербург, ул. Садовая, д. 33", "tax_id": "7815123459", "phone": "88123456792", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["sport_bonus"]},
            {"name": "СТАРТ", "address": "Санкт-Петербург, Лиговский пр-т, д. 144", "tax_id": "7815123460", "phone": "88123456793", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["sport_bonus"]},
            {"name": "СТАРТ", "address": "Санкт-Петербург, ул. Восстания, д. 22", "tax_id": "7815123461", "phone": "88123456794", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["sport_bonus"]},
            {"name": "ДВОЙКА", "address": "Москва, ул. Люблинская, д. 55", "tax_id": "7709123456", "phone": "84951234999", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ДВОЙКА", "address": "Москва, ул. Шипиловская, д. 40", "tax_id": "7709123457", "phone": "84951235000", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ДВОЙКА", "address": "Москва, Каширское шоссе, д. 55", "tax_id": "7709123458", "phone": "84951235001", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["discount_card"]},
            {"name": "ДВОЙКА", "address": "Москва, ул. Миклухо-Маклая, д. 33", "tax_id": "7709123459", "phone": "84951235002", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["discount_card"]},
            {"name": "СЕМЬ ДОРОГ", "address": "Санкт-Петербург, ул. Ленсовета, д. 67", "tax_id": "7816123456", "phone": "88125678901", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["family_card"]},
            {"name": "СЕМЬ ДОРОГ", "address": "Санкт-Петербург, ул. Бухарестская, д. 101", "tax_id": "7816123457", "phone": "88125678902", "type": "grocery", "tax_system": "УСН", "alignment": "compact", "features": ["family_card"]},
            {"name": "СЕМЬ ДОРОГ", "address": "Санкт-Петербург, пр-т Ветеранов, д. 78", "tax_id": "7816123458", "phone": "88125678903", "type": "grocery", "tax_system": "ОСН", "alignment": "compact", "features": ["family_card"]},
            {"name": "СЕМЬ ДОРОГ", "address": "Санкт-Петербург, ул. Дыбенко, д. 23", "tax_id": "7816123459", "phone": "88125678904", "type": "grocery", "tax_system": "ЕНВД", "alignment": "compact", "features": ["family_card"]}
        ]

        self.grocery_products = [
            {"name": "МОЛОКО 2.5% 1Л", "price_range": (65, 95), "vat": "10%"},
            {"name": "МОЛОКО 3.2% 0,9Л", "price_range": (55, 80), "vat": "10%"},
            {"name": "МОЛОКО ТОПЛЁНОЕ 4%", "price_range": (90, 130), "vat": "10%"},
            {"name": "МОЛОКО БЕЗЛАКТ. 1Л", "price_range": (120, 170), "vat": "10%"},
            {"name": "КЕФИР 1% 1Л", "price_range": (65, 95), "vat": "10%"},
            {"name": "КЕФИР 2.5% 0,5Л", "price_range": (40, 60), "vat": "10%"},
            {"name": "КЕФИР БИО 3.2% 1Л", "price_range": (80, 120), "vat": "10%"},
            {"name": "РЯЖЕНКА 4% 0,9Л", "price_range": (70, 110), "vat": "10%"},
            {"name": "РЯЖЕНКА 2.5% 0,5Л", "price_range": (45, 65), "vat": "10%"},
            {"name": "ЙОГУРТ ПИТЬЕВОЙ КЛУБ", "price_range": (45, 70), "vat": "10%"},
            {"name": "ЙОГУРТ ПИТЬЕВОЙ ПЕРС", "price_range": (45, 70), "vat": "10%"},
            {"name": "ЙОГУРТ ГРЕЧЕСКИЙ 2%", "price_range": (55, 85), "vat": "10%"},
            {"name": "ЙОГУРТ ТЕРМОСТАТНЫЙ", "price_range": (70, 110), "vat": "10%"},
            {"name": "ТВОРОГ 5% 200Г", "price_range": (80, 120), "vat": "10%"},
            {"name": "ТВОРОГ 9% 400Г", "price_range": (140, 200), "vat": "10%"},
            {"name": "ТВОРОГ ОБЕЗЖИР. 180Г", "price_range": (65, 95), "vat": "10%"},
            {"name": "ТВОРОГ ЗЕРНИСТЫЙ 4%", "price_range": (110, 160), "vat": "10%"},
            {"name": "СМЕТАНА 15% 200Г", "price_range": (50, 80), "vat": "10%"},
            {"name": "СМЕТАНА 20% 300Г", "price_range": (80, 120), "vat": "10%"},
            {"name": "СМЕТАНА ДЛЯ СУПА 10%", "price_range": (40, 60), "vat": "10%"},
            {"name": "СЫР РОССИЙСКИЙ 300Г", "price_range": (200, 290), "vat": "10%"},
            {"name": "СЫР ГАУДА 200Г", "price_range": (180, 260), "vat": "10%"},
            {"name": "СЫР ПЛАВЛЕНЫЙ ДРУЖБА", "price_range": (35, 55), "vat": "10%"},
            {"name": "СЫР МОЦАРЕЛЛА 125Г", "price_range": (120, 180), "vat": "10%"},
            {"name": "МАСЛО СЛИВОЧН. 72,5%", "price_range": (120, 170), "vat": "10%"},
            {"name": "МАСЛО СЛИВОЧН. 82,5%", "price_range": (160, 220), "vat": "10%"},
            {"name": "МАСЛО ТОПЛЁНОЕ 99%", "price_range": (180, 250), "vat": "10%"},
            {"name": "ПРОСТОКВАША 1Л", "price_range": (60, 90), "vat": "10%"},
            {"name": "АЦИДОФИЛИН 1Л", "price_range": (80, 120), "vat": "10%"},
            {"name": "ТАН (АЙРАН) 0,5Л", "price_range": (55, 85), "vat": "10%"},
            {"name": "СНЕЖОК 0,5Л", "price_range": (60, 90), "vat": "10%"},
            {"name": "ВАРЕНЕЦ 0,9Л", "price_range": (75, 110), "vat": "10%"},
            {"name": "СЛИВКИ 10% 250МЛ", "price_range": (55, 85), "vat": "10%"},
            {"name": "СЛИВКИ 33% 250МЛ", "price_range": (110, 160), "vat": "10%"},
            {"name": "ТВОР.МАССА С ИЗЮМ.", "price_range": (90, 140), "vat": "20%"},

            {"name": "ГОВЯДИНА ВЫРЕЗКА 1КГ", "price_range": (550, 850), "vat": "10%"},
            {"name": "ГОВЯДИНА ДЛЯ ТУШЕНИЯ", "price_range": (450, 650), "vat": "10%"},
            {"name": "СВИНИНА ШЕЯ 1КГ", "price_range": (350, 520), "vat": "10%"},
            {"name": "СВИНИНА КАРБОНАД 1КГ", "price_range": (400, 580), "vat": "10%"},
            {"name": "КУРИНОЕ ФИЛЕ 1КГ", "price_range": (280, 420), "vat": "10%"},
            {"name": "КУРИНЫЕ БЁДРА 1КГ", "price_range": (180, 280), "vat": "10%"},
            {"name": "КУРИНЫЕ КРЫЛЬЯ 1КГ", "price_range": (150, 240), "vat": "10%"},
            {"name": "КУРИНЫЙ ФАРШ 400Г", "price_range": (120, 180), "vat": "10%"},
            {"name": "ИНДЕЙКА ФИЛЕ 1КГ", "price_range": (400, 600), "vat": "10%"},
            {"name": "КОЛБАСА ДОКТОРСКАЯ", "price_range": (250, 380), "vat": "20%"},
            {"name": "КОЛБАСА СЕРВЕЛАТ 400Г", "price_range": (320, 520), "vat": "20%"},
            {"name": "КОЛБАСА КРАКОВСКАЯ", "price_range": (300, 480), "vat": "20%"},
            {"name": "СОСИСКИ ГОЛЛАНДСКИЕ", "price_range": (140, 210), "vat": "20%"},
            {"name": "САРДЕЛЬКИ КЛАССИЧ.", "price_range": (130, 190), "vat": "20%"},
            {"name": "ВЕТЧИНА ИЗ ИНДЕЙКИ", "price_range": (100, 150), "vat": "20%"},
            {"name": "САЛО СОЛЁНОЕ 300Г", "price_range": (150, 250), "vat": "10%"},
            {"name": "ПЕЛЬМЕНИ СВ/ГОВ 800Г", "price_range": (200, 320), "vat": "10%"},
            {"name": "ХИНКАЛИ С ГОВЯДИНОЙ", "price_range": (280, 420), "vat": "10%"},
            {"name": "КОТЛЕТЫ ДОМАШНИЕ", "price_range": (250, 380), "vat": "10%"},
            {"name": "ГОРБУША СВЕЖЕМОР.", "price_range": (350, 550), "vat": "10%"},
            {"name": "СЁМГА ОХЛАЖДЁННАЯ", "price_range": (1200, 1800), "vat": "10%"},
            {"name": "МИНТАЙ 1КГ", "price_range": (120, 190), "vat": "10%"},
            {"name": "СЕЛЬДЬ СЛАБОСОЛ.", "price_range": (110, 170), "vat": "10%"},
            {"name": "КРЕВЕТКИ КОКТ. 400Г", "price_range": (350, 550), "vat": "20%"},
            {"name": "КАЛЬМАРЫ 500Г", "price_range": (250, 390), "vat": "20%"},
            {"name": "КРАБОВЫЕ ПАЛОЧКИ", "price_range": (70, 120), "vat": "20%"},
            {"name": "ПЕЧЕНЬ КУРИНАЯ 500Г", "price_range": (90, 140), "vat": "10%"},
            {"name": "ПЕЧЕНЬ ГОВЯЖЬЯ 500Г", "price_range": (160, 250), "vat": "10%"},

            {"name": "ГРЕЧКА ЯДРИЦА 800Г", "price_range": (70, 120), "vat": "10%"},
            {"name": "ГРЕЧКА ПРОДЕЛ 900Г", "price_range": (60, 100), "vat": "10%"},
            {"name": "РИС КРУГЛЫЙ 800Г", "price_range": (65, 105), "vat": "10%"},
            {"name": "РИС БАСМАТИ 500Г", "price_range": (90, 150), "vat": "10%"},
            {"name": "ПШЕНО 800Г", "price_range": (45, 75), "vat": "10%"},
            {"name": "ОВСЯНЫЕ ХЛОПЬЯ ГЕРК.", "price_range": (50, 85), "vat": "10%"},
            {"name": "МАННАЯ КРУПА 500Г", "price_range": (35, 60), "vat": "10%"},
            {"name": "МАКАРОНЫ СПИРАЛИ", "price_range": (45, 75), "vat": "10%"},
            {"name": "МАКАРОНЫ РОЖКИ 400Г", "price_range": (40, 70), "vat": "10%"},
            {"name": "МАКАРОНЫ ПЕРЬЯ 400Г", "price_range": (40, 70), "vat": "10%"},
            {"name": "ВЕРМИШЕЛЬ БЫСТР.", "price_range": (35, 60), "vat": "10%"},
            {"name": "МУКА ПШЕН. В/С 1КГ", "price_range": (45, 75), "vat": "10%"},
            {"name": "САХАР ПЕСОК 1КГ", "price_range": (55, 85), "vat": "10%"},
            {"name": "СОЛЬ ЭКСТРА 1КГ", "price_range": (15, 30), "vat": "10%"},
            {"name": "СОДА ПИЩЕВАЯ 100Г", "price_range": (10, 25), "vat": "10%"},
            {"name": "МАСЛО ПОДСОЛНЕЧН. 1Л", "price_range": (85, 140), "vat": "10%"},
            {"name": "МАСЛО ОЛИВКОВОЕ 0,5Л", "price_range": (350, 550), "vat": "10%"},
            {"name": "ТУШЁНКА ГОВЯЖЬЯ", "price_range": (180, 280), "vat": "20%"},
            {"name": "СГУЩЁНКА С САХАРОМ", "price_range": (90, 140), "vat": "10%"},
            {"name": "ГОРОШЕК ЗЕЛЁНЫЙ", "price_range": (60, 100), "vat": "10%"},
            {"name": "КУКУРУЗА КОНСЕРВ.", "price_range": (50, 85), "vat": "10%"},
            {"name": "ШПРОТЫ В МАСЛЕ", "price_range": (100, 170), "vat": "20%"},
            {"name": "ПАШТЕТ КУРИНЫЙ 100Г", "price_range": (35, 60), "vat": "20%"},
            {"name": "МАЙОНЕЗ 400Г", "price_range": (60, 100), "vat": "20%"},
            {"name": "КЕТЧУП 300Г", "price_range": (70, 120), "vat": "20%"},
            {"name": "СОЕВЫЙ СОУС 200МЛ", "price_range": (80, 130), "vat": "20%"},
            {"name": "СУХАРИ ПАНИРОВОЧ.", "price_range": (30, 50), "vat": "20%"},
            {"name": "ПЮРЕ КАРТОФ. БЫСТР.", "price_range": (60, 100), "vat": "10%"},

            {"name": "ХЛЕБ БОРОДИНСКИЙ", "price_range": (50, 85), "vat": "10%"},
            {"name": "ХЛЕБ БЕЛЫЙ ФОРМОВОЙ", "price_range": (35, 60), "vat": "10%"},
            {"name": "БАТОН НАРЕЗНОЙ 300Г", "price_range": (30, 50), "vat": "10%"},
            {"name": "РОЖОК С ПОВИДЛОМ", "price_range": (25, 45), "vat": "20%"},
            {"name": "БУЛКА С МАКОМ", "price_range": (30, 50), "vat": "20%"},
            {"name": "ЛАВАШ ТОНКИЙ 200Г", "price_range": (40, 65), "vat": "10%"},
            {"name": "ПЕЧЕНЬЕ ЮБИЛЕЙНОЕ", "price_range": (45, 75), "vat": "20%"},
            {"name": "ПЕЧЕНЬЕ ОВСЯНОЕ", "price_range": (55, 90), "vat": "20%"},
            {"name": "ПРЯНИКИ ТУЛЬСКИЕ", "price_range": (70, 115), "vat": "20%"},
            {"name": "КРЕКЕР С СОЛЬЮ", "price_range": (35, 60), "vat": "20%"},
            {"name": "ВАФЛИ ШОКОЛАДНЫЕ", "price_range": (60, 100), "vat": "20%"},
            {"name": "КЕКС МРАМОРНЫЙ", "price_range": (80, 130), "vat": "20%"},
            {"name": "ШОКОЛАД МОЛОЧНЫЙ", "price_range": (75, 125), "vat": "20%"},
            {"name": "ШОКОЛАД ГОРЬКИЙ 75%", "price_range": (90, 150), "vat": "20%"},
            {"name": "КОНФЕТЫ КОРОВКА", "price_range": (70, 110), "vat": "20%"},
            {"name": "КАРАМЕЛЬ ЛЕДЕНЦ.", "price_range": (50, 85), "vat": "20%"},
            {"name": "ХАЛВА ПОДСОЛНЕЧНАЯ", "price_range": (80, 130), "vat": "20%"},
            {"name": "ЗЕФИР ВАНИЛЬНЫЙ", "price_range": (80, 130), "vat": "20%"},
            {"name": "МОРОЖЕНОЕ ПЛОМБИР", "price_range": (55, 95), "vat": "20%"},
            {"name": "ЭСКИМО", "price_range": (40, 70), "vat": "20%"},

            {"name": "КАРТОФЕЛЬ МОЛОДОЙ", "price_range": (40, 80), "vat": "10%"},
            {"name": "КАРТОФЕЛЬ СТАРЫЙ", "price_range": (30, 55), "vat": "10%"},
            {"name": "ЛУК РЕПЧАТЫЙ 1КГ", "price_range": (30, 55), "vat": "10%"},
            {"name": "МОРКОВЬ 1КГ", "price_range": (35, 65), "vat": "10%"},
            {"name": "КАПУСТА БЕЛОКОЧ.", "price_range": (25, 50), "vat": "10%"},
            {"name": "СВЁКЛА 1КГ", "price_range": (35, 60), "vat": "10%"},
            {"name": "ЧЕСНОК 200Г", "price_range": (50, 100), "vat": "10%"},
            {"name": "ПОМИДОРЫ РОЗОВЫЕ", "price_range": (180, 280), "vat": "10%"},
            {"name": "ОГУРЦЫ", "price_range": (130, 200), "vat": "10%"},
            {"name": "ПЕРЕЦ БОЛГАРСКИЙ", "price_range": (150, 240), "vat": "10%"},
            {"name": "АВОКАДО ШТ", "price_range": (110, 180), "vat": "10%"},
            {"name": "ЛИМОН ШТ", "price_range": (40, 75), "vat": "10%"},
            {"name": "ЯБЛОКИ СЕМЕРЕНКО", "price_range": (75, 125), "vat": "10%"},
            {"name": "АПЕЛЬСИНЫ 1КГ", "price_range": (110, 180), "vat": "10%"},
            {"name": "МАНДАРИНЫ 1КГ", "price_range": (120, 190), "vat": "10%"},
            {"name": "БАНАНЫ 1КГ", "price_range": (80, 130), "vat": "10%"},
            {"name": "ВИНОГРАД КИШМИШ", "price_range": (110, 180), "vat": "10%"},
            {"name": "КЛУБНИКА 500Г", "price_range": (200, 350), "vat": "10%"},
            {"name": "УКРОП ПУЧОК", "price_range": (25, 45), "vat": "10%"},
            {"name": "ПЕТРУШКА ПУЧОК", "price_range": (25, 45), "vat": "10%"},
            {"name": "САЛАТ АЙСБЕРГ", "price_range": (60, 100), "vat": "10%"},
            {"name": "РУККОЛА 100Г", "price_range": (80, 140), "vat": "10%"},

            {"name": "ВОДА ПИТЬЕВАЯ 5Л", "price_range": (40, 70), "vat": "10%"},
            {"name": "ВОДА ГАЗИР. 1,5Л", "price_range": (30, 55), "vat": "20%"},
            {"name": "ВОДА МИНЕР. ГАЗ. 1Л", "price_range": (40, 70), "vat": "10%"},
            {"name": "КОКА-КОЛА 0,5Л", "price_range": (45, 75), "vat": "20%"},
            {"name": "КОКА-КОЛА 1,5Л", "price_range": (80, 130), "vat": "20%"},
            {"name": "ПЕПСИ 0,5Л", "price_range": (45, 75), "vat": "20%"},
            {"name": "ФАНТА АПЕЛЬСИН", "price_range": (45, 75), "vat": "20%"},
            {"name": "СПРАЙТ 0,5Л", "price_range": (45, 70), "vat": "20%"},
            {"name": "ЛИМОНАД ДЮШЕС", "price_range": (35, 55), "vat": "20%"},
            {"name": "МОРС КЛЮКВЕННЫЙ", "price_range": (70, 110), "vat": "20%"},
            {"name": "СОК ЯБЛОЧНЫЙ 1Л", "price_range": (65, 105), "vat": "20%"},
            {"name": "СОК АПЕЛЬСИН. 1Л", "price_range": (80, 130), "vat": "20%"},
            {"name": "СОК ТОМАТНЫЙ 1Л", "price_range": (70, 115), "vat": "20%"},
            {"name": "КВАС ЖИВОЙ 1,5Л", "price_range": (60, 100), "vat": "20%"},
            {"name": "ЭНЕРГЕТИК ПУРШАТ", "price_range": (70, 120), "vat": "20%"},
            {"name": "ПИВО СВЕТЛОЕ 0,5Л", "price_range": (60, 100), "vat": "20%"},
            {"name": "ПИВО НЕФИЛЬТР.", "price_range": (90, 150), "vat": "20%"},

            {"name": "ЧИПСЫ ЛЕЙС ПАПРИКА", "price_range": (130, 210), "vat": "20%"},
            {"name": "ЧИПСЫ ПРОКЛЫЕ", "price_range": (80, 130), "vat": "20%"},
            {"name": "СУХАРИКИ КИРИЕШКИ", "price_range": (35, 60), "vat": "20%"},
            {"name": "КОЗИНАКИ ПОДСОЛН.", "price_range": (50, 85), "vat": "20%"},
            {"name": "ПОПКОРН СЛАДКИЙ", "price_range": (60, 100), "vat": "20%"},
            {"name": "МАРМЕЛАД ЖЕВАТ.", "price_range": (70, 120), "vat": "20%"},
            {"name": "ЧАЙ ЧЁРНЫЙ ЛИСТ.", "price_range": (60, 100), "vat": "10%"},
            {"name": "ЧАЙ ЗЕЛЁНЫЙ 100Г", "price_range": (70, 120), "vat": "10%"},
            {"name": "ЧАЙ В ПАКЕТИКАХ", "price_range": (60, 100), "vat": "10%"},
            {"name": "КОФЕ РАСТВОРИМЫЙ", "price_range": (250, 400), "vat": "10%"},
            {"name": "КОФЕ 3 В 1", "price_range": (80, 130), "vat": "10%"},
            {"name": "СЕМЕЧКИ ЖАРЕНЫЕ", "price_range": (60, 100), "vat": "20%"},
            {"name": "ФИСТАШКИ СОЛЁНЫЕ", "price_range": (200, 320), "vat": "20%"},
            {"name": "АРАХИС ЖАРЕНЫЙ", "price_range": (100, 160), "vat": "20%"},
            {"name": "МИКС ОРЕХОВЫЙ", "price_range": (180, 280), "vat": "20%"},
            {"name": "КУРАГА 200Г", "price_range": (130, 210), "vat": "10%"},
            {"name": "МЕД ЦВЕТОЧНЫЙ", "price_range": (180, 280), "vat": "10%"},

            {"name": "СТИР. ПОРОШОК АВТ.", "price_range": (280, 450), "vat": "20%"},
            {"name": "ГЕЛЬ ДЛЯ СТИРКИ", "price_range": (400, 650), "vat": "20%"},
            {"name": "КОНДИЦ. ДЛЯ БЕЛЬЯ", "price_range": (180, 280), "vat": "20%"},
            {"name": "МЫЛО ХОЗЯЙСТВЕН.", "price_range": (20, 40), "vat": "20%"},
            {"name": "САЛФЕТКИ ВЛАЖНЫЕ", "price_range": (50, 85), "vat": "20%"},
            {"name": "БУМАГА ТУАЛЕТНАЯ", "price_range": (50, 90), "vat": "20%"},
            {"name": "СР-ВО ДЛЯ ПОСУДЫ", "price_range": (80, 130), "vat": "20%"},
            {"name": "ШАМПУНЬ 400МЛ", "price_range": (180, 300), "vat": "20%"},
            {"name": "ГЕЛЬ ДЛЯ ДУША", "price_range": (140, 230), "vat": "20%"},
            {"name": "ЗУБНАЯ ПАСТА", "price_range": (80, 140), "vat": "20%"},
            {"name": "ЗУБНАЯ ЩЁТКА", "price_range": (70, 150), "vat": "20%"},
            {"name": "КОРМ ДЛЯ КОШЕК", "price_range": (100, 170), "vat": "20%"},
            {"name": "КОРМ ДЛЯ СОБАК", "price_range": (150, 250), "vat": "20%"},
        ]

        self.pharmacy_products = [
            {"name": "АСПИРИН 500МГ №10", "price_range": (50, 100), "vat": "10%"},
            {"name": "АСПИРИН КАРДИО №28", "price_range": (120, 200), "vat": "10%"},
            {"name": "ПАРАЦЕТАМОЛ 500МГ №20", "price_range": (30, 60), "vat": "10%"},
            {"name": "НО-ШПА 40МГ №24", "price_range": (150, 250), "vat": "10%"},
            {"name": "ИБУПРОФЕН 200МГ №20", "price_range": (50, 90), "vat": "10%"},
            {"name": "НИМЕСУЛИД 100МГ №20", "price_range": (80, 140), "vat": "10%"},
            {"name": "ЦИТРАМОН №10", "price_range": (20, 45), "vat": "10%"},
            {"name": "СУПРАСТИН 25МГ №20", "price_range": (120, 200), "vat": "10%"},
            {"name": "ЛОРАТАДИН 10МГ №10", "price_range": (40, 80), "vat": "10%"},
            {"name": "АМБРОКСОЛ 30МГ №20", "price_range": (80, 140), "vat": "10%"},
            {"name": "ЛАЗОЛВАН 30МГ №20", "price_range": (180, 300), "vat": "10%"},
            {"name": "АЦЦ 200МГ №20", "price_range": (150, 250), "vat": "10%"},
            {"name": "МЕЗИМ 10000 №20", "price_range": (150, 250), "vat": "10%"},
            {"name": "КРЕОН 10000 №20", "price_range": (250, 400), "vat": "10%"},
            {"name": "ЛИНЕКС №16", "price_range": (250, 400), "vat": "10%"},
            {"name": "ЭНТЕРОСГЕЛЬ 225Г", "price_range": (300, 500), "vat": "10%"},
            {"name": "АКТ. УГОЛЬ №50", "price_range": (20, 40), "vat": "10%"},
            {"name": "КОРВАЛОЛ 25МЛ", "price_range": (50, 90), "vat": "10%"},
            {"name": "ВАЛИДОЛ №10", "price_range": (30, 60), "vat": "10%"},
            {"name": "ГЛИЦИН 100МГ №50", "price_range": (40, 80), "vat": "10%"},
            {"name": "АФОБАЗОЛ 10МГ №60", "price_range": (350, 550), "vat": "10%"},
            {"name": "ФЕНИБУТ 250МГ №20", "price_range": (150, 280), "vat": "10%"},
            {"name": "КЕТОРОЛ 10МГ №20", "price_range": (70, 120), "vat": "10%"},

            {"name": "КОМПЛИВИТ №60", "price_range": (200, 350), "vat": "10%"},
            {"name": "КОМПЛИВИТ АКТИВ №60", "price_range": (250, 400), "vat": "10%"},
            {"name": "КОМПЛИВИТ КАЛЬЦИЙ D3", "price_range": (220, 380), "vat": "10%"},
            {"name": "ВИТРУМ №60", "price_range": (500, 800), "vat": "10%"},
            {"name": "СУПРАДИН №30", "price_range": (350, 550), "vat": "10%"},
            {"name": "АЛФАВИТ КЛАССИК №60", "price_range": (250, 400), "vat": "10%"},
            {"name": "АЛФАВИТ ПРОСТУДА №60", "price_range": (300, 480), "vat": "10%"},
            {"name": "ВИТАМИН С 500МГ №20", "price_range": (50, 100), "vat": "10%"},
            {"name": "ВИТАМИН Д3 2000МЕ", "price_range": (300, 500), "vat": "10%"},
            {"name": "ВИТАМИН Е 400МГ №30", "price_range": (150, 250), "vat": "10%"},
            {"name": "МАГНИЙ В6 №50", "price_range": (200, 350), "vat": "10%"},
            {"name": "КАЛЬЦИЙ D3 №60", "price_range": (150, 280), "vat": "10%"},
            {"name": "ОМЕГА-3 №100", "price_range": (300, 500), "vat": "10%"},
            {"name": "РЫБИЙ ЖИР №100", "price_range": (150, 250), "vat": "10%"},
            {"name": "ЛЕЦИТИН №120", "price_range": (250, 420), "vat": "10%"},
            {"name": "КАРДИОМАГНИЛ №30", "price_range": (150, 260), "vat": "10%"},
            {"name": "ТЕРАФЛЮ №10", "price_range": (250, 400), "vat": "10%"},
            {"name": "КОЛДАКТ №10", "price_range": (180, 300), "vat": "10%"},
            {"name": "АНТИГРИППИН №10", "price_range": (200, 350), "vat": "10%"},
            {"name": "ИММУНАЛ 50МЛ", "price_range": (200, 350), "vat": "10%"},

            {"name": "БИНТ СТЕР. 5М", "price_range": (30, 60), "vat": "10%"},
            {"name": "БИНТ СТЕР. 10М", "price_range": (50, 90), "vat": "10%"},
            {"name": "БИНТ НЕСТЕР. 7М", "price_range": (25, 50), "vat": "10%"},
            {"name": "БИНТ ЭЛАСТИЧ. 2М", "price_range": (100, 180), "vat": "20%"},
            {"name": "ЛЕЙКОПЛАСТЫРЬ 2СМ", "price_range": (40, 80), "vat": "10%"},
            {"name": "ЛЕЙКОПЛАСТЫРЬ БАКТ.", "price_range": (50, 100), "vat": "10%"},
            {"name": "МАРЛЯ МЕД. 1М", "price_range": (20, 40), "vat": "10%"},
            {"name": "ВАТА 100Г", "price_range": (40, 80), "vat": "10%"},
            {"name": "МАСКА МЕД. 10ШТ", "price_range": (50, 100), "vat": "10%"},
            {"name": "ПЕРЧАТКИ ЛАТЕКСНЫЕ", "price_range": (400, 700), "vat": "20%"},
            {"name": "БАХИЛЫ 100ПАР", "price_range": (200, 400), "vat": "20%"},
            {"name": "ЖГУТ КРОВООСТ.", "price_range": (100, 200), "vat": "10%"},

            {"name": "ТОНОМЕТР МЕХАН.", "price_range": (1000, 2000), "vat": "20%"},
            {"name": "ТОНОМЕТР АВТОМ.", "price_range": (2500, 4500), "vat": "20%"},
            {"name": "ТЕРМОМЕТР ЭЛЕКТР.", "price_range": (200, 500), "vat": "20%"},
            {"name": "ТЕРМОМЕТР ИК", "price_range": (1500, 3500), "vat": "20%"},
            {"name": "ИНГАЛЯТОР", "price_range": (2500, 5000), "vat": "20%"},
            {"name": "ПУЛЬСОКСИМЕТР", "price_range": (1500, 3000), "vat": "20%"},
            {"name": "ГЛЮКОМЕТР", "price_range": (1200, 2500), "vat": "20%"},
            {"name": "ТЕСТ-ПОЛОСКИ 50ШТ", "price_range": (800, 1500), "vat": "10%"},

            {"name": "ДЕТСКИЙ КРЕМ 50МЛ", "price_range": (60, 120), "vat": "20%"},
            {"name": "БЕПАНТЕН 30Г", "price_range": (350, 600), "vat": "20%"},
            {"name": "СУДОКРЕМ 60Г", "price_range": (200, 350), "vat": "20%"},
            {"name": "ПАНТЕНОЛ 130МЛ", "price_range": (250, 450), "vat": "20%"},
            {"name": "МИРАМИСТИН 50МЛ", "price_range": (200, 350), "vat": "10%"},
            {"name": "ХЛОРГЕКСИДИН 100МЛ", "price_range": (20, 40), "vat": "10%"},
            {"name": "ПЕРЕКИСЬ ВОДОРОДА", "price_range": (20, 40), "vat": "10%"},
            {"name": "ЗЕЛЁНКА 25МЛ", "price_range": (20, 40), "vat": "10%"},
            {"name": "ЙОД 25МЛ", "price_range": (20, 40), "vat": "10%"},
            {"name": "МАЗЬ ВИШНЕВСКОГО", "price_range": (40, 80), "vat": "10%"},
            {"name": "ДИКЛОФЕНАК 30Г", "price_range": (50, 100), "vat": "10%"},
            {"name": "НОСКИ КОМПРЕСС. 1КЛ", "price_range": (600, 1200), "vat": "20%"},
            {"name": "СТЕЛЬКИ ОРТОПЕД.", "price_range": (200, 500), "vat": "20%"},
            {"name": "БАНДАЖ КОЛЕННЫЙ", "price_range": (700, 1500), "vat": "20%"},
        ]

        self.russian_names = [
    "Иванова А.С.", "Петрова М.И.", "Сидорова В.П.", "Козлова Е.В.",
    "Смирнова О.Н.", "Кузнецова А.А.", "Попова Н.В.", "Васильева И.П.",
    "Павлова Л.С.", "Соколова Р.В.", "Михайлова Т.Д.", "Федорова Е.Н.",
    "Морозова А.В.", "Волкова И.С.", "Алексеева О.В.", "Лебедева М.А.",
    "Семенова Е.Ю.", "Егорова Н.Д.", "Григорьева А.И.", "Николаева О.П.",
    "Новикова А.В.", "Андреева М.О.", "Потапова Н.А.", "Романенко С.В.",
    "Борисова Е.В.", "Королева А.А.", "Тимофеева О.С.", "Кудрявцева М.Д.",
    "Белова Н.И.", "Гаврилова Л.В.", "Денисова А.Ю.", "Ермакова О.А.",
    "Захарова Е.П.", "Зуева М.С.", "Ильина Н.В.", "Киселева А.Р.",
    "Комарова О.В.", "Крылова Е.Н.", "Ларина М.А.", "Медведева Т.С.",
    "Никитина А.В.", "Орлова О.И.", "Полякова Е.В.", "Романова А.С.",
    "Сергеева М.В.", "Тарасова О.Н.", "Ушакова Е.А.", "Фролова А.В.",
    "Цветкова О.М.", "Чернова Е.С.", "Ширяева М.П.", "Щербакова Н.В.",
    "Яковлева А.А.", "Блинова О.В.", "Власова Е.Д.", "Горбунова М.И.",
    "Дроздова Т.В.", "Евдокимова А.Н.", "Журавлева О.П.", "Зайцева Е.В.",
    "Карпова М.С.", "Лобанова Н.А.", "Максимова А.В.", "Назарова О.Ю.",
    "Овчинникова Е.А.", "Панина М.В.", "Рожкова Т.Н.", "Савельева А.С.",
    "Тихонова О.В.", "Филиппова Е.М.", "Харитонова Н.А.", "Чистякова А.В.",
    "Шестакова О.Д.", "Юдина Е.В.", "Агафонова М.А.", "Беляева Т.С.",
    "Васина А.И.", "Герасимова О.В.", "Данилова Е.Н.", "Елисеева М.В.",
    "Жданова Н.А.", "Зиновьева А.В.", "Игнатьева О.С.", "Казакова Е.А.",
    "Лукьянова М.Н.", "Малышева Т.В.", "Нестерова А.А.", "Осипова О.В.",
    "Панова Е.И.", "Рыбакова М.С.", "Самсонова Н.В.", "Трофимова А.Ю.",
    "Фадеева О.А.", "Хохлова Е.В.", "Чернышева М.А.", "Шубина Н.С.",
    "Щукина А.В.", "Юркова О.Д.", "Аксенова Е.В.", "Бабкина М.А.",
    "Вавилова Т.С.", "Галкина А.Н.", "Дьякова О.В.", "Еремина Е.С.",
    "Жилина М.В.", "Зимина Н.А.", "Исаева А.А.", "Калинина О.В.",

    "Иванов А.С.", "Петров М.И.", "Сидоров В.П.", "Козлов Е.В.",
    "Михайлов Д.А.", "Смирнов О.Н.", "Кузнецов А.А.", "Попов Н.В.",
    "Васильев И.П.", "Павлов Л.С.", "Соколов Р.В.", "Федоров А.Н.",
    "Морозов Д.В.", "Волков И.С.", "Алексеев О.В.", "Новиков А.В.",
    "Андреев М.О.", "Степанов С.С.", "Чеснов В.Р.", "Носов И.К.",
    "Борисов Е.В.", "Королев А.А.", "Тимофеев О.С.", "Кудрявцев М.Д.",
    "Белов Н.И.", "Гаврилов Л.В.", "Денисов А.Ю.", "Ермаков О.А.",
    "Захаров Е.П.", "Зуев М.С.", "Ильин Н.В.", "Киселев А.Р.",
    "Комаров О.В.", "Крылов Е.Н.", "Ларин М.А.", "Медведев Т.С.",
    "Никитин А.В.", "Орлов О.И.", "Поляков Е.В.", "Романов А.С.",
    "Сергеев М.В.", "Тарасов О.Н.", "Ушаков Е.А.", "Фролов А.В.",
    "Цветков О.М.", "Чернов Е.С.", "Ширяев М.П.", "Щербаков Н.В.",
    "Яковлев А.А.", "Блинов О.В.", "Власов Е.Д.", "Горбунов М.И.",
    "Дроздов Т.В.", "Евдокимов А.Н.", "Журавлев О.П.", "Зайцев Е.В.",
    "Карпов М.С.", "Лобанов Н.А.", "Максимов А.В.", "Назаров О.Ю.",
    "Овчинников Е.А.", "Панин М.В.", "Рожков Т.Н.", "Савельев А.С.",
    "Тихонов О.В.", "Филиппов Е.М.", "Харитонов Н.А.", "Чистяков А.В.",
    "Шестаков О.Д.", "Юдин Е.В.", "Агафонов М.А.", "Беляев Т.С.",
    "Васин А.И.", "Герасимов О.В.", "Данилов Е.Н.", "Елисеев М.В.",
    "Жданов Н.А.", "Зиновьев А.В.", "Игнатьев О.С.", "Казаков Е.А.",
    "Лукьянов М.Н.", "Малышев Т.В.", "Нестеров А.А.", "Осипов О.В.",
    "Панов Е.И.", "Рыбаков М.С.", "Самсонов Н.В.", "Трофимов А.Ю.",
    "Фадеев О.А.", "Хохлов Е.В.", "Чернышев М.А.", "Шубин Н.С.",
    "Щукин А.В.", "Юрков О.Д.", "Аксенов Е.В.", "Бабкин М.А.",
    "Вавилов Т.С.", "Галкин А.Н.", "Дьяков О.В.", "Еремин Е.С.",
    "Жилин М.В.", "Зимин Н.А.", "Исаев А.А.", "Калинин О.В.",
    "Козырев Д.А.", "Колесников П.В.", "Коновалов А.Н.", "Кочетков И.С.",
    "Крюков В.А.", "Кулаков М.Ю.", "Лаптев А.В.", "Ларионов Н.С.",
    "Левин О.А.", "Логинов Д.В.", "Мамонтов А.С.", "Мельников И.В.",
    "Меркулов Е.А.", "Моисеев П.В.", "Молчанов А.Н.", "Муравьев С.В.",
    "Мышкин В.А.", "Наумов М.В.", "Некрасов А.Д.", "Никонов И.А.",
    "Одинцов О.В.", "Пастухов А.С.", "Пахомов И.В.", "Пименов Е.Н.",
    "Пономарев А.А.", "Прохоров В.В.", "Пугачев М.С.", "Пушкарев А.В.",
    "Разумов Д.А.", "Рогов И.С.", "Русаков О.А.", "Рычков В.В.",
    "Сазонов А.Н.", "Самохвалов М.В.", "Сафонов Д.С.", "Свиридов А.А.",
    "Селезнев И.В.", "Селиванов О.Н.", "Симонов В.А.", "Ситников А.С.",
    "Скворцов М.В.", "Соболев И.А.", "Соловьев Д.В.", "Сорокин О.С.",
    "Суворов А.В.", "Суханов И.Н.", "Сычев М.А.", "Тетерин Д.В.",
]


        self.paper_colors = [(255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        self.init_fonts()
        self.extraction_info = []


    def apply_magnat_item_discounts(self, items, subtotal):
        if random.random() > 0.3:
            for item in items:
                item['original_price'] = item['price']
                item['has_discount'] = False
            return items, 0, subtotal, subtotal

        num_discounted = random.randint(1, min(2, len(items)))
        discounted_indices = random.sample(range(len(items)), num_discounted)

        discount_percent = random.uniform(10, 15)

        total_item_discount = 0
        original_subtotal = subtotal

        for idx in discounted_indices:
            item = items[idx]
            item['original_price'] = item['price']
            item['has_discount'] = True
            item['discount_percent'] = round(discount_percent, 1)

            new_price = round(item['price'] * (1 - discount_percent / 100), 2)
            old_total = item['total']

            item['price'] = new_price
            item['total'] = round(new_price * item['quantity'], 2)
            item['discount_amount'] = round(old_total - item['total'], 2)

            total_item_discount += item['discount_amount']

        new_subtotal = sum(item['total'] for item in items)

        return items, round(total_item_discount, 2), new_subtotal, original_subtotal


    def draw_receipt_start(self, data):
      """Отрисовка чека СТАРТ с QR-кодом справа"""
      width = getattr(self, 'width', 384)
      padding = 12

      img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
      draw = ImageDraw.Draw(img)

      y = 20

      shop_name = "СТАРТ"
      bold_font = self.fonts['bold_large']
      name_width = self.get_text_width(draw, shop_name, 'bold_large')
      name_x = (width - name_width) // 2
      draw.text((name_x, y), shop_name, font=bold_font, fill=0)
      draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
      y += self.fonts['bold_large'].size + 8
      self.draw_text_centered(draw, data['shop']['address'], y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      self.draw_text_centered(draw, f"Тел.: {data['shop']['phone']}", y, 'tiny', width)
      y += self.fonts['tiny'].size + 2
      self.draw_text_centered(draw, f"ИНН {data['shop']['tax_id']}", y, 'tiny', width)
      y += self.fonts['tiny'].size + 8

      date_str = data['date'].strftime("%d.%m.%Y %H:%M")
      self.draw_text_centered(draw, date_str, y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      receipt_text = f"ЧЕК: {data['receipt_num']}"
      self.draw_text_centered(draw, receipt_text, y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      cashier_text = f"КАССИР: {data['cashier']}"
      self.draw_text_centered(draw, cashier_text, y, 'tiny', width)
      y += self.fonts['tiny'].size + 8

      draw.text((padding, y), "ТОВАР", font=self.fonts['bold'], fill=0)

      col_price = width - padding - 130
      col_qty = width - padding - 85
      col_sum = width - padding - 45
      col_price_width = 45
      col_qty_width = 45
      col_sum_width = 40

      price_title = "ЦЕНА"
      price_title_width = self.get_text_width(draw, price_title, 'tiny')
      price_center_x = col_price + col_price_width // 2 - price_title_width // 2
      draw.text((price_center_x, y), price_title, font=self.fonts['tiny'], fill=0)

      col_title = "КОЛ-ВО"
      col_title_width = self.get_text_width(draw, col_title, 'tiny')
      col_title_center_x = col_qty + col_qty_width // 2 - col_title_width // 2
      draw.text((col_title_center_x, y), col_title, font=self.fonts['tiny'], fill=0)

      sum_title = "ИТОГО"
      sum_title_width = self.get_text_width(draw, sum_title, 'tiny')
      sum_center_x = col_sum + col_sum_width // 2 - sum_title_width // 2
      draw.text((sum_center_x, y), sum_title, font=self.fonts['tiny'], fill=0)

      y += self.fonts['bold'].size + 2

      for item in data['items']:
          name = item['name']
          if len(name) > 24:
              name = name[:22] + ".."

          draw.text((padding, y), name, font=self.fonts['small'], fill=0)

          price_text = f"{item['price']:.2f}"
          price_width = self.get_text_width(draw, price_text, 'small')
          price_center_x = col_price + col_price_width // 2 - price_width // 2
          draw.text((price_center_x, y), price_text, font=self.fonts['small'], fill=0)

          qty_text = str(item['quantity'])
          qty_width = self.get_text_width(draw, qty_text, 'small')
          qty_center_x = col_qty + col_qty_width // 2 - qty_width // 2
          draw.text((qty_center_x, y), qty_text, font=self.fonts['small'], fill=0)

          sum_text = f"{item['total']:.2f}"
          sum_width = self.get_text_width(draw, sum_text, 'small')
          sum_x = col_sum + col_sum_width - sum_width
          draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

          y += self.fonts['small'].size + 1
          vat_text = f"  НДС {item['vat']}"
          draw.text((padding + 5, y), vat_text, font=self.fonts['tiny'], fill=0)
          y += self.fonts['tiny'].size + 1

      draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
      y += 8

      draw.text((padding, y), "ПОДЫТОГ:", font=self.fonts['small'], fill=0)
      draw.text((col_sum, y), f"{data['subtotal']:.2f}", font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 1

      discount_val = data.get('discount', data.get('total_discount', 0))
      if discount_val > 0:
          draw.text((padding, y), "СКИДКА:", font=self.fonts['small'], fill=0)
          draw.text((col_sum, y), f"-{data['discount']:.2f}", font=self.fonts['small'], fill=0)
          y += self.fonts['small'].size + 1

      draw.text((padding, y), "ИТОГО:", font=self.fonts['bold'], fill=0)
      draw.text((col_sum, y), f"{data['total']:.2f}", font=self.fonts['bold'], fill=0)
      y += self.fonts['bold'].size + 4

      draw.text((padding, y), data['payment_type'], font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      fiscal_y_start = y

      draw.text((padding, y), f"СНО: {data['tax_system']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 1
      draw.text((padding, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 1
      draw.text((padding, y), f"ЗН ФН: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 1
      draw.text((padding, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 1
      draw.text((padding, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 1
      draw.text((padding, y), f"ФД: {data['fd']}", font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 3

      qr_size = 110
      qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
      qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
      qr.make(fit=True)
      qr_img = qr.make_image(fill_color="black", back_color="white")
      qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

      paper_color = img.getpixel((padding, fiscal_y_start))
      qr_img = qr_img.convert('RGBA')
      qr_data = qr_img.getdata()
      new_data = []
      for pixel in qr_data:
          if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
              new_data.append((0, 0, 0, 255))
          else:
              new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
      qr_img.putdata(new_data)

      qr_x = width - padding - qr_size 
      img.paste(qr_img, (qr_x, fiscal_y_start), qr_img)

      y = max(y, fiscal_y_start + qr_size + 15)
      self.draw_text_centered(draw, "СПАСИБО ЗА ПОКУПКУ!", y, 'small', width)
      y += self.fonts['small'].size + 10

      img_array = np.array(img.convert('L'))
      non_empty_rows = np.where(img_array < 250)[0]
      if len(non_empty_rows) > 0:
          actual_bottom = max(non_empty_rows) + 20
      else:
          actual_bottom = y
      img = img.crop((0, 0, width, min(actual_bottom, 2000)))

      return img, data['extraction_data']

    def init_fonts(self):
        self.fonts = {}
        font_candidates = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"]

        for font_name in font_candidates:
            try:
                self.fonts['tiny'] = ImageFont.truetype(font_name, 10)
                self.fonts['small'] = ImageFont.truetype(font_name, 12)
                self.fonts['normal'] = ImageFont.truetype(font_name, 13)
                self.fonts['large'] = ImageFont.truetype(font_name, 15)
                self.fonts['bold'] = ImageFont.truetype(font_name, 13)
                self.fonts['bold_large'] = ImageFont.truetype(font_name, 16)
                break
            except:
                continue
        else:
            default_font = ImageFont.load_default()
            for name in self.fonts:
                self.fonts[name] = default_font

    def get_text_width(self, draw, text, font_key):
        bbox = draw.textbbox((0, 0), text, font=self.fonts[font_key])
        return bbox[2] - bbox[0]

    def draw_text_centered(self, draw, text, y, font_key, width):
        text_width = self.get_text_width(draw, text, font_key)
        x = (width - text_width) // 2
        draw.text((x, y), text, font=self.fonts[font_key], fill=0)
        return text_width

    def draw_text_two_columns(self, draw, left_text, right_text, y, left_font, right_font, width, padding):
        draw.text((padding, y), left_text, font=self.fonts[left_font], fill=0)
        right_width = self.get_text_width(draw, right_text, right_font)
        draw.text((width - padding - right_width, y), right_text, font=self.fonts[right_font], fill=0)
        return max(self.fonts[left_font].size, self.fonts[right_font].size)

    def get_bonus_operation(self, shop, total):
        if shop["name"] in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
            return None

        features = shop.get('features', [])

        if "hotline" in features:
            if random.random() > 0.6:
                bonus = round(random.randint(10, 200) / 10, 1)
                return f"НАЧИСЛЕНО БОНУСОВ: {bonus}"
            else:
                bonus = round(random.randint(5, 150) / 10, 1)
                return f"СПИСАНО БОНУСОВ: {bonus}"
        elif "bonus_card" in features:
            bonus = round(total * random.uniform(0.01, 0.05), 1)
            return f"НАЧИСЛЕНО БОНУСОВ: {bonus}"
        elif "discount_card" in features:
            saved = round(total * random.uniform(0.03, 0.10), 2)
            return f"ВАША СКИДКА: {saved:.2f}"
        elif "club_card" in features:
            points = round(total * random.uniform(0.02, 0.08), 1)
            return f"НАЧИСЛЕНО КЛУБНЫХ БАЛЛОВ: {points}"
        elif "bonus_program" in features:
            bonus = round(total * random.uniform(0.01, 0.03), 1)
            return f"ПРОГРАММА ЛОЯЛЬНОСТИ: +{bonus}"
        elif random.random() > 0.85:
            bonus = round(random.randint(5, 50) / 10, 1)
            return f"БОНУСНАЯ КАРТА: {bonus}"

        return None

    def create_receipt_content(self):
        shop = random.choice(self.shops)
        all_products = self.grocery_products if shop["type"] == "grocery" else self.pharmacy_products

        days_ago = random.randint(0, 7)
        receipt_date = datetime.now() - timedelta(days=days_ago)
        receipt_date = receipt_date.replace(hour=random.randint(8, 22), minute=random.randint(0, 59))

        rn_kkt = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        zi_kkt = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        fn = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        fp = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        fd = str(random.randint(10000, 99999))

        kkt_reg_num = rn_kkt
        fn_zav_num = zi_kkt
        receipt_num = str(random.randint(1000, 9999))
        num_items = random.randint(3, 12)
        items, subtotal = [], 0
        vat_by_rate = {"20%": 0, "10%": 0, "0%": 0}

        selected_products = random.sample(all_products, min(num_items, len(all_products)))

        for item in selected_products:
            qty = random.choices([1, 2], weights=[80, 20])[0]
            price = round(random.randint(*item["price_range"]) + random.randint(0, 99)/100, 2)
            total = round(price * qty, 2)
            subtotal += total

            vat_rate = item["vat"]
            vat_amount = round(total * (20/120 if vat_rate == "20%" else 10/110 if vat_rate == "10%" else 0), 2)
            vat_by_rate[vat_rate] += vat_amount

            items.append({
                "name": item["name"],
                "quantity": qty,
                "price": price,
                "total": total,
                "vat": vat_rate,
                "vat_amount": vat_amount
            })

        discount = round(random.randint(10, 50)/100, 2) if random.random() > 0.8 else 0

        item_discount = 0
        original_subtotal = subtotal

        if shop["name"] == "МАГНАТ":
            items, item_discount, new_subtotal, original_subtotal = self.apply_magnat_item_discounts(items, subtotal)
            subtotal = new_subtotal 
        else:
            original_subtotal = subtotal

        card_discount = 0
        if shop["name"] == "МАГНАТ":
            if random.random() > 0.5:
                card_discount = round(subtotal * random.uniform(0.02, 0.05), 2)

        total_discount = round(item_discount + card_discount, 2)

        total = round(subtotal - card_discount, 2)

        if shop["type"] == "pharmacy":
            nds_20 = 0
            nds_10 = 0
            nds_0 = 0
        else:
            if original_subtotal > 0:
                total_discount_ratio = 1 - (total / original_subtotal) if total < original_subtotal else 1
            else:
                total_discount_ratio = 1
            nds_20 = round(vat_by_rate["20%"] * total_discount_ratio, 2)
            nds_10 = round(vat_by_rate["10%"] * total_discount_ratio, 2)
            nds_0 = 0

        date_qr = receipt_date.strftime("%d%m%y")
        time_qr = receipt_date.strftime("%H%M%S")
        qr_string = f"t={date_qr}T{time_qr}&s={total:.2f}&fn={fn}&i={fd}&fp={fp}&n=1"

        cashier = random.choice(self.russian_names)
        payment = random.choice(["НАЛИЧНЫМИ", "БАНКОВСКОЙ КАРТОЙ"])

        card_data = None
        if payment == "БАНКОВСКОЙ КАРТОЙ":
            card_data = {
                "rrn": ''.join([str(random.randint(0, 9)) for _ in range(12)]),
                "auth_code": ''.join([str(random.randint(0, 9)) for _ in range(6)]),
                "terminal": ''.join([str(random.randint(0, 9)) for _ in range(8)]),
                "card_type": random.choice(["VISA", "MasterCard", "МИР"]),
                "card_mask": f"{random.randint(1000,9999)} {random.randint(1000,9999)}"
            }

        cash_recv = cash_chng = None
        if payment == "НАЛИЧНЫМИ":
            if shop["type"] == "pharmacy":
                reasonable_bills = [100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000]
                cash_recv = None
                for bill in reasonable_bills:
                    if bill >= total:
                        cash_recv = bill
                        break
                if cash_recv is None:
                    cash_recv = ((total // 20000) + 1) * 20000

                if cash_recv < total:
                    for bill in reasonable_bills:
                        if bill >= total:
                            cash_recv = bill
                            break

                cash_chng = round(cash_recv - total, 2)
                if cash_chng < 0:
                    cash_chng = 0
            else:
                bill_denominations = [50, 100, 200, 500, 1000, 2000, 5000]
                suitable_bills = [b for b in bill_denominations if b >= total]
                if suitable_bills:
                    cash_recv = min(suitable_bills)
                else:
                    cash_recv = ((total // 5000) + 1) * 5000
                cash_chng = round(cash_recv - total, 2)
                if cash_chng < 0:
                    cash_chng = 0

        bonus_text = self.get_bonus_operation(shop, total)

        extraction_data = {
            "id": self.receipt_counter,
            "fn": fn, "fd": fd, "fp": fp,
            "subtotal": subtotal,
            "subtotal_original": original_subtotal,
            "item_discount": item_discount,
            "card_discount": card_discount,
            "total_discount": total_discount,
            "total": total,
            "nds_20": nds_20, "nds_10": nds_10, "nds_0": nds_0,
            "date": receipt_date.strftime("%d.%m.%Y"),
            "time": receipt_date.strftime("%H:%M"),
            "shop_name": shop["name"], "shop_address": shop["address"],
            "tax_id": shop["tax_id"], "receipt_num": receipt_num,
            "payment_type": payment, "cash_received": cash_recv, "cash_change": cash_chng,
            "cashier": cashier, "items_count": num_items, "items": items,
            "qr_data": qr_string,
            "kkt_reg_num": rn_kkt,
            "fn_zav_num": zi_kkt,
            "tax_system": shop["tax_system"], "smena_num": self.smena_counter,
            "card_data": card_data, "timezone": "MSK", "alignment": shop["alignment"],
            "bonus_text": bonus_text, "hotline_number": self.hotline_number if "hotline" in shop.get("features", []) else None
        }

        self.receipt_counter += 1
        self.smena_counter += 1

        return {
            "shop": shop, "date": receipt_date, "fn": fn, "fd": fd, "fp": fp,
            "items": items, "subtotal": subtotal,
            "subtotal_original": original_subtotal,
            "item_discount": item_discount,
            "card_discount": card_discount,
            "total_discount": total_discount,
            "total": total,
            "nds_20": nds_20, "nds_10": nds_10, "nds_0": nds_0,
            "cashier": cashier, "payment_type": payment,
            "cash_received": cash_recv, "cash_change": cash_chng, "receipt_num": receipt_num,
            "extraction_data": extraction_data, "qr_string": qr_string,
            "kkt_reg_num": rn_kkt,
            "fn_zav_num": zi_kkt,
            "tax_system": shop["tax_system"], "smena_num": self.smena_counter - 1,
            "card_data": card_data, "alignment": shop["alignment"],
            "bonus_text": bonus_text
        }

    def draw_receipt_semidorog(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        self.draw_text_centered(draw, 'Сеть магазинов "У дома"', y, 'normal', width)
        y += self.fonts['small'].size + 2
        shop_name = "емь дорог"
        bold_font = self.fonts['bold_large']
        circle_size = 21
        letter_c = "С"
        letter_width = self.get_text_width(draw, letter_c, 'bold_large')
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        total_width = circle_size + name_width
        start_x = (width - total_width) // 2
        circle_x = start_x
        circle_y = y - 1
        draw.ellipse([circle_x, circle_y, circle_x + circle_size, circle_y + circle_size], fill=0, outline=0)

        text_x = circle_x + (circle_size - letter_width) // 2
        text_y = circle_y + (circle_size - self.fonts['bold_large'].size) // 2
        draw.text((text_x, text_y), "С", font=bold_font, fill=(255, 255, 255))

        draw.text((start_x + circle_size, y), shop_name, font=bold_font, fill=0)
        draw.text((start_x + circle_size + 1, y), shop_name, font=bold_font, fill=0)

        y += self.fonts['bold_large'].size + 8
        half_width = width // 2

        draw.text((padding, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['small'], fill=0)
        datetime_str = data['date'].strftime("%d.%m.%Y  %H:%M")
        datetime_width = self.get_text_width(draw, datetime_str, 'small')
        draw.text((width - padding - datetime_width, y), datetime_str, font=self.fonts['small'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((padding, y), f"ЗН ККТ: {data['fn_zav_num']}", font=self.fonts['small'], fill=0)
        smena_chek_str = f"Смена: {data['smena_num']}  Чек: {data['receipt_num']}"
        smena_chek_width = self.get_text_width(draw, smena_chek_str, 'small')
        draw.text((width - padding - smena_chek_width, y), smena_chek_str, font=self.fonts['small'], fill=0)
        y += self.fonts['tiny'].size + 4

        draw.text((padding, y), "КАССОВЫЙ ЧЕК / ПРИХОД", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4
        draw.text((padding, y), f"ИНН {data['shop']['tax_id']}", font=self.fonts['small'], fill=0)
        fn_str = f"ФН: {data['fn']}"
        fn_width = self.get_text_width(draw, fn_str, 'small')
        draw.text((width - padding - fn_width, y), fn_str, font=self.fonts['tiny'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), f"Кассир: {data['cashier']}", font=self.fonts['small'], fill=0)
        cash_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        cash_str = f"#{cash_num}"
        cash_width = self.get_text_width(draw, cash_str, 'small')
        draw.text((width - padding - cash_width, y), cash_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), "Сайт ФНС:", font=self.fonts['small'], fill=0)
        fns_url = "www.nalog.ru"
        fns_width = self.get_text_width(draw, fns_url, 'small')
        draw.text((width - padding - fns_width, y), fns_url, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        ofd_options = [
            'ООО "Экватор-ОФД"',
            'ООО "Ярус-ОФД"',
            'ООО "Такском-ОФД"',
            'ООО "Платформа ОФД"',
            'ООО "Эвотор ОФД"'
        ]
        ofd = random.choice(ofd_options)
        draw.text((padding, y), "ОФД:", font=self.fonts['small'], fill=0)
        ofd_width = self.get_text_width(draw, ofd, 'small')
        draw.text((width - padding - ofd_width, y), ofd, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        network_sites = ['www.7dorog.ru', 'www.semdorog.ru', 'www.7-roads.ru', 'www.sem-dorog.ru']
        site = random.choice(network_sites)
        draw.text((padding, y), "Сайт ОФД:", font=self.fonts['small'], fill=0)
        site_width = self.get_text_width(draw, site, 'small')
        draw.text((width - padding - site_width, y), site, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        addr_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        draw.text((padding, y), f"{addr_code}, {data['shop']['address']}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        stars = '*' * 115
        self.draw_text_centered(draw, stars, y, 'small', width)
        y += self.fonts['small'].size + 8

        col_price = width - padding - 130  
        col_qty = width - padding - 85     
        col_sum = width - padding - 45     
        col_price_width = 45
        col_qty_width = 45
        col_sum_width = 40

        y += self.fonts['bold'].size + 2

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            formula_text = f"{item['quantity']}.000 x {item['price']:.2f}"
            formula_width = self.get_text_width(draw, formula_text, 'small')
            formula_x = width - padding - formula_width
            draw.text((formula_x, y), formula_text, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 1

            sum_text = f"= {item['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 3
        draw_line(y, 'dashed')
        y += 8

        discount_val = data.get('discount', data.get('total_discount', 0))
        if discount_val > 0:
            draw.text((padding, y), "ИТОГО СКИДКА ПО ЧЕКУ:", font=self.fonts['tiny'], fill=0)
            discount_str = f"= {data['discount']:.2f}"
            discount_width = self.get_text_width(draw, discount_str, 'tiny')
            discount_x = width - padding - discount_width
            draw.text((discount_x, y), discount_str, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 4

        draw.text((padding, y), "ИТОГ:", font=self.fonts['bold_large'], fill=0)

        total_val = data['total']
        total_str = f"= {total_val:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold_large')
        total_x = width - padding - total_width
        draw.text((total_x, y), total_str, font=self.fonts['bold_large'], fill=0)
        y += self.fonts['bold_large'].size + 4

        draw.text((padding, y), data['payment_type'], font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 4
        if data['nds_10'] > 0:
            draw.text((padding, y), "НДС 10%:", font=self.fonts['tiny'], fill=0)
            nds_10_str = f"= {data['nds_10']:.2f}"
            nds_10_width = self.get_text_width(draw, nds_10_str, 'tiny')
            nds_10_x = width - padding - nds_10_width
            draw.text((nds_10_x, y), nds_10_str, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 2

        if data['nds_20'] > 0:
            draw.text((padding, y), "НДС 20%:", font=self.fonts['tiny'], fill=0)
            nds_20_str = f"= {data['nds_20']:.2f}"
            nds_20_width = self.get_text_width(draw, nds_20_str, 'tiny')
            nds_20_x = width - padding - nds_20_width
            draw.text((nds_20_x, y), nds_20_str, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 2

        y += 4
        draw.text((padding, y), f"СНО: {data['tax_system']}", font=self.fonts['small'], fill=0)
        fd_fp_str = f"ФД: {data['fd']}  ФП: {data['fp']}"
        fd_fp_width = self.get_text_width(draw, fd_fp_str, 'small')
        draw.text((width - padding - fd_fp_width, y), fd_fp_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 15
        qr_size = 125
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data = qr_img.getdata()
        new_data = []
        for pixel in qr_data:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0,0,0,255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0,0), qr_img)

        qr_x = (width - qr_size) // 2
        img.paste(qr_with_paper, (qr_x, y))
        y += qr_size + 20
        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']


    def draw_receipt_pharmacy(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20
        pharmacy_names = [
            "Аптека-В", "Аптека-А.В.Е", "Аптека-Фарм", "Аптека-Здоровье",
            "Аптека-Плюс", "Аптека-Мед", "Аптека-Доктор", "Аптека-Витамин",
            "Аптека-Эко", "Аптека-Лайф"
        ]
        ph_name = random.choice(pharmacy_names)
        ooo_name = f'ООО "{ph_name}"'

        shop_name = data['shop']['name']
        bold_font = self.fonts['bold_large']
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        draw.text((name_x, y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 8

        addr_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        addr_text = f"{addr_code}, {data['shop']['address']}"
        self.draw_text_centered(draw, addr_text, y, 'tiny', width)
        y += self.fonts['tiny'].size + 4

        self.draw_text_centered(draw, ooo_name, y, 'small', width)
        y += self.fonts['small'].size + 8

        draw.text((padding, y), "ПРИХОД", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4
        draw.text((padding, y), f"Кассир: {data['cashier']}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8
        draw_line(y, 'dashed')
        y += 8

        self.draw_text_centered(draw, "Товар", y, 'small', width)
        y += self.fonts['small'].size + 4

        draw_line(y, 'dashed')
        y += 8

        for item in data['items']:
            name = item['name']
            if len(name) > 22:
                name = name[:20] + ".."

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            sum_text = f"= {item['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            formula_text = f"{item['quantity']}.000 * {item['price']:.2f}"
            formula_width = self.get_text_width(draw, formula_text, 'tiny')
            formula_x = sum_x - 5 - formula_width  # Отступ 5px от суммы
            draw.text((formula_x, y), formula_text, font=self.fonts['tiny'], fill=0)

            y += self.fonts['small'].size + 2

        y += 4

        draw_line(y, 'dashed')
        y += 8

        itog_tov_str = f"Итог по товарам:"
        itog_tov_width = self.get_text_width(draw, itog_tov_str, 'small')
        draw.text((width - padding - itog_tov_width, y), itog_tov_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2
        draw_line(y, 'dashed')
        y += 8

        draw.text((padding, y), "К оплате:", font=self.fonts['small'], fill=0)
        oplata_str = f"{data['total']:.2f}"
        oplata_width = self.get_text_width(draw, oplata_str, 'small')
        draw.text((width - padding - oplata_width, y), oplata_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw_line(y, 'dashed')
        y += 8

        draw.text((padding, y), "Итог:", font=self.fonts['bold_large'], fill=0)
        total_str = f"= {data['total']:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold_large')
        draw.text((width - padding - total_width, y), total_str, font=self.fonts['bold_large'], fill=0)
        y += self.fonts['bold'].size + 4

        if data['nds_20'] > 0:
            draw.text((padding, y), "Сумма НДС 20%:", font=self.fonts['tiny'], fill=0)
            nds_sum_str = f"= {data['nds_20']:.2f}"
            nds_sum_width = self.get_text_width(draw, nds_sum_str, 'tiny')
            draw.text((width - padding - nds_sum_width, y), nds_sum_str, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 2

        draw.text((padding, y), data['payment_type'], font=self.fonts['tiny'], fill=0)

        if data['payment_type'] == "НАЛИЧНЫМИ" and data.get('cash_received'):
            payment_sum = data['cash_received']
            cash_received_value = data['cash_received']
        else:
            payment_sum = data['total']
            cash_received_value = data['total']

        payment_str = f"{payment_sum:.2f}"
        payment_width = self.get_text_width(draw, payment_str, 'small')
        draw.text((width - padding - payment_width, y), payment_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        if data['payment_type'] == "НАЛИЧНЫМИ" and data.get('cash_received'):
            draw.text((padding, y), "Получено:", font=self.fonts['small'], fill=0)
            cash_str = f"= {cash_received_value:.2f}"
            cash_width = self.get_text_width(draw, cash_str, 'small')
            draw.text((width - padding - cash_width, y), cash_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 2

            draw.text((padding, y), "Сдача:", font=self.fonts['small'], fill=0)
            change = max(0, cash_received_value - data['total'])
            change_str = f"{change:.2f}"
            change_width = self.get_text_width(draw, change_str, 'small')
            draw.text((width - padding - change_width, y), change_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

        draw.text((padding, y), "СНО:", font=self.fonts['small'], fill=0)
        sno_str = data['tax_system']
        sno_width = self.get_text_width(draw, sno_str, 'small')
        draw.text((width - padding - sno_width, y), sno_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), "Пользователь:", font=self.fonts['small'], fill=0)
        user_width = self.get_text_width(draw, ooo_name, 'small')
        draw.text((width - padding - user_width, y), ooo_name, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "Адрес:", font=self.fonts['small'], fill=0)
        addr_str = data['shop']['address']
        addr_width = self.get_text_width(draw, addr_str, 'small')
        draw.text((width - padding - addr_width, y), addr_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2
        draw.text((padding, y), "Место расчетов:", font=self.fonts['small'], fill=0)
        place_str = "Аптека"
        place_width = self.get_text_width(draw, place_str, 'small')
        draw.text((width - padding - place_width, y), place_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), "Кассир:", font=self.fonts['small'], fill=0)
        cashier_str = data['cashier']
        cashier_width = self.get_text_width(draw, cashier_str, 'small')
        draw.text((width - padding - cashier_width, y), cashier_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "Сайт ФНС:", font=self.fonts['small'], fill=0)
        fns_url = "www.nalog.ru"
        fns_width = self.get_text_width(draw, fns_url, 'small')
        draw.text((width - padding - fns_width, y), fns_url, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "ЗН ККТ:", font=self.fonts['small'], fill=0)
        zn_str = data['fn_zav_num']
        zn_width = self.get_text_width(draw, zn_str, 'small')
        draw.text((width - padding - zn_width, y), zn_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "Смена №:", font=self.fonts['small'], fill=0)
        smena_str = str(data['smena_num'])
        smena_width = self.get_text_width(draw, smena_str, 'small')
        draw.text((width - padding - smena_width, y), smena_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "Чек №:", font=self.fonts['small'], fill=0)
        receipt_str = data['receipt_num']
        receipt_width = self.get_text_width(draw, receipt_str, 'small')
        draw.text((width - padding - receipt_width, y), receipt_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "Дата/время:", font=self.fonts['small'], fill=0)
        datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")
        datetime_width = self.get_text_width(draw, datetime_str, 'small')
        draw.text((width - padding - datetime_width, y), datetime_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "ИНН:", font=self.fonts['small'], fill=0)
        inn_str = data['shop']['tax_id']
        inn_width = self.get_text_width(draw, inn_str, 'small')
        draw.text((width - padding - inn_width, y), inn_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "РН ККТ:", font=self.fonts['small'], fill=0)
        rn_str = data['kkt_reg_num']
        rn_width = self.get_text_width(draw, rn_str, 'small')
        draw.text((width - padding - rn_width, y), rn_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "ФН №:", font=self.fonts['small'], fill=0)
        fn_str = data['fn']
        fn_width = self.get_text_width(draw, fn_str, 'small')
        draw.text((width - padding - fn_width, y), fn_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "ФД №:", font=self.fonts['small'], fill=0)
        fd_str = data['fd']
        fd_width = self.get_text_width(draw, fd_str, 'small')
        draw.text((width - padding - fd_width, y), fd_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 2

        draw.text((padding, y), "ФП:", font=self.fonts['small'], fill=0)
        fp_str = data['fp']
        fp_width = self.get_text_width(draw, fp_str, 'small')
        draw.text((width - padding - fp_width, y), fp_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 15

        qr_size = 110
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data = qr_img.getdata()
        new_data = []
        for pixel in qr_data:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0,0,0,255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0,0), qr_img)

        qr_x = (width - qr_size) // 2
        img.paste(qr_with_paper, (qr_x, y))
        y += qr_size + 20

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_magnat(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = "МАГНАТ"
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        name_y = y
        m_x = name_x - 25
        m_y = name_y
        draw.text((m_x, m_y), "М", font=bold_font, fill=0)
        draw.text((m_x + 1, m_y), "М", font=bold_font, fill=0)
        m_bbox = draw.textbbox((m_x, m_y), "М", font=bold_font)
        m_left = m_bbox[0]
        m_top = m_bbox[1]
        m_right = m_bbox[2]
        m_bottom = m_bbox[3]
        padding_around_m = 3
        square_left = m_left - padding_around_m
        square_top = m_top - padding_around_m
        square_right = m_right + padding_around_m
        square_bottom = m_bottom + padding_around_m
        for i in range(2):
            draw.rectangle([square_left - i, square_top - i, square_right + i, square_bottom + i], outline=0, width=1)

        draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 12

        available_width = width - (padding * 2)
        col_width = available_width // 4

        col1_center = padding + col_width // 2
        col2_center = padding + col_width + col_width // 2
        col3_center = padding + col_width * 2 + col_width // 2
        col4_center = padding + col_width * 3 + col_width // 2

        draw.text((col1_center - self.get_text_width(draw, "ЦЕНА", 'tiny') // 2, y), "ЦЕНА", font=self.fonts['tiny'], fill=0)
        draw.text((col2_center - self.get_text_width(draw, "ЦЕНА СО СКИДКОЙ", 'tiny') // 2, y), "ЦЕНА СО СКИДКОЙ", font=self.fonts['tiny'], fill=0)
        draw.text((col3_center - self.get_text_width(draw, "КОЛ-ВО", 'tiny') // 2, y), "КОЛ-ВО", font=self.fonts['tiny'], fill=0)
        draw.text((col4_center - self.get_text_width(draw, "ИТОГ", 'tiny') // 2, y), "ИТОГ", font=self.fonts['tiny'], fill=0)
        y += self.fonts['small'].size + 8

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 2

            original_price = item.get('original_price', item['price'])
            price_text = f"{original_price:.2f}"
            draw.text((col1_center - self.get_text_width(draw, price_text, 'small') // 2, y), price_text, font=self.fonts['small'], fill=0)

            if item.get('has_discount', False):
                discounted_price_text = f"{item['price']:.2f}"
                draw.text((col2_center - self.get_text_width(draw, discounted_price_text, 'small') // 2, y), discounted_price_text, font=self.fonts['small'], fill=0)
            else:
                draw.text((col2_center - self.get_text_width(draw, price_text, 'small') // 2, y), price_text, font=self.fonts['small'], fill=0)

            qty_text = f"{item['quantity']}.000"
            draw.text((col3_center - self.get_text_width(draw, qty_text, 'small') // 2, y), qty_text, font=self.fonts['small'], fill=0)

            total_text = f"{item['total']:.2f}"
            draw.text((col4_center - self.get_text_width(draw, total_text, 'small') // 2, y), total_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 8

        card_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        card_label = "Карта №:"
        card_number = f"****-****-****-{card_suffix}"
        draw.text((padding, y), card_label, font=self.fonts['small'], fill=0)
        card_number_width = self.get_text_width(draw, card_number, 'small')
        draw.text((width - padding - card_number_width, y), card_number, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        bonus_earned = round(data['total'] * random.uniform(0.01, 0.05), 1)
        bonus_balance = round(random.uniform(100, 500), 1)

        draw.text((padding, y), "Начислено бонусов", font=self.fonts['small'], fill=0)
        bonus_earned_str = f"{bonus_earned:.1f}"
        draw.text((width - padding - self.get_text_width(draw, bonus_earned_str, 'small'), y), bonus_earned_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), "Баланс бонусов", font=self.fonts['small'], fill=0)
        bonus_balance_str = f"{bonus_balance:.1f}"
        draw.text((width - padding - self.get_text_width(draw, bonus_balance_str, 'small'), y), bonus_balance_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw_line(y, 'solid')
        y += 8

        card_discount = data.get('card_discount', 0)
        if card_discount > 0:
            draw.text((padding, y), "Скидка по Карте Магнат", font=self.fonts['small'], fill=0)
            card_discount_str = f"{card_discount:.2f}"
            draw.text((width - padding - self.get_text_width(draw, card_discount_str, 'small'), y), card_discount_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

        subtotal_original = data.get('subtotal_original', data['subtotal'])
        draw.text((padding, y), "Итог без скидок", font=self.fonts['small'], fill=0)
        subtotal_original_str = f"{subtotal_original:.2f}"
        draw.text((width - padding - self.get_text_width(draw, subtotal_original_str, 'small'), y), subtotal_original_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        total_discount = data.get('total_discount', 0)
        if total_discount > 0:
            draw.text((padding, y), "Скидка", font=self.fonts['bold'], fill=0)
            discount_str = f"{total_discount:.2f}"
            draw.text((width - padding - self.get_text_width(draw, discount_str, 'bold'), y), discount_str, font=self.fonts['bold'], fill=0)
            y += self.fonts['bold'].size + 4

        total_val = data['total']
        draw.text((padding, y), "Итог", font=self.fonts['bold'], fill=0)
        total_str = f"{total_val:.2f}"
        draw.text((width - padding - self.get_text_width(draw, total_str, 'bold'), y), total_str, font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 4

        payment_text = data['payment_type']
        draw.text((padding, y), payment_text, font=self.fonts['small'], fill=0)

        if data['payment_type'] == "НАЛИЧНЫМИ":
            payment_sum = f"{data['cash_received']:.2f}"
        else:
            payment_sum = f"{total_val:.2f}"

        draw.text((width - padding - self.get_text_width(draw, payment_sum, 'small'), y), payment_sum, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        if data['payment_type'] == "НАЛИЧНЫМИ":
            draw.text((padding, y), "Сдача", font=self.fonts['small'], fill=0)
            change = data['cash_received'] - total_val
            if change < 0:
                change = 0
            change_str = f"{change:.2f}"
            draw.text((width - padding - self.get_text_width(draw, change_str, 'small'), y), change_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

        draw_line(y, 'solid')
        y += 8

        right_block_start_y = y
        qr_size = 125
        left_x = padding

        draw.text((left_x, y), "Место расчётов Магазин Магнат", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        zip_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        address_text = f"АО \"Тандр\" {zip_code}, {data['shop']['address']}"
        draw.text((left_x, y), address_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"Кассир: {data['cashier']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), "Кассовый чек", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), "ПРИХОД", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        inn_num = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        draw.text((left_x, y), f"ИНН: {inn_num}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ЗН ККТ: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        fd_num = str(random.randint(10000, 99999))
        draw.text((left_x, y), f"ФД: {fd_num}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")
        draw.text((left_x, y), datetime_str, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 8

        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, right_block_start_y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data_img = qr_img.getdata()
        new_data = []
        for pixel in qr_data_img:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0, 0, 0, 255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0, 0), qr_img)

        qr_x = width - padding - qr_size
        img.paste(qr_with_paper, (qr_x, right_block_start_y))

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_shesterochka(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = "ШЕСТЕРОЧКА"
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        name_y = y

        icon_size = self.fonts['bold_large'].size + 4
        circle_x = name_x - icon_size - 8
        circle_y = name_y - 2

        draw.ellipse([circle_x, circle_y, circle_x + icon_size, circle_y + icon_size], fill=0, outline=0)
        draw.text((circle_x + icon_size//2 - 6 + 1, circle_y + icon_size//2 - 8 + 1), "6", font=bold_font, fill=(80,80,80))
        draw.text((circle_x + icon_size//2 - 6, circle_y + icon_size//2 - 8), "6", font=bold_font, fill=(255,255,255))

        draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 4

        self.draw_text_centered(draw, "КАССОВЫЙ ЧЕК", y, 'small', width)
        y += self.fonts['small'].size + 10

        draw.text((padding, y), "ТОВАР", font=self.fonts['bold'], fill=0)

        col_price = width - padding - 130
        col_qty = width - padding - 85
        col_sum = width - padding - 45
        col_price_width = 45
        col_qty_width = 45
        col_sum_width = 40

        price_title = "ЦЕНА"
        price_title_width = self.get_text_width(draw, price_title, 'tiny')
        price_center_x = col_price + col_price_width // 2 - price_title_width // 2
        draw.text((price_center_x, y), price_title, font=self.fonts['tiny'], fill=0)

        col_title = "КОЛ-ВО"
        col_title_width = self.get_text_width(draw, col_title, 'tiny')
        col_title_center_x = col_qty + col_qty_width // 2 - col_title_width // 2
        draw.text((col_title_center_x, y), col_title, font=self.fonts['tiny'], fill=0)

        sum_title = "ИТОГО"
        sum_title_width = self.get_text_width(draw, sum_title, 'tiny')
        sum_center_x = col_sum + col_sum_width // 2 - sum_title_width // 2
        draw.text((sum_center_x, y), sum_title, font=self.fonts['tiny'], fill=0)

        y += self.fonts['bold'].size + 2

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            price_text = f"{item['price']:.2f}"
            price_width = self.get_text_width(draw, price_text, 'small')
            price_center_x = col_price + col_price_width // 2 - price_width // 2
            draw.text((price_center_x, y), price_text, font=self.fonts['small'], fill=0)

            qty_text = str(item['quantity'])
            qty_width = self.get_text_width(draw, qty_text, 'small')
            qty_center_x = col_qty + col_qty_width // 2 - qty_width // 2
            draw.text((qty_center_x, y), qty_text, font=self.fonts['small'], fill=0)

            sum_text = f"{item['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = col_sum + col_sum_width - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 1
            vat_text = f"  НДС {item['vat']}"
            draw.text((padding + 5, y), vat_text, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1

        draw_line(y, 'dashed')
        y += 5

        draw.text((padding, y), "ИТОГ С УЧЕТОМ СКИДОК:", font=self.fonts['small'], fill=0)

        total_val = data['total']
        total_str = f"{total_val:.2f}"
        right_edge_x = width - padding
        draw.text((right_edge_x - self.get_text_width(draw, total_str, 'small'), y), total_str, font=self.fonts['small'], fill=0)

        y += self.fonts['small'].size + 5

        draw_line(y, 'dashed')
        y += 8

        half_width = width // 2

        draw.text((padding, y), "СКИДКА:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 15), "ОКРУГЛЕНИЕ:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 30), "НАЛИЧНЫМИ:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 45), "БЕЗНАЛИЧНЫМИ:", font=self.fonts['tiny'], fill=0)

        discount_val = data.get('discount', data.get('total_discount', 0))
        rounding_val = 0.00
        cash_val = data['cash_received'] if data['payment_type'] == "НАЛИЧНЫМИ" else 0.00
        cashless_val = data['total'] if data['payment_type'] == "БАНКОВСКОЙ КАРТОЙ" else 0.00

        left_sum_edge_x = half_width - 5

        discount_str = f"{discount_val:.2f}"
        rounding_str = f"{rounding_val:.2f}"
        cash_str = f"{cash_val:.2f}"
        cashless_str = f"{cashless_val:.2f}"

        draw.text((left_sum_edge_x - self.get_text_width(draw, discount_str, 'tiny'), y), discount_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, rounding_str, 'tiny'), y + 15), rounding_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, cash_str, 'tiny'), y + 30), cash_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, cashless_str, 'tiny'), y + 45), cashless_str, font=self.fonts['tiny'], fill=0)

        right_start_x = half_width

        draw.text((right_start_x, y), "ПОДЫТОГ:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 15), "ИТОГ:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 30), "ПРИНЯТО:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 45), "СДАЧА:", font=self.fonts['tiny'], fill=0)

        subtotal_val = data['subtotal']
        total_val = data['total']
        accepted_val = cash_val if data['payment_type'] == "НАЛИЧНЫМИ" else data['total']
        change_val = data['cash_change'] if data['payment_type'] == "НАЛИЧНЫМИ" else 0

        right_edge_x = width - padding

        subtotal_str = f"{subtotal_val:.2f}"
        total_str = f"{total_val:.2f}"
        accepted_str = f"{accepted_val:.2f}"
        change_str = f"{change_val:.2f}"

        draw.text((right_edge_x - self.get_text_width(draw, subtotal_str, 'tiny'), y), subtotal_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, total_str, 'tiny'), y + 15), total_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, accepted_str, 'tiny'), y + 30), accepted_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, change_str, 'tiny'), y + 45), change_str, font=self.fonts['tiny'], fill=0)

        y += 65

        draw_line(y, 'dashed')
        y += 8

        half_width = width // 2

        draw.text((padding, y), "НДС 10%", font=self.fonts['tiny'], fill=0)

        nds_10_val = data['nds_10']
        nds_10_str = f"{nds_10_val:.2f}"
        left_sum_edge_x = half_width - 5
        draw.text((left_sum_edge_x - self.get_text_width(draw, nds_10_str, 'tiny'), y), nds_10_str, font=self.fonts['tiny'], fill=0)

        right_start_x = half_width
        draw.text((right_start_x, y), "НДС 20%", font=self.fonts['tiny'], fill=0)

        nds_20_val = data['nds_20']
        nds_20_str = f"{nds_20_val:.2f}"
        right_edge_x = width - padding
        draw.text((right_edge_x - self.get_text_width(draw, nds_20_str, 'tiny'), y), nds_20_str, font=self.fonts['tiny'], fill=0)

        y += 15

        draw_line(y, 'dashed')
        y += 10

        company_names = ["КОПЕЙКА", "ФРАНЧ", "АГРОТОРГ"]
        company = random.choice(company_names)

        draw.text((padding, y), f'ООО "{company}"', font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((padding, y), f"ИНН {data['shop']['tax_id']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((padding, y), f"Адрес: {data['shop']['address']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        date_str = data['date'].strftime("%d.%m.%Y %H:%M")
        draw.text((padding, y), f"Кассир: {data['cashier']}", font=self.fonts['tiny'], fill=0)
        date_width = self.get_text_width(draw, date_str, 'tiny')
        draw.text((width - padding - date_width, y), date_str, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        auto_num = ''.join([str(random.randint(0,9)) for _ in range(16)])
        auto_text = f"АВТОМАТ: {auto_num}"
        draw.text((padding, y), auto_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        cash_num = random.randint(1, 5)
        smena_num = data['smena_num']
        receipt_num = data['receipt_num']

        cash_text = f"Касса: {cash_num}"
        draw.text((padding, y), cash_text, font=self.fonts['tiny'], fill=0)

        prihod_text = "ПРИХОД"
        prihod_width = self.get_text_width(draw, prihod_text, 'tiny')
        draw.text((width - padding - prihod_width, y), prihod_text, font=self.fonts['tiny'], fill=0)

        smena_text = f"Смена: {smena_num}"
        chek_text = f"Чек: {receipt_num}"

        available_width = width - (padding * 2) - self.get_text_width(draw, cash_text, 'tiny') - prihod_width
        space_between = available_width // 4

        smena_x = padding + self.get_text_width(draw, cash_text, 'tiny') + space_between
        draw.text((smena_x, y), smena_text, font=self.fonts['tiny'], fill=0)

        chek_x = smena_x + self.get_text_width(draw, smena_text, 'tiny') + space_between
        draw.text((chek_x, y), chek_text, font=self.fonts['tiny'], fill=0)

        y += self.fonts['tiny'].size + 2

        draw_line(y, 'dashed')
        y += 8

        draw.text((padding, y), "Сайт ФНС www.nalog.gov.ru", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 5

        draw.text((padding, y), f"Система налогообложения: {data['tax_system']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 1
        draw.text((padding, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 1
        draw.text((padding, y), f"ЗН ФН: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 1
        draw.text((padding, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 1
        draw.text((padding, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 1
        draw.text((padding, y), f"ФД: {data['fd']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 10

        qr_size = 125
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data = qr_img.getdata()
        new_data = []
        for pixel in qr_data:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0,0,0,255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0,0), qr_img)

        qr_x = (width - qr_size) // 2
        img.paste(qr_with_paper, (qr_x, y))
        y += qr_size + 10

        self.draw_text_centered(draw, "СПАСИБО ЗА ПОКУПКУ!", y, 'small', width)
        y += self.fonts['small'].size + 10

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_vkusoland(self, data):
        """Отрисовка чека ВКУСОЛЕНД с уникальной структурой"""
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = 'ООО "ВКУСОЛЕНД"'
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        draw.text((name_x, y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 6

        addr_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        addr_text = f"{addr_code}, {data['shop']['address']}"
        self.draw_text_centered(draw, addr_text, y, 'small', width)
        y += self.fonts['small'].size + 8

        receipt_num = data['receipt_num']
        chek_text = f"Чек №: {receipt_num}"
        cashier_text = f"Кассир: {data['cashier']}"
        draw.text((padding, y), chek_text, font=self.fonts['small'], fill=0)
        cashier_width = self.get_text_width(draw, cashier_text, 'small')
        draw.text((width - padding - cashier_width, y), cashier_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        smena_num = data['smena_num']
        smena_text = f"СМЕНА №: {smena_num}"
        prihod_text = "ПРИХОД"
        datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")

        draw.text((padding, y), smena_text, font=self.fonts['small'], fill=0)
        prihod_x = padding + self.get_text_width(draw, smena_text, 'small') + 15
        draw.text((prihod_x, y), prihod_text, font=self.fonts['small'], fill=0)
        datetime_width = self.get_text_width(draw, datetime_str, 'small')
        draw.text((width - padding - datetime_width, y), datetime_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        sale_num = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        sale_text = f"ПРОДАЖА №: {sale_num}"
        self.draw_text_centered(draw, sale_text, y, 'small', width)
        y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 10

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            formula_text = f"{item['quantity']}.000 * {item['price']:.2f}"
            sum_text = f"= {item['total']:.2f}"

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            formula_width = self.get_text_width(draw, formula_text, 'small')
            formula_x = width - padding - formula_width - 60
            draw.text((formula_x, y), formula_text, font=self.fonts['small'], fill=0)

            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 4

        draw_line(y, 'dashed')
        y += 8

        items_count = len(data['items'])
        draw.text((padding, y), f"Позиций: {items_count}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), "ИТОГ:", font=self.fonts['bold'], fill=0)
        total_str = f"{data['total']:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold')
        draw.text((width - padding - total_width, y), total_str, font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 4

        discount_val = data.get('discount', data.get('total_discount', 0))
        draw.text((padding, y), "СКИДКИ:", font=self.fonts['small'], fill=0)
        discount_str = f"{discount_val:.2f}"
        discount_width = self.get_text_width(draw, discount_str, 'small')
        draw.text((width - padding - discount_width, y), discount_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw.text((padding, y), data['payment_type'], font=self.fonts['small'], fill=0)

        if data['payment_type'] == "НАЛИЧНЫМИ":
            cash_sum = f"{data['cash_received']:.2f}"
            cash_sum_width = self.get_text_width(draw, cash_sum, 'small')
            draw.text((width - padding - cash_sum_width, y), cash_sum, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

            draw.text((padding, y), "СДАЧА:", font=self.fonts['small'], fill=0)
            change = data['cash_received'] - data['total']
            if change < 0:
                change = 0
            change_str = f"{change:.2f}"
            change_width = self.get_text_width(draw, change_str, 'small')
            draw.text((width - padding - change_width, y), change_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4
        else:
            sum_str = f"{data['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_str, 'small')
            draw.text((width - padding - sum_width, y), sum_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Наш сайт: www.vkusoland.ru", y, 'small', width)
        y += self.fonts['small'].size + 6

        phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        phone_text = f"Телефон для Ваших отзывов и предложений +7 (988) {phone_suffix}"
        self.draw_text_centered(draw, phone_text, y, 'small', width)
        y += self.fonts['small'].size + 12

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_dvoyka(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = "ДВОЙКА"
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        draw.text((name_x, y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 6

        self.draw_text_centered(draw, "Добро пожаловать!", y, 'small', width)
        y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Кассовый чек", y, 'small', width)
        y += self.fonts['small'].size + 8

        draw.text((padding, y), "Приход", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), 'ООО "Двойка"', font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), f"ИНН: {data['shop']['tax_id']}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        draw.text((padding, y), f"Кассир: {data['cashier']}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        shop_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        draw.text((padding, y), f"Магазин ID: {shop_id}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        receipt_num = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        draw.text((padding, y), f"Чек №: {receipt_num}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        self.draw_text_centered(draw, "Продажа", y, 'small', width)
        y += self.fonts['small'].size + 8

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            qty_price = f"{item['quantity']} * {item['price']:.2f}"
            sum_text = f"={item['total']:.2f}"

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            qty_price_width = self.get_text_width(draw, qty_price, 'small')
            qty_price_x = width - padding - qty_price_width - 50
            draw.text((qty_price_x, y), qty_price, font=self.fonts['small'], fill=0)

            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 4

        y += 4

        discount_val = data.get('discount', data.get('total_discount', 0))
        draw.text((padding, y), "Скидка:", font=self.fonts['small'], fill=0)
        discount_str = f"{discount_val:.2f}"
        discount_width = self.get_text_width(draw, discount_str, 'small')
        draw.text((width - padding - discount_width, y), discount_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4
        draw.text((padding, y), "Итог:", font=self.fonts['bold'], fill=0)
        total_str = f"{data['total']:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold')
        draw.text((width - padding - total_width, y), total_str, font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 4

        draw.text((padding, y), "Оплата:", font=self.fonts['small'], fill=0)

        if data['payment_type'] == "НАЛИЧНЫМИ":
            payment_text = "Наличный расчёт"
            draw.text((padding, y + self.fonts['small'].size + 4), payment_text, font=self.fonts['small'], fill=0)

            cash_sum = f"{data['cash_received']:.2f}"
            cash_sum_width = self.get_text_width(draw, cash_sum, 'small')
            draw.text((width - padding - cash_sum_width, y + self.fonts['small'].size + 4), cash_sum, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size * 2 + 8

            draw.text((padding, y), "Сдача:", font=self.fonts['small'], fill=0)
            change = data['cash_received'] - data['total']
            if change < 0:
                change = 0
            change_str = f"{change:.2f}"
            change_width = self.get_text_width(draw, change_str, 'small')
            draw.text((width - padding - change_width, y), change_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4
        else:
            payment_text = "Безналичный расчёт"
            draw.text((padding, y + self.fonts['small'].size + 4), payment_text, font=self.fonts['small'], fill=0)

            sum_str = f"{data['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_str, 'small')
            draw.text((width - padding - sum_width, y + self.fonts['small'].size + 4), sum_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size * 2 + 8
        y += 10
        self.draw_text_centered(draw, "Ждём Вас снова!", y, 'small', width)
        y += self.fonts['small'].size + 10

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_monetika(self, data):
      width = getattr(self, 'width', 384)
      padding = 12

      img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
      draw = ImageDraw.Draw(img)

      def draw_line(y, line_type='solid'):
          if line_type == 'solid':
              draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
          elif line_type == 'dashed':
              for x in range(padding, width - padding, 6):
                  draw.line([(x, y), (x + 3, y)], fill=0, width=1)

      y = 20

      bold_font = self.fonts['bold_large']
      shop_name = "Монетика"
      name_width = self.get_text_width(draw, shop_name, 'bold_large')
      name_x = (width - name_width) // 2
      draw.text((name_x, y), shop_name, font=bold_font, fill=0)
      draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
      y += self.fonts['bold_large'].size + 4

      ooo_text = 'ООО "Монетика"'
      self.draw_text_centered(draw, ooo_text, y, 'small', width)
      y += self.fonts['small'].size + 4

      self.draw_text_centered(draw, data['shop']['address'], y, 'small', width)
      y += self.fonts['small'].size + 4

      sale_num = random.randint(100, 999)
      chek_text = f"Кассовый чек на продажу № {sale_num}"
      self.draw_text_centered(draw, chek_text, y, 'small', width)
      y += self.fonts['small'].size + 8

      draw_line(y, 'dashed')
      y += 10

      for item in data['items']:
          name = item['name']
          if len(name) > 24:
              name = name[:22] + ".."
          price_qty = f"{item['price']:.2f} * {item['quantity']}"
          sum_text = f"={item['total']:.2f}"

          draw.text((padding, y), name, font=self.fonts['small'], fill=0)

          price_qty_width = self.get_text_width(draw, price_qty, 'small')
          price_qty_x = width - padding - price_qty_width - 50
          draw.text((price_qty_x, y), price_qty, font=self.fonts['small'], fill=0)

          sum_width = self.get_text_width(draw, sum_text, 'small')
          sum_x = width - padding - sum_width
          draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

          y += self.fonts['small'].size + 4

      y += 4

      discount_val = data.get('discount', data.get('total_discount', 0))
      draw.text((padding, y), "Скидка:", font=self.fonts['small'], fill=0)
      discount_str = f"{discount_val:.2f}"
      discount_width = self.get_text_width(draw, discount_str, 'small')
      draw.text((width - padding - discount_width, y), discount_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      draw.text((padding, y), "Итого:", font=self.fonts['small'], fill=0)
      total_str = f"={data['total']:.2f}"
      total_width = self.get_text_width(draw, total_str, 'small')
      draw.text((width - padding - total_width, y), total_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      draw_line(y, 'dashed')
      y += 8

      draw.text((padding, y), "Итого к оплате:", font=self.fonts['small'], fill=0)
      total_pay_str = f"={data['total']:.2f}"
      total_pay_width = self.get_text_width(draw, total_pay_str, 'small')
      draw.text((width - padding - total_pay_width, y), total_pay_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      if data['payment_type'] == "НАЛИЧНЫМИ":
          payment_text = "Наличными"
          payment_sum = f"={data['cash_received']:.2f}"
      else:
          payment_text = "Безналичными"
          payment_sum = f"={data['total']:.2f}"

      draw.text((padding, y), payment_text, font=self.fonts['small'], fill=0)
      payment_sum_width = self.get_text_width(draw, payment_sum, 'small')
      draw.text((width - padding - payment_sum_width, y), payment_sum, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 12
      qr_size = 110
      qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
      qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
      qr.make(fit=True)
      qr_img = qr.make_image(fill_color="black", back_color="white")
      qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

      paper_color = img.getpixel((padding, y))
      qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
      qr_img = qr_img.convert('RGBA')
      qr_data = qr_img.getdata()
      new_data = []
      for pixel in qr_data:
          if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
              new_data.append((0, 0, 0, 255))
          else:
              new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
      qr_img.putdata(new_data)
      qr_with_paper.paste(qr_img, (0, 0), qr_img)

      qr_x = (width - qr_size) // 2
      img.paste(qr_with_paper, (qr_x, y))
      y += qr_size + 12
      fn_text = f"ФН: {data['fn']}"
      fp_text = f"ФП: {data['fp']}"
      draw.text((padding, y), fn_text, font=self.fonts['tiny'], fill=0)
      fp_width = self.get_text_width(draw, fp_text, 'tiny')
      draw.text((width - padding - fp_width, y), fp_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2
      fd_text = f"ФД: {data['fd']}"
      inn_text = f"ИНН: {data['shop']['tax_id']}"
      draw.text((padding, y), fd_text, font=self.fonts['tiny'], fill=0)
      inn_width = self.get_text_width(draw, inn_text, 'tiny')
      draw.text((width - padding - inn_width, y), inn_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2
      datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")
      draw.text((padding, y), datetime_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 8

      img_array = np.array(img.convert('L'))
      non_empty_rows = np.where(img_array < 250)[0]
      if len(non_empty_rows) > 0:
          actual_bottom = max(non_empty_rows) + 20
      else:
          actual_bottom = y
      img = img.crop((0, 0, width, min(actual_bottom, 2000)))

      return img, data['extraction_data']

    def draw_receipt_allenta(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20
        bold_font = self.fonts['bold_large']
        shop_name = "АЛЛЕНТА"
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        draw.text((name_x, y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 4

        ooo_text = "ООО \"Аллента\""
        self.draw_text_centered(draw, ooo_text, y, 'tiny', width)
        y += self.fonts['tiny'].size + 4

        addr_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        addr_text = f"{addr_code}, {data['shop']['address']}"
        self.draw_text_centered(draw, addr_text, y, 'tiny', width)
        y += self.fonts['tiny'].size + 8

        draw_line(y, 'dashed')
        y += 8

        cash_num = random.randint(1, 8)
        cash_text = f"Касса: {cash_num:04d}"
        cashier_text = f"Кассир: {data['cashier']}"

        draw.text((padding, y), cash_text, font=self.fonts['small'], fill=0)
        cashier_width = self.get_text_width(draw, cashier_text, 'small')
        draw.text((width - padding - cashier_width, y), cashier_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 6

        doc_num = random.randint(1000, 9999)
        smena_num = random.randint(1000, 9999)
        doc_text = f"Документ на продажу №: {doc_num}"
        smena_text = f"Смена №: {smena_num}"

        draw.text((padding, y), doc_text, font=self.fonts['small'], fill=0)
        smena_width = self.get_text_width(draw, smena_text, 'small')
        draw.text((width - padding - smena_width, y), smena_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 8

        left_text = "Кассовый чек (Приход)"
        right_text = "*Продажа товара*"
        draw.text((padding, y), left_text, font=self.fonts['small'], fill=0)
        right_width = self.get_text_width(draw, right_text, 'small')
        draw.text((width - padding - right_width, y), right_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 10

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            price_qty = f"{item['price']:.2f} * {item['quantity']}"
            sum_text = f"={item['total']:.2f}"
            vat_text = f"НДС {item['vat']}"

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            price_qty_width = self.get_text_width(draw, price_qty, 'small')
            price_qty_x = width - padding - price_qty_width - 50
            draw.text((price_qty_x, y), price_qty, font=self.fonts['small'], fill=0)

            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 2

            draw.text((padding + 5, y), vat_text, font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 4

        draw_line(y, 'dashed')
        y += 8

        draw.text((padding, y), "ИТОГО К ОПЛАТЕ:", font=self.fonts['bold'], fill=0)
        total_str = f"={data['total']:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold')
        draw.text((width - padding - total_width, y), total_str, font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 4
        payment_text = data['payment_type']
        draw.text((padding, y), payment_text, font=self.fonts['small'], fill=0)
        payment_sum_str = f"={data['total']:.2f}"
        payment_sum_width = self.get_text_width(draw, payment_sum_str, 'small')
        draw.text((width - padding - payment_sum_width, y), payment_sum_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        if data['payment_type'] == "НАЛИЧНЫМИ":
            cash_received = data['cash_received']
        else:
            cash_received = data['total']

        draw.text((padding, y), "ПОЛУЧЕНО:", font=self.fonts['small'], fill=0)
        cash_received_str = f"={cash_received:.2f}"
        cash_received_width = self.get_text_width(draw, cash_received_str, 'small')
        draw.text((width - padding - cash_received_width, y), cash_received_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        if data['payment_type'] == "НАЛИЧНЫМИ":
            cash_change = data['cash_change']
        else:
            cash_change = 0

        draw.text((padding, y), "СДАЧА:", font=self.fonts['small'], fill=0)
        cash_change_str = f"={cash_change:.2f}"
        cash_change_width = self.get_text_width(draw, cash_change_str, 'small')
        draw.text((width - padding - cash_change_width, y), cash_change_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        nds_total = data['nds_10'] + data['nds_20']
        draw.text((padding, y), "СУММА НДС:", font=self.fonts['small'], fill=0)
        nds_str = f"={nds_total:.2f}"
        nds_width = self.get_text_width(draw, nds_str, 'small')
        draw.text((width - padding - nds_width, y), nds_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 12

        self.draw_text_centered(draw, "Спасибо за покупку!", y, 'small', width)
        y += self.fonts['small'].size + 12

        qr_size = 110
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data = qr_img.getdata()
        new_data = []
        for pixel in qr_data:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0, 0, 0, 255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0, 0), qr_img)

        qr_x = (width - qr_size) // 2
        img.paste(qr_with_paper, (qr_x, y))
        y += qr_size + 12
        zn_text = f"ЗН ККТ: {data['fn_zav_num']}"
        fn_text = f"ФН: {data['fn']}"
        draw.text((padding, y), zn_text, font=self.fonts['tiny'], fill=0)
        fn_width = self.get_text_width(draw, fn_text, 'tiny')
        draw.text((width - padding - fn_width, y), fn_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        rn_text = f"РН ККТ: {data['kkt_reg_num']}"
        inn_text = f"ИНН: {data['shop']['tax_id']}"
        draw.text((padding, y), rn_text, font=self.fonts['tiny'], fill=0)
        inn_width = self.get_text_width(draw, inn_text, 'tiny')
        draw.text((width - padding - inn_width, y), inn_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        receipt_num = data['receipt_num']
        chek_text = f"ЧЕК: {receipt_num}"
        sno_text = f"СНО {data['tax_system']}"
        draw.text((padding, y), chek_text, font=self.fonts['tiny'], fill=0)
        sno_width = self.get_text_width(draw, sno_text, 'tiny')
        draw.text((width - padding - sno_width, y), sno_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        self.draw_text_centered(draw, "САЙТ ФНС: www.nalog.gov.ru", y, 'tiny', width)
        y += self.fonts['tiny'].size + 2

        datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")
        draw.text((padding, y), f"ДАТА ПРИХОДА: {datetime_str}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        fd_text = f"ФД: {data['fd']}"
        fp_text = f"ФП: {data['fp']}"
        draw.text((padding, y), fd_text, font=self.fonts['tiny'], fill=0)
        fp_width = self.get_text_width(draw, fp_text, 'tiny')
        draw.text((width - padding - fp_width, y), fp_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 8

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_perekrestki(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = "Перекрестки"
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        name_y = y

        circle_size = 8
        circle_gap = 2
        circles_x = name_x - 38
        cx1 = circles_x
        cy1 = name_y + circle_size // 2
        draw.ellipse([cx1, cy1, cx1 + circle_size, cy1 + circle_size], fill=0, outline=0)
        cx2 = circles_x + circle_size + circle_gap
        cy2 = name_y + circle_size // 2
        draw.ellipse([cx2, cy2, cx2 + circle_size, cy2 + circle_size], fill=None, outline=0, width=1)
        cx3 = circles_x + (circle_size + circle_gap) * 2
        cy3 = name_y + circle_size // 2
        draw.ellipse([cx3, cy3, cx3 + circle_size, cy3 + circle_size], fill=0, outline=0)

        draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 8

        hotline_text = f"******** Горячая линия: {self.hotline_number} ********"
        self.draw_text_centered(draw, hotline_text, y, 'tiny', width)
        y += self.fonts['tiny'].size + 8

        cash_num = random.randint(1, 12)
        doc_num = random.randint(1000, 9999)
        cash_text = f"Касса: {cash_num}"
        doc_text = f"Док: {doc_num}"
        draw.text((padding, y), cash_text, font=self.fonts['small'], fill=0)
        doc_width = self.get_text_width(draw, doc_text, 'small')
        draw.text((width - padding - doc_width, y), doc_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        for idx, item in enumerate(data['items'], 1):
            name = item['name']
            if len(name) > 20:
                name = name[:18] + ".."

            num_text = f"{idx}:"
            price_qty = f"{item['price']:.2f}*{item['quantity']:.3f}"
            sum_text = f"={item['total']:.2f}"

            draw.text((padding, y), num_text, font=self.fonts['small'], fill=0)

            name_x_pos = padding + self.get_text_width(draw, num_text, 'small') + 5
            draw.text((name_x_pos, y), name, font=self.fonts['small'], fill=0)

            price_qty_width = self.get_text_width(draw, price_qty, 'small')
            price_qty_x = width - padding - price_qty_width - 60
            draw.text((price_qty_x, y), price_qty, font=self.fonts['small'], fill=0)

            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 4

        y += 4

        draw.text((padding, y), "Промежуточный итог:", font=self.fonts['small'], fill=0)
        subtotal_str = f"{data['subtotal']:.2f}"
        subtotal_width = self.get_text_width(draw, subtotal_str, 'small')
        draw.text((width - padding - subtotal_width, y), subtotal_str, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        draw_line(y, 'dashed')
        y += 8

        half_width = width // 2

        draw.text((padding, y), "СКИДКА:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 15), "ОКРУГЛЕНИЕ:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 30), "НАЛИЧНЫМИ:", font=self.fonts['tiny'], fill=0)
        draw.text((padding, y + 45), "БЕЗНАЛИЧНЫМИ:", font=self.fonts['tiny'], fill=0)

        discount_val = data.get('discount', data.get('total_discount', 0))
        rounding_val = round(random.uniform(0, 0.99), 2)

        if data.get('payment_type') == "НАЛИЧНЫМИ":
            cash_val = data.get('cash_received', 0)
            cashless_val = 0.00
        else:
            cash_val = 0.00
            cashless_val = data.get('total', 0)

        left_sum_edge_x = half_width - 5

        discount_str = f"{discount_val:.2f}"
        rounding_str = f"{rounding_val:.2f}"
        cash_str = f"{cash_val:.2f}"
        cashless_str = f"{cashless_val:.2f}"

        draw.text((left_sum_edge_x - self.get_text_width(draw, discount_str, 'tiny'), y), discount_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, rounding_str, 'tiny'), y + 15), rounding_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, cash_str, 'tiny'), y + 30), cash_str, font=self.fonts['tiny'], fill=0)
        draw.text((left_sum_edge_x - self.get_text_width(draw, cashless_str, 'tiny'), y + 45), cashless_str, font=self.fonts['tiny'], fill=0)

        right_start_x = half_width

        draw.text((right_start_x, y), "ПОДЫТОГ:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 15), "ИТОГ:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 30), "ПРИНЯТО:", font=self.fonts['tiny'], fill=0)
        draw.text((right_start_x, y + 45), "СДАЧА:", font=self.fonts['tiny'], fill=0)

        subtotal_val = data.get('subtotal', 0)
        total_val = data.get('total', 0)

        if data.get('payment_type') == "НАЛИЧНЫМИ":
            accepted_val = data.get('cash_received', 0)
            change_val = max(0, accepted_val - total_val) 
        else:
            accepted_val = data.get('total', 0)
            change_val = 0.00

        right_edge_x = width - padding

        subtotal_str = f"{subtotal_val:.2f}"
        total_str = f"{total_val:.2f}"
        accepted_str = f"{accepted_val:.2f}"
        change_str = f"{change_val:.2f}"

        draw.text((right_edge_x - self.get_text_width(draw, subtotal_str, 'tiny'), y), subtotal_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, total_str, 'tiny'), y + 15), total_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, accepted_str, 'tiny'), y + 30), accepted_str, font=self.fonts['tiny'], fill=0)
        draw.text((right_edge_x - self.get_text_width(draw, change_str, 'tiny'), y + 45), change_str, font=self.fonts['tiny'], fill=0)

        y += 60

        draw_line(y, 'dashed')
        y += 8

        nds_10_val = data.get('nds_10', 0)
        nds_20_val = data.get('nds_20', 0)

        nds_rates = [10, 13, 15, 20]
        nds_rate = random.choice(nds_rates)

        if nds_rate == 10:
            nds_amount = nds_10_val
            nds_text = f"Сумма НДС 10%:"
        elif nds_rate == 13:
            nds_amount = round(data.get('total', 0) * 13/113, 2)
            nds_text = f"Сумма НДС 13%:"
        elif nds_rate == 15:
            nds_amount = round(data.get('total', 0) * 15/115, 2)
            nds_text = f"Сумма НДС 15%:"
        else:
            nds_amount = nds_20_val
            nds_text = f"Сумма НДС 20%:"

        left_sum_edge_x = half_width - 5

        draw.text((padding, y), nds_text, font=self.fonts['tiny'], fill=0)

        nds_amount_str = f"{nds_amount:.2f}"
        draw.text((left_sum_edge_x - self.get_text_width(draw, nds_amount_str, 'tiny'), y), nds_amount_str, font=self.fonts['tiny'], fill=0)

        y += self.fonts['tiny'].size + 8

        draw_line(y, 'dashed')
        y += 8

        draw.text((padding, y), 'АО "ТД Перекресток"', font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        inn_text = f"ИНН: {data['shop']['tax_id']}"
        sno_text = f"СНО: {data['tax_system']}"
        draw.text((padding, y), inn_text, font=self.fonts['tiny'], fill=0)
        sno_width = self.get_text_width(draw, sno_text, 'tiny')
        draw.text((width - padding - sno_width, y), sno_text, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((padding, y), data['shop']['address'], font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((padding, y), f"Кассир: {data['cashier']}", font=self.fonts['tiny'], fill=0)
        datetime_str = data['date'].strftime("%d.%m.%y %H:%M")
        datetime_width = self.get_text_width(draw, datetime_str, 'tiny')
        draw.text((width - padding - datetime_width, y), datetime_str, font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        cash_num = random.randint(1, 13)
        smena_num = random.randint(1000, 9999)
        receipt_num = random.randint(10000, 99999)

        draw.text((padding, y), f"Касса: {cash_num:02d}", font=self.fonts['tiny'], fill=0)
        draw.text((padding + 60, y), f"Смена: {smena_num}", font=self.fonts['tiny'], fill=0)
        draw.text((padding + 130, y), f"Чек: {receipt_num}", font=self.fonts['tiny'], fill=0)
        prihod_text = "ПРИХОД"
        prihod_width = self.get_text_width(draw, prihod_text, 'tiny')
        draw.text((width - padding - prihod_width, y), prihod_text, font=self.fonts['tiny'], fill=0)

        y += self.fonts['tiny'].size + 8

        draw_line(y, 'dashed')
        y += 8

        qr_start_y = y
        qr_size = 110

        left_x = padding

        draw.text((left_x, y), "Сайт ФНС: www.nalog.ru", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ЗН ККТ: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        draw.text((left_x, y), f"ФД: {data['fd']}", font=self.fonts['tiny'], fill=0)
        y += self.fonts['tiny'].size + 2

        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

        paper_color = img.getpixel((padding, qr_start_y))
        qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
        qr_img = qr_img.convert('RGBA')
        qr_data = qr_img.getdata()
        new_data = []
        for pixel in qr_data:
            if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                new_data.append((0, 0, 0, 255))
            else:
                new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
        qr_img.putdata(new_data)
        qr_with_paper.paste(qr_img, (0, 0), qr_img)

        qr_x = width - padding - qr_size
        img.paste(qr_with_paper, (qr_x, qr_start_y))

        y = max(y, qr_start_y + qr_size + 10)

        self.draw_text_centered(draw, "Спасибо за покупку!", y, 'small', width)
        y += self.fonts['small'].size + 10

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

    def draw_receipt_villazbuka(self, data):
      width = getattr(self, 'width', 384)
      padding = 12

      img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
      draw = ImageDraw.Draw(img)

      def draw_line(y, line_type='solid'):
          if line_type == 'solid':
              draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
          elif line_type == 'dashed':
              for x in range(padding, width - padding, 6):
                  draw.line([(x, y), (x + 3, y)], fill=0, width=1)

      y = 20

      bold_font = self.fonts['bold_large']
      shop_name = "Виллазбука"
      name_width = self.get_text_width(draw, shop_name, 'bold_large')
      name_x = (width - name_width) // 2
      draw.text((name_x, y), shop_name, font=bold_font, fill=0)
      draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
      y += self.fonts['bold_large'].size + 4

      ooo_text = 'ООО "Супермаркет Виллазбука"'
      self.draw_text_centered(draw, ooo_text, y, 'small', width)
      y += self.fonts['small'].size + 4

      inn_text = f"ИНН: {data['shop']['tax_id']}"
      self.draw_text_centered(draw, inn_text, y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      city = data['shop']['address'].split(',')[0] if ',' in data['shop']['address'] else data['shop']['address']
      zip_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
      city_text = f"{zip_code}, {city}"
      self.draw_text_centered(draw, city_text, y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      address_without_city = data['shop']['address'].split(',', 1)[1].strip() if ',' in data['shop']['address'] else data['shop']['address']
      self.draw_text_centered(draw, address_without_city, y, 'tiny', width)
      y += self.fonts['tiny'].size + 4

      check_num = random.randint(100, 999)
      check_text = f"Кассовый чек: {check_num} (Приход)"
      self.draw_text_centered(draw, check_text, y, 'small', width)
      y += self.fonts['small'].size + 8

      cash_num = random.randint(1000, 9999)
      cash_text = f"Касса: {cash_num}"
      cashier_text = f"Кассир: {data['cashier']}"
      draw.text((padding, y), cash_text, font=self.fonts['small'], fill=0)
      cashier_width = self.get_text_width(draw, cashier_text, 'small')
      draw.text((width - padding - cashier_width, y), cashier_text, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 8

      draw_line(y, 'dashed')
      y += 10
      for item in data['items']:
          name = item['name']
          if len(name) > 24:
              name = name[:22] + ".."

          price_qty = f"{item['price']:.2f} * {item['quantity']}"
          sum_text = f"{item['total']:.2f}"

          draw.text((padding, y), name, font=self.fonts['small'], fill=0)

          price_qty_width = self.get_text_width(draw, price_qty, 'small')
          price_qty_x = width - padding - price_qty_width - 50
          draw.text((price_qty_x, y), price_qty, font=self.fonts['small'], fill=0)

          sum_width = self.get_text_width(draw, sum_text, 'small')
          sum_x = width - padding - sum_width
          draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

          y += self.fonts['small'].size + 4

      y += 4

      vat_rates = ["10%", "15%", "18%"]
      vat_rate = random.choice(vat_rates)
      nds_amount = 0
      if vat_rate == "10%":
          nds_amount = round(data['total'] * 10/110, 2)
      elif vat_rate == "15%":
          nds_amount = round(data['total'] * 15/115, 2)
      elif vat_rate == "18%":
          nds_amount = round(data['total'] * 18/118, 2)

      draw.text((padding, y), f"в т.ч. НДС {vat_rate}:", font=self.fonts['tiny'], fill=0)
      nds_str = f"{nds_amount:.2f}"
      nds_width = self.get_text_width(draw, nds_str, 'tiny')
      draw.text((width - padding - nds_width, y), nds_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 4

      draw_line(y, 'dashed')
      y += 8

      draw.text((padding, y), "Сумма покупок:", font=self.fonts['small'], fill=0)
      subtotal_str = f"={data['subtotal']:.2f}"
      subtotal_width = self.get_text_width(draw, subtotal_str, 'small')
      draw.text((width - padding - subtotal_width, y), subtotal_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      self.draw_text_centered(draw, "Итого к оплате:", y, 'small', width)
      total_str = f"={data['total']:.2f}"
      total_width = self.get_text_width(draw, total_str, 'small')
      draw.text((width - padding - total_width, y), total_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      if data['payment_type'] == "НАЛИЧНЫМИ":
          payment_text = "Наличными"
          payment_sum = f"={data['cash_received']:.2f}"
      else:
          payment_text = "Безналичными"
          payment_sum = f"={data['total']:.2f}"

      self.draw_text_centered(draw, payment_text, y, 'small', width)
      payment_width = self.get_text_width(draw, payment_sum, 'small')
      draw.text((width - padding - payment_width, y), payment_sum, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 4

      if data['payment_type'] == "НАЛИЧНЫМИ":
          self.draw_text_centered(draw, "Сдача:", y, 'small', width)
          change = data['cash_received'] - data['total']
          if change < 0:
              change = 0
          change_str = f"={change:.2f}"
          change_width = self.get_text_width(draw, change_str, 'small')
          draw.text((width - padding - change_width, y), change_str, font=self.fonts['small'], fill=0)
          y += self.fonts['small'].size + 4

      discount_round = round(random.uniform(0, 0.99), 2)
      draw.text((padding, y), "Скидка на округление:", font=self.fonts['tiny'], fill=0)
      discount_round_str = f"{discount_round:.2f}"
      discount_round_width = self.get_text_width(draw, discount_round_str, 'tiny')
      draw.text((width - padding - discount_round_width, y), discount_round_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 4

      nds_10_amount = round(data['subtotal'] * 10/110, 2) if data['subtotal'] > 0 else 0
      self.draw_text_centered(draw, "в т.ч. НДС 10%:", y, 'tiny', width)
      nds_10_str = f"{nds_10_amount:.2f}"
      nds_10_width = self.get_text_width(draw, nds_10_str, 'tiny')
      draw.text((width - padding - nds_10_width, y), nds_10_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      nds_15_amount = round(data['subtotal'] * 15/115, 2) if data['subtotal'] > 0 else 0
      self.draw_text_centered(draw, "в т.ч. НДС 15%:", y, 'tiny', width)
      nds_15_str = f"{nds_15_amount:.2f}"
      nds_15_width = self.get_text_width(draw, nds_15_str, 'tiny')
      draw.text((width - padding - nds_15_width, y), nds_15_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      nds_18_amount = round(data['subtotal'] * 18/118, 2) if data['subtotal'] > 0 else 0
      self.draw_text_centered(draw, "в т.ч. НДС 18%:", y, 'tiny', width)
      nds_18_str = f"{nds_18_amount:.2f}"
      nds_18_width = self.get_text_width(draw, nds_18_str, 'tiny')
      draw.text((width - padding - nds_18_width, y), nds_18_str, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 4

      draw.text((padding, y), "Скидка с покупок:", font=self.fonts['small'], fill=0)
      discount_val = data.get('discount', data.get('total_discount', 0))
      discount_str = f"{discount_val:.2f}"
      discount_width = self.get_text_width(draw, discount_str, 'small')
      draw.text((width - padding - discount_width, y), discount_str, font=self.fonts['small'], fill=0)
      y += self.fonts['small'].size + 8

      self.draw_text_centered(draw, "Спасибо за покупку!", y, 'small', width)
      y += self.fonts['small'].size + 8

      self.draw_text_centered(draw, "Служба клиентской поддержки:", y, 'tiny', width)
      y += self.fonts['tiny'].size + 2

      phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
      phone_suffix2 = ''.join([str(random.randint(0, 9)) for _ in range(2)])
      phone_suffix3 = ''.join([str(random.randint(0, 9)) for _ in range(2)])
      phone_text = f"+7 (495) {phone_suffix}-{phone_suffix2}-{phone_suffix3}"
      self.draw_text_centered(draw, phone_text, y, 'tiny', width)
      y += self.fonts['tiny'].size + 2

      self.draw_text_centered(draw, "Ежедневно с 09:00 до 21:00", y, 'tiny', width)
      y += self.fonts['tiny'].size + 2

      self.draw_text_centered(draw, "www.villazbuka.ru", y, 'tiny', width)
      y += self.fonts['tiny'].size + 2

      self.draw_text_centered(draw, "Проверьте чек на сайте: www.nalog.ru", y, 'tiny', width)
      y += self.fonts['tiny'].size + 8

      qr_size = 110
      qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
      qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
      qr.make(fit=True)
      qr_img = qr.make_image(fill_color="black", back_color="white")
      qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

      paper_color = img.getpixel((padding, y))
      qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
      qr_img = qr_img.convert('RGBA')
      qr_data = qr_img.getdata()
      new_data = []
      for pixel in qr_data:
          if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
              new_data.append((0, 0, 0, 255))
          else:
              new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
      qr_img.putdata(new_data)
      qr_with_paper.paste(qr_img, (0, 0), qr_img)

      qr_x = (width - qr_size) // 2
      img.paste(qr_with_paper, (qr_x, y))
      y += qr_size + 12

      zn_text = f"ЗН ККТ: {data['fn_zav_num']}"
      fn_text = f"ФН: {data['fn']}"
      draw.text((padding, y), zn_text, font=self.fonts['tiny'], fill=0)
      fn_width = self.get_text_width(draw, fn_text, 'tiny')
      draw.text((width - padding - fn_width, y), fn_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      rn_text = f"РН ККТ: {data['kkt_reg_num']}"
      inn_text = f"ИНН: {data['shop']['tax_id']}"
      draw.text((padding, y), rn_text, font=self.fonts['tiny'], fill=0)
      inn_width = self.get_text_width(draw, inn_text, 'tiny')
      draw.text((width - padding - inn_width, y), inn_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      sno_text = f"СНО {data['tax_system']}"
      draw.text((padding, y), sno_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      datetime_str = data['date'].strftime("%d.%m.%Y %H:%M")
      smena_num = data['smena_num']
      receipt_num = data['receipt_num']

      draw.text((padding, y), datetime_str, font=self.fonts['tiny'], fill=0)

      smena_chek_text = f"Смена: {smena_num}  Чек: {receipt_num}"
      smena_chek_width = self.get_text_width(draw, smena_chek_text, 'tiny')
      draw.text((width - padding - smena_chek_width, y), smena_chek_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 2

      fd_text = f"ФД: {data['fd']}"
      fp_text = f"ФП: {data['fp']}"
      draw.text((padding, y), fd_text, font=self.fonts['tiny'], fill=0)
      fp_width = self.get_text_width(draw, fp_text, 'tiny')
      draw.text((width - padding - fp_width, y), fp_text, font=self.fonts['tiny'], fill=0)
      y += self.fonts['tiny'].size + 8

      img_array = np.array(img.convert('L'))
      non_empty_rows = np.where(img_array < 250)[0]
      if len(non_empty_rows) > 0:
          actual_bottom = max(non_empty_rows) + 20
      else:
          actual_bottom = y
      img = img.crop((0, 0, width, min(actual_bottom, 2000)))

      return img, data['extraction_data']

    def draw_receipt(self, data):
        if data['shop']['name'] == "ШЕСТЕРОЧКА":
            return self.draw_receipt_shesterochka(data)
        if data['shop']['name'] == "СЕМЬ ДОРОГ":
            return self.draw_receipt_semidorog(data)
        if data['shop']['name'] == "СТАРТ":
            return self.draw_receipt_start(data)
        if data['shop']['name'] == "ВКУСОЛЕНД":
          return self.draw_receipt_vkusoland(data)
        if data['shop']['name'] == "АЛЛЕНТА":
          return self.draw_receipt_allenta(data)
        if data['shop']['name'] == "АШАНЧИК":
          return self.draw_receipt_ashanchik(data)
        if data['shop']['name'] == "ДВОЙКА":
          return self.draw_receipt_dvoyka(data)
        if data['shop']['name'] == "МОНЕТИКА":
          return self.draw_receipt_monetika(data)
        if data['shop']['name'] == "ВИЛЛАЗБУКА":
          return self.draw_receipt_villazbuka(data)
        if data['shop']['name'] == "ПЕРЕКРЕСТКИ":
          return self.draw_receipt_perekrestki(data)
        if data['shop']['name'] == "МАГНАТ":
          return self.draw_receipt_magnat(data)
        if data['shop']['type'] == "pharmacy":
          return self.draw_receipt_pharmacy(data)

        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        shop_name = data['shop']['name']

        line1_type = 'solid'
        line2_type = 'solid'
        line3_type = 'dashed'

        if shop_name in ["ШЕСТЕРОЧКА", "ДВОЙКА"]:
            line1_type = 'none'
            line2_type = 'dashed'
            line3_type = 'dashed'
        elif shop_name == "МАГНАТ":
            line1_type = 'solid'
            line2_type = 'solid'
            line3_type = 'solid'
        elif shop_name == "АШАНЧИК":
            line1_type = 'none'
            line2_type = 'none'
            line3_type = 'none'
        elif shop_name in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
            line1_type = 'dashed'
            line2_type = 'dashed'
            line3_type = 'none'
        elif shop_name == "ПЕРЕКРЕСТКИ":
            line1_type = 'none'
            line2_type = 'none'
            line3_type = 'dashed'
        else:
            line1_type = random.choice(['solid', 'dashed', 'none'])
            line2_type = random.choice(['solid', 'dashed', 'none'])
            line3_type = random.choice(['solid', 'dashed'])

        y = 20

        # ========== 1. ШАПКА ==========
        shop_name = data['shop']['name']

        if shop_name == "МАГНАТ":
            bold_font = self.fonts['bold_large']
            name_width = self.get_text_width(draw, shop_name, 'bold_large')
            name_x = (width - name_width) // 2
            name_y = y
            m_x = name_x - 25
            m_y = name_y
            draw.text((m_x, m_y), "М", font=bold_font, fill=0)
            draw.text((m_x + 1, m_y), "М", font=bold_font, fill=0)
            m_bbox = draw.textbbox((m_x, m_y), "М", font=bold_font)
            m_left = m_bbox[0]
            m_top = m_bbox[1]
            m_right = m_bbox[2]
            m_bottom = m_bbox[3]
            padding_around_m = 3
            square_left = m_left - padding_around_m
            square_top = m_top - padding_around_m
            square_right = m_right + padding_around_m
            square_bottom = m_bottom + padding_around_m
            for i in range(2):
                draw.rectangle([square_left - i, square_top - i, square_right + i, square_bottom + i], outline=0, width=1)
            draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
            draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        elif shop_name == "ПЕРЕКРЕСТКИ":
            bold_font = self.fonts['bold_large']
            name_width = self.get_text_width(draw, shop_name, 'bold_large')
            name_x = (width - name_width) // 2
            name_y = y
            circle_size = 8
            circle_gap = 2
            circles_x = name_x - 38
            cx1 = circles_x
            cy1 = name_y + circle_size // 2
            draw.ellipse([cx1, cy1, cx1 + circle_size, cy1 + circle_size], fill=0, outline=0)
            cx2 = circles_x + circle_size + circle_gap
            cy2 = name_y + circle_size // 2
            draw.ellipse([cx2, cy2, cx2 + circle_size, cy2 + circle_size], fill=None, outline=0, width=1)
            cx3 = circles_x + (circle_size + circle_gap) * 2
            cy3 = name_y + circle_size // 2
            draw.ellipse([cx3, cy3, cx3 + circle_size, cy3 + circle_size], fill=0, outline=0)
            draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
            draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        elif shop_name == "ШЕСТЕРОЧКА":
            bold_font = self.fonts['bold_large']
            name_width = self.get_text_width(draw, shop_name, 'bold_large')
            name_x = (width - name_width) // 2
            name_y = y
            icon_size = self.fonts['bold_large'].size + 4
            circle_x = name_x - icon_size - 8
            circle_y = name_y - 2
            draw.ellipse([circle_x, circle_y, circle_x + icon_size, circle_y + icon_size], fill=0, outline=0)
            draw.text((circle_x + icon_size//2 - 6 + 1, circle_y + icon_size//2 - 8 + 1), "6", font=bold_font, fill=(80,80,80))
            draw.text((circle_x + icon_size//2 - 6, circle_y + icon_size//2 - 8), "6", font=bold_font, fill=(255,255,255))
            draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
            draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)
        else:
            bold_font = self.fonts['bold_large']
            name_width = self.get_text_width(draw, shop_name, 'bold_large')
            name_x = (width - name_width) // 2
            name_y = y
            draw.text((name_x, name_y), shop_name, font=bold_font, fill=0)
            draw.text((name_x + 1, name_y), shop_name, font=bold_font, fill=0)

        y += self.fonts['bold_large'].size + 4

        if "hotline" in data['shop'].get('features', []):
            if data['shop']['name'] == "ПЕРЕКРЕСТКИ":
                hotline_text = f"******** Горячая линия: {self.hotline_number} ********"
            else:
                hotline_text = f"Горячая линия: {self.hotline_number}"
            self.draw_text_centered(draw, hotline_text, y, 'tiny', width)
            y += self.fonts['tiny'].size + 2

        if shop_name != "ШЕСТЕРОЧКА":
            if shop_name in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
                self.draw_text_centered(draw, data['shop']['address'], y, 'tiny', width)
                y += self.fonts['tiny'].size + 4
            else:
                self.draw_text_centered(draw, data['shop']['address'], y, 'tiny', width)
                y += self.fonts['tiny'].size + 1
                self.draw_text_centered(draw, f"Тел.: {data['shop']['phone']}", y, 'tiny', width)
                y += self.fonts['tiny'].size + 1
                self.draw_text_centered(draw, f"ИНН {data['shop']['tax_id']}", y, 'tiny', width)
                y += self.fonts['tiny'].size + 4

        if line1_type != 'none':
            draw_line(y, line1_type)
        y += 3

        date_str = data['date'].strftime("%d.%m.%Y %H:%M")
        receipt_text = f"ЧЕК: {data['receipt_num']}"
        y += self.draw_text_two_columns(draw, date_str, receipt_text, y, 'tiny', 'tiny', width, padding)
        y += 2

        smena_text = f"СМЕНА: {data['smena_num']}"
        cashier_text = f"КАССИР: {data['cashier']}"
        y += self.draw_text_two_columns(draw, smena_text, cashier_text, y, 'tiny', 'tiny', width, padding)
        y += 4

        if shop_name == "ШЕСТЕРОЧКА":
            self.draw_text_centered(draw, data['shop']['address'], y, 'tiny', width)
            y += self.fonts['tiny'].size + 1
            self.draw_text_centered(draw, f"Тел.: {data['shop']['phone']}", y, 'tiny', width)
            y += self.fonts['tiny'].size + 1
            self.draw_text_centered(draw, f"ИНН {data['shop']['tax_id']}", y, 'tiny', width)
            y += self.fonts['tiny'].size + 4

        draw.text((padding, y), "ТОВАР", font=self.fonts['bold'], fill=0)

        col_price = width - padding - 130
        col_qty = width - padding - 85
        col_sum = width - padding - 45
        col_price_width = 45
        col_qty_width = 45
        col_sum_width = 40

        price_title = "ЦЕНА"
        price_title_width = self.get_text_width(draw, price_title, 'tiny')
        price_center_x = col_price + col_price_width // 2 - price_title_width // 2
        draw.text((price_center_x, y), price_title, font=self.fonts['tiny'], fill=0)

        col_title = "КОЛ-ВО"
        col_title_width = self.get_text_width(draw, col_title, 'tiny')
        col_title_center_x = col_qty + col_qty_width // 2 - col_title_width // 2
        draw.text((col_title_center_x, y), col_title, font=self.fonts['tiny'], fill=0)

        sum_title = "ИТОГО"
        sum_title_width = self.get_text_width(draw, sum_title, 'tiny')
        sum_center_x = col_sum + col_sum_width // 2 - sum_title_width // 2
        draw.text((sum_center_x, y), sum_title, font=self.fonts['tiny'], fill=0)

        y += self.fonts['bold'].size + 2

        for item in data['items']:
            name = item['name']
            max_name_len = 24
            if len(name) > max_name_len:
                name = name[:max_name_len-2] + ".."

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            price_text = f"{item['price']:.2f}"
            price_width = self.get_text_width(draw, price_text, 'small')
            price_center_x = col_price + col_price_width // 2 - price_width // 2
            draw.text((price_center_x, y), price_text, font=self.fonts['small'], fill=0)

            qty_text = str(item['quantity'])
            qty_width = self.get_text_width(draw, qty_text, 'small')
            qty_center_x = col_qty + col_qty_width // 2 - qty_width // 2
            draw.text((qty_center_x, y), qty_text, font=self.fonts['small'], fill=0)

            sum_text = f"{item['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_center_x = col_sum + col_sum_width // 2 - sum_width // 2
            draw.text((sum_center_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 1

            if shop_name not in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
                vat_text = f"  НДС {item['vat']}"
                draw.text((padding + 5, y), vat_text, font=self.fonts['tiny'], fill=0)
                y += self.fonts['tiny'].size + 1
            else:
                y += 1

        if line2_type != 'none':
            draw_line(y, line2_type)
        y += 3

        draw.text((padding, y), "ПОДЫТОГ:", font=self.fonts['small'], fill=0)
        draw.text((col_sum, y), f"{data['subtotal']:.2f}", font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 1

        if data['discount'] > 0:
            draw.text((padding, y), "СКИДКА:", font=self.fonts['small'], fill=0)
            draw.text((col_sum, y), f"-{data['discount']:.2f}", font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 1

        draw.text((padding, y), "ИТОГО:", font=self.fonts['bold'], fill=0)
        draw.text((col_sum, y), f"{data['total']:.2f}", font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 2

        if shop_name not in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
            if data['nds_20'] > 0:
                draw.text((padding, y), "В т.ч. НДС 20%:", font=self.fonts['tiny'], fill=0)
                draw.text((col_sum, y), f"{data['nds_20']:.2f}", font=self.fonts['tiny'], fill=0)
                y += self.fonts['tiny'].size + 1
            if data['nds_10'] > 0:
                draw.text((padding, y), "В т.ч. НДС 10%:", font=self.fonts['tiny'], fill=0)
                draw.text((col_sum, y), f"{data['nds_10']:.2f}", font=self.fonts['tiny'], fill=0)
                y += self.fonts['tiny'].size + 1
        else:
            y += 2

        y += 2
        draw.text((padding, y), data['payment_type'], font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 1

        is_pharmacy = shop_name in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]

        if data['payment_type'] == "НАЛИЧНЫМИ" and data['cash_received']:
            draw.text((padding, y), "ВНЕСЕНО:", font=self.fonts['tiny'], fill=0)
            draw.text((col_sum, y), f"{data['cash_received']:.2f}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), "СДАЧА:", font=self.fonts['tiny'], fill=0)
            draw.text((col_sum, y), f"{data['cash_change']:.2f}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 3

        if data['payment_type'] == "БАНКОВСКОЙ КАРТОЙ" and data.get('card_data'):
            cd = data['card_data']
            draw.text((padding, y), "ОДОБРЕНО", font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 1
            draw.text((padding, y), f"{cd['card_type']} {cd['card_mask']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"RRN: {cd['rrn']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ТЕРМИНАЛ: {cd['terminal']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 3

        if data.get('bonus_text'):
            if shop_name in ["МАГНАТ", "ШЕСТЕРОЧКА", "ДВОЙКА"]:
                self.draw_text_centered(draw, data['bonus_text'], y, 'small', width)
            else:
                draw.text((padding, y), data['bonus_text'], font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 3

        y += 2

        if is_pharmacy:
            qr_y_start = y

            draw.text((padding, y), f"СИСТЕМА НАЛОГООБЛОЖЕНИЯ: {data['tax_system']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            y += 2
            draw.text((padding, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ЗН ФН: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФД: {data['fd']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 3

            qr_size = 100
            qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
            qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

            paper_color = img.getpixel((padding, qr_y_start))
            qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
            qr_img = qr_img.convert('RGBA')
            qr_data = qr_img.getdata()
            new_data = []
            for pixel in qr_data:
                if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                    new_data.append((0, 0, 0, 255))
                else:
                    new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
            qr_img.putdata(new_data)
            qr_with_paper.paste(qr_img, (0, 0), qr_img)

            qr_x = width - padding - qr_size
            img.paste(qr_with_paper, (qr_x, qr_y_start))

        else:
            draw.text((padding, y), f"СИСТЕМА НАЛОГООБЛОЖЕНИЯ: {data['tax_system']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ЧАСОВАЯ ЗОНА: MSK", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 2
            draw.text((padding, y), f"РН ККТ: {data['kkt_reg_num']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ЗН ФН: {data['fn_zav_num']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФН: {data['fn']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФП: {data['fp']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 1
            draw.text((padding, y), f"ФД: {data['fd']}", font=self.fonts['tiny'], fill=0)
            y += self.fonts['tiny'].size + 3

        if shop_name in ["ШЕСТЕРОЧКА", "ДВОЙКА"]:
            self.draw_text_centered(draw, "www.nalog.gov.ru", y, 'tiny', width)
            y += self.fonts['tiny'].size + 5

        if not is_pharmacy:
            qr_start_y = y
            qr_size = 125

            qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
            qr.add_data(f"https://proverkachecka.com/check?{data['qr_string']}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS).convert('RGB')

            paper_color = img.getpixel((padding, qr_start_y))
            qr_with_paper = Image.new('RGB', (qr_size, qr_size), paper_color)
            qr_img = qr_img.convert('RGBA')
            qr_data = qr_img.getdata()
            new_data = []
            for pixel in qr_data:
                if pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50:
                    new_data.append((0, 0, 0, 255))
                else:
                    new_data.append((paper_color[0], paper_color[1], paper_color[2], 0))
            qr_img.putdata(new_data)
            qr_with_paper.paste(qr_img, (0, 0), qr_img)

            qr_x = (width - qr_size) // 2
            img.paste(qr_with_paper, (qr_x, qr_start_y))
            y = qr_start_y + qr_size + 5

        y += 3

        if is_pharmacy:
            draw.text((padding, y), "СПАСИБО ЗА ПОКУПКУ!", font=self.fonts['small'], fill=0)
        else:
            self.draw_text_centered(draw, "СПАСИБО ЗА ПОКУПКУ!", y, 'small', width)
        y += self.fonts['small'].size + 3

        if shop_name in ["АПТЕКА 37.7", "РИГЛАЙФ", "ЗДОРОВУМ", "ФАРМТЭК"]:
            if is_pharmacy:
                draw.text((padding, y), f"Тел.: {data['shop']['phone']}", font=self.fonts['tiny'], fill=0)
                y += self.fonts['tiny'].size + 1
                draw.text((padding, y), f"ИНН {data['shop']['tax_id']}", font=self.fonts['tiny'], fill=0)
            else:
                self.draw_text_centered(draw, f"Тел.: {data['shop']['phone']}", y, 'tiny', width)
                y += self.fonts['tiny'].size + 1
                self.draw_text_centered(draw, f"ИНН {data['shop']['tax_id']}", y, 'tiny', width)
            y += self.fonts['tiny'].size + 3

        if shop_name == "МАГНАТ":
            self.draw_text_centered(draw, "www.nalog.gov.ru", y, 'tiny', width)
            y += self.fonts['tiny'].size + 5

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y + 10
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        if random.random() > 0.7:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(random.uniform(0.94, 1.02))

        return img, data['extraction_data']

    def draw_receipt_ashanchik(self, data):
        width = getattr(self, 'width', 384)
        padding = 12

        img = Image.new('RGB', (width, 2000), color=random.choice(self.paper_colors))
        draw = ImageDraw.Draw(img)

        def draw_line(y, line_type='solid'):
            if line_type == 'solid':
                draw.line([(padding, y), (width - padding, y)], fill=0, width=1)
            elif line_type == 'dashed':
                for x in range(padding, width - padding, 6):
                    draw.line([(x, y), (x + 3, y)], fill=0, width=1)

        y = 20

        bold_font = self.fonts['bold_large']
        shop_name = 'ООО "Ашанчик"'
        name_width = self.get_text_width(draw, shop_name, 'bold_large')
        name_x = (width - name_width) // 2
        draw.text((name_x, y), shop_name, font=bold_font, fill=0)
        draw.text((name_x + 1, y), shop_name, font=bold_font, fill=0)
        y += self.fonts['bold_large'].size + 6

        self.draw_text_centered(draw, data['shop']['address'], y, 'small', width)
        y += self.fonts['small'].size + 4

        phone_suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        phone_text = f"8-898-{phone_suffix[:3]}-{phone_suffix[3:5]}-{phone_suffix[5:7]}"
        full_phone_text = f"{phone_text}  звонок бесплатный"
        self.draw_text_centered(draw, full_phone_text, y, 'small', width)
        y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Информация о нас на www.auchanchik.ru", y, 'small', width)
        y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Часы работы: 8:00 - 23:00", y, 'small', width)
        y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Сохраняйте ваш чек для возврата покупок", y, 'small', width)
        y += self.fonts['small'].size + 6

        self.draw_text_centered(draw, "СПАСИБО ЗА ПОКУПКУ!", y, 'small', width)
        y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "ЖДЁМ ВАС СНОВА!", y, 'small', width)
        y += self.fonts['small'].size + 8

        sale_text = "Продажа"
        sale_num = f"#{random.randint(1000, 9999)}/{random.randint(10000, 99999)}"
        draw.text((padding, y), sale_text, font=self.fonts['small'], fill=0)
        sale_num_width = self.get_text_width(draw, sale_num, 'small')
        draw.text((width - padding - sale_num_width, y), sale_num, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        operator_text = f"Оператор: {data['cashier']}"
        draw.text((padding, y), operator_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 4

        dept_num = random.randint(100, 999)
        dept_text = f"Отдел: {dept_num}"
        draw.text((padding, y), dept_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 8

        trans_num1 = random.randint(10, 99)
        trans_num2 = random.randint(1000000, 9999999)
        trans_text = f"Номер транзакции: {trans_num1}/{trans_num2}"
        draw.text((padding, y), trans_text, font=self.fonts['small'], fill=0)
        y += self.fonts['small'].size + 12

        for item in data['items']:
            name = item['name']
            if len(name) > 24:
                name = name[:22] + ".."

            price_qty = f"{item['price']:.2f}*{item['quantity']}"

            draw.text((padding, y), name, font=self.fonts['small'], fill=0)

            price_qty_width = self.get_text_width(draw, price_qty, 'small')
            price_qty_x = width - padding - price_qty_width - 80
            draw.text((price_qty_x, y), price_qty, font=self.fonts['small'], fill=0)

            sum_text = f"{item['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_text, 'small')
            sum_x = width - padding - sum_width
            draw.text((sum_x, y), sum_text, font=self.fonts['small'], fill=0)

            y += self.fonts['small'].size + 4

        y += 4

        draw.text((padding, y), "ИТОГ:", font=self.fonts['bold'], fill=0)
        total_str = f"{data['total']:.2f}"
        total_width = self.get_text_width(draw, total_str, 'bold')
        draw.text((width - padding - total_width, y), total_str, font=self.fonts['bold'], fill=0)
        y += self.fonts['bold'].size + 4

        draw.text((padding, y), data['payment_type'], font=self.fonts['small'], fill=0)

        if data['payment_type'] == "НАЛИЧНЫМИ":
            cash_sum = f"{data['cash_received']:.2f}"
            cash_sum_width = self.get_text_width(draw, cash_sum, 'small')
            draw.text((width - padding - cash_sum_width, y), cash_sum, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

            draw.text((padding, y), "СДАЧА:", font=self.fonts['small'], fill=0)
            change = data['cash_received'] - data['total']
            if change < 0:
                change = 0
            change_str = f"{change:.2f}"
            change_width = self.get_text_width(draw, change_str, 'small')
            draw.text((width - padding - change_width, y), change_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4
        else:
            sum_str = f"{data['total']:.2f}"
            sum_width = self.get_text_width(draw, sum_str, 'small')
            draw.text((width - padding - sum_width, y), sum_str, font=self.fonts['small'], fill=0)
            y += self.fonts['small'].size + 4

        self.draw_text_centered(draw, "Оплата товара", y, 'small', width)
        y += self.fonts['small'].size + 8

        img_array = np.array(img.convert('L'))
        non_empty_rows = np.where(img_array < 250)[0]
        if len(non_empty_rows) > 0:
            actual_bottom = max(non_empty_rows) + 20
        else:
            actual_bottom = y
        img = img.crop((0, 0, width, min(actual_bottom, 2000)))

        return img, data['extraction_data']

if __name__ == "__main__":
    if Path("generated_receipts_dataset").exists():
        shutil.rmtree("generated_receipts_dataset")
    gen = ReceiptGenerator()

    with open("backgrounds_sizes_with_shops.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✅ Загружено фонов: {len(data['backgrounds'])}")
    print(f"✅ Доступно магазинов: {len(set(shop['name'] for shop in gen.shops))}")

    for bg in data["backgrounds"]:
        bg_id = bg["id"]
        filename = bg["filename"]
        target_width = bg["width"]
        target_height = bg["height"]
        suitable_shops = bg["suitable_shops"]

        if not suitable_shops:
            print(f"\n⚠️ ФОН {filename} не подходит - пропускаем")
            continue
        selected_shop_name = random.choice(suitable_shops)
        
        selected_shop = next((s for s in gen.shops if s["name"] == selected_shop_name), None)

        print(f"\n📋 ФОН: {filename} | Размер: {target_width}x{target_height} | Магазин: {selected_shop_name}")

        gen.width = target_width

        original_shops = gen.shops
        gen.shops = [selected_shop]

        data_content = gen.create_receipt_content()
        
        best_num_items, _ = gen.get_optimal_item_count(selected_shop_name, target_height)
        if best_num_items > 0 and best_num_items != len(data_content['items']):
            if best_num_items < len(data_content['items']):
                data_content['items'] = data_content['items'][:best_num_items]
                data_content['subtotal'] = sum(item['total'] for item in data_content['items'])
                data_content['total'] = data_content['subtotal'] - data_content.get('discount', 0)
                data_content['extraction_data']['items'] = data_content['items']
                data_content['extraction_data']['subtotal'] = data_content['subtotal']
                data_content['extraction_data']['total'] = data_content['total']

        gen.shops = original_shops

        img, meta = gen.draw_receipt(data_content)

        fname = f"receipt_{bg_id}_{target_width}x{target_height}_{selected_shop_name}.png"
        img.save(gen.images_dir / fname, 'PNG', quality=95)
        meta['filename'] = fname
        meta['background'] = filename
        meta['selected_shop'] = selected_shop_name

        with open(gen.metadata_dir / f"{fname.replace('.png', '_meta.json')}", 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"   ✅ {fname} ({img.width}x{img.height})")

    print("\n📦 Собираем метаданные...")
    all_metadata = []
    for meta_file in gen.metadata_dir.glob("*.json"):
        if meta_file.name != "all_receipts_info.json":
            with open(meta_file, 'r', encoding='utf-8') as f:
                all_metadata.append(json.load(f))

    with open(gen.metadata_dir / "all_receipts_info.json", 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(all_metadata)} чеков")
    print("\n✅ Готово!")