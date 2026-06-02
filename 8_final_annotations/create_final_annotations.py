import json
import os
import cv2
from pathlib import Path

print("📝 Создаем аннотации для финальных результатов (чеки на фоне)...")

final_results_path = Path("final_results")
annotations_final = {}

metadata_path = Path("generated_receipts_dataset/metadata/all_receipts_info.json")

if metadata_path.exists():
    with open(metadata_path, 'r', encoding='utf-8') as f:
        receipts_metadata = json.load(f)

    receipt_metadata_map = {}
    for meta in receipts_metadata:
        filename = meta.get("filename", "")
        receipt_metadata_map[filename] = meta

    print(f"✅ Загружено {len(receipts_metadata)} записей метаданных чеков")

    for result_file in list(final_results_path.glob("*.jpg")) + list(final_results_path.glob("*.png")):
        parts = result_file.stem.split('_')
        if len(parts) >= 2:
            bg_id = parts[1]
            matching_meta = None
            for filename, meta in receipt_metadata_map.items():
                if filename.startswith(f"receipt_{bg_id}_"):
                    matching_meta = meta
                    break

            if matching_meta:
                img = cv2.imread(str(result_file))
                img_height, img_width = img.shape[:2] if img is not None else (0, 0)

                annotation = {
                    "filename": result_file.name,
                    "image_size": f"{img_width}x{img_height}",
                    "source_receipt": matching_meta.get("filename", ""),
                    "bg_id": bg_id,
                    "store": matching_meta.get("shop_name", ""),
                    "address": matching_meta.get("shop_address", ""),
                    "tax_id": matching_meta.get("tax_id", ""),
                    "datetime": f"{matching_meta.get('date', '')} {matching_meta.get('time', '')}",
                    "receipt_num": matching_meta.get("receipt_num", ""),
                    "cashier": matching_meta.get("cashier", ""),
                    "items": matching_meta.get("items", []),
                    "items_count": matching_meta.get("items_count", 0),
                    "subtotal": matching_meta.get("subtotal", 0.0),
                    "discount": matching_meta.get("discount", 0.0),
                    "total": matching_meta.get("total", 0.0),
                    "nds_20": matching_meta.get("nds_20", 0.0),
                    "nds_10": matching_meta.get("nds_10", 0.0),
                    "payment": matching_meta.get("payment", {}),
                    "fiscal_data": matching_meta.get("fiscal_data", {}),
                    "tax_system": matching_meta.get("tax_system", ""),
                    "bonus_text": matching_meta.get("bonus_text", ""),
                    "qr_data": matching_meta.get("qr_data", "")
                }

                annotations_final[result_file.name] = annotation
                print(f"   ✅ Обработан: {result_file.name}")
            else:
                print(f"   ⚠️ Не найдены метаданные для: {result_file.name}")
        else:
            print(f"   ⚠️ Неверный формат имени: {result_file.name}")

    output_path = "final_results/annotations_final.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(annotations_final, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Создано аннотаций для финальных результатов: {len(annotations_final)}")

    if annotations_final:
        first_key = list(annotations_final.keys())[0]
        print(f"\n📊 Пример аннотации для {first_key}:")
        print(json.dumps(annotations_final[first_key], ensure_ascii=False, indent=2))

    coco_format_final = {
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "receipt"}]
    }

    for i, (img_name, ann) in enumerate(annotations_final.items()):
        size_parts = ann.get("image_size", "0x0").split('x')
        width = int(size_parts[0]) if len(size_parts) > 0 else 0
        height = int(size_parts[1]) if len(size_parts) > 1 else 0

        coco_format_final["images"].append({
            "id": i,
            "file_name": img_name,
            "width": width,
            "height": height
        })

    coco_path = "final_results/annotations_final_coco.json"
    with open(coco_path, "w", encoding="utf-8") as f:
        json.dump(coco_format_final, f, ensure_ascii=False, indent=2)

    print(f"✅ COCO аннотации сохранены в: {coco_path}")

else:
    print(f"❌ Файл метаданных не найден: {metadata_path}")
    print("   Сначала запусти генерацию чеков и создание метаданных")