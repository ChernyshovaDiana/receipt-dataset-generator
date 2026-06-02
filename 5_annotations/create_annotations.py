import json
import os
from pathlib import Path
from datetime import datetime

print("📝 Создаем аннотации для датасета...")

metadata_path = Path("generated_receipts_dataset/metadata/all_receipts_info.json")

if metadata_path.exists():
    with open(metadata_path, 'r', encoding='utf-8') as f:
        receipts_metadata = json.load(f)

    print(f"✅ Загружено {len(receipts_metadata)} записей из метаданных")

    annotations = {}

    for receipt in receipts_metadata:
        img_name = receipt.get("filename", f"receipt_{receipt['id']:04d}.png")

        items_list = []
        for item in receipt.get("items", []):
            items_list.append({
                "name": item.get("name", ""),
                "quantity": item.get("quantity", 1),
                "price": item.get("price", 0.0),
                "total": item.get("total", 0.0),
                "vat": item.get("vat", "")
            })

        img_width, img_height = 0, 0
        image_size = receipt.get("image_size", "")
        if "x" in image_size:
            parts = image_size.split("x")
            if len(parts) == 2:
                try:
                    img_width = int(parts[0])
                    img_height = int(parts[1])
                except ValueError:
                    pass

        annotation = {
            "filename": img_name,
            "store": receipt.get("shop_name", ""),
            "address": receipt.get("shop_address", ""),
            "tax_id": receipt.get("tax_id", ""),
            "datetime": f"{receipt.get('date', '')} {receipt.get('time', '')}",
            "receipt_num": receipt.get("receipt_num", ""),
            "cashier": receipt.get("cashier", ""),
            "items": items_list,
            "items_count": receipt.get("items_count", 0),
            "subtotal": receipt.get("subtotal", 0.0),
            "discount": receipt.get("discount", 0.0),
            "total": receipt.get("total", 0.0),
            "nds_20": receipt.get("nds_20", 0.0),
            "nds_10": receipt.get("nds_10", 0.0),
            "payment": {
                "method": receipt.get("payment_type", ""),
                "cash_received": receipt.get("cash_received", 0.0),
                "cash_change": receipt.get("cash_change", 0.0)
            },
            "fiscal_data": {
                "fn": receipt.get("fn", ""),
                "fd": receipt.get("fd", ""),
                "fp": receipt.get("fp", ""),
                "kkt_reg_num": receipt.get("kkt_reg_num", ""),
                "fn_zav_num": receipt.get("fn_zav_num", "")
            },
            "tax_system": receipt.get("tax_system", ""),
            "bonus_text": receipt.get("bonus_text", ""),
            "qr_data": receipt.get("qr_data", ""),
            "image_size": receipt.get("image_size", ""),
            "width": img_width,
            "height": img_height
        }

        annotations[img_name] = annotation

    output_path = "generated_receipts_dataset/annotations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"✅ Создано аннотаций: {len(annotations)}")

    if annotations:
        first_key = list(annotations.keys())[0]
        print(f"\n📊 Пример аннотации для {first_key}:")
        print(json.dumps(annotations[first_key], ensure_ascii=False, indent=2))

    coco_format = {
        "info": {
            "description": "Dataset of generated receipts",
            "version": "1.0",
            "year": 2025,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "receipt", "supercategory": "document"}]
    }

    annotation_id = 1

    for i, (img_name, ann) in enumerate(annotations.items()):
        coco_format["images"].append({
            "id": i,
            "file_name": img_name,
            "width": ann.get("width", 0),
            "height": ann.get("height", 0),
            "date_captured": ann.get("datetime", ""),
            "license": None,
            "flickr_url": None,
            "coco_url": None
        })

        coco_format["annotations"].append({
            "id": annotation_id,
            "image_id": i,
            "category_id": 1,
            "bbox": [0, 0, ann.get("width", 0), ann.get("height", 0)],
            "area": ann.get("width", 0) * ann.get("height", 0),
            "segmentation": [],
            "iscrowd": 0,
            "attributes": {
                "store": ann.get("store", ""),
                "total": ann.get("total", 0.0),
                "items_count": ann.get("items_count", 0),
                "payment_method": ann.get("payment", {}).get("method", ""),
                "fiscal_data": ann.get("fiscal_data", {})
            }
        })
        annotation_id += 1

    coco_path = "generated_receipts_dataset/annotations_coco.json"
    with open(coco_path, "w", encoding="utf-8") as f:
        json.dump(coco_format, f, ensure_ascii=False, indent=2)

    print(f"✅ COCO аннотации сохранены в: {coco_path}")
    print(f"   - Изображений в COCO: {len(coco_format['images'])}")
    print(f"   - Аннотаций в COCO: {len(coco_format['annotations'])}")

else:
    print(f"❌ Файл метаданных не найден: {metadata_path}")