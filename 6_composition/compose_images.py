import cv2
import numpy as np
import json
import os
import glob
import matplotlib.pyplot as plt

print("🎯 ПРАВИЛЬНОЕ НАЛОЖЕНИЕ ЧЕКОВ (ПОИСК ПО ID)")
print("=" * 60)

with open("backgrounds_sizes_with_shops.json", "r", encoding="utf-8") as f:
    data = json.load(f)

backgrounds = data["backgrounds"]
print(f"✅ Загружено {len(backgrounds)} фонов")

os.makedirs("final_results", exist_ok=True)
os.makedirs("debug_corners", exist_ok=True)

def visualize_corners(image, corners, title, save_path):
    vis = image.copy()
    pts = corners.astype(np.int32)
    cv2.polylines(vis, [pts], True, (0, 255, 0), 3)

    colors = [(0, 0, 255), (255, 0, 0), (0, 255, 255), (255, 255, 0)]
    corner_names = ["ТЛ", "ТП", "ПН", "ЛН"]

    for i, (corner, color, name) in enumerate(zip(corners, colors, corner_names)):
        corner_pt = tuple(corner.astype(int))
        cv2.circle(vis, corner_pt, 8, color, -1)
        cv2.circle(vis, corner_pt, 10, (255, 255, 255), 2)
        cv2.putText(vis, f"{i+1}:{name}", (corner_pt[0] + 10, corner_pt[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    width = int(np.linalg.norm(corners[1] - corners[0]))
    height = int(np.linalg.norm(corners[3] - corners[0]))
    cv2.putText(vis, f"Size: {width}x{height}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(vis, title, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imwrite(save_path, vis)

    plt.figure(figsize=(10, 8))
    plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    plt.title(f"Углы: {title}")
    plt.axis('off')
    plt.show()

    return vis

print("\n🔍 Накладываем чеки на фоны...")

for idx, bg in enumerate(backgrounds):
    bg_id = bg["id"]
    filename = bg["filename"]

    corners = np.array(bg["corners"], dtype=np.float32)

    pattern = f"generated_receipts_dataset/images/receipt_{bg_id}_*.png"
    matching_files = glob.glob(pattern)

    if not matching_files:
        print(f"\n📌 {idx+1}/{len(backgrounds)}: {filename}")
        print(f"   ⚠️ Чек для ID={bg_id} не найден по паттерну: {pattern}")
        continue

    receipt_path = matching_files[0]

    print(f"\n📌 {idx+1}/{len(backgrounds)}: {filename}")
    print(f"   ✅ Найден чек: {os.path.basename(receipt_path)}")

    background = cv2.imread(filename)
    receipt = cv2.imread(receipt_path)

    if background is None or receipt is None:
        print(f"   ⚠️ Ошибка загрузки")
        continue

    print(f"   ✅ Фон: {background.shape[1]}x{background.shape[0]}")
    print(f"   ✅ Чек: {receipt.shape[1]}x{receipt.shape[0]}")
    print(f"   ✅ Углы из JSON: ТЛ={corners[0]}, ТП={corners[1]}, ПН={corners[2]}, ЛН={corners[3]}")

    rect_width = int(np.linalg.norm(corners[1] - corners[0]))
    rect_height = int(np.linalg.norm(corners[3] - corners[0]))
    print(f"   ✅ Размер прямоугольника: {rect_width}x{rect_height}")

    debug_path = f"debug_corners/corners_{bg_id}_{filename}"
    visualize_corners(background, corners, f"Фон {bg_id}: {filename} (из JSON)", debug_path)

    h, w = receipt.shape[:2]

    src_pts = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
    dst_pts = corners

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

    transformed_receipt = cv2.warpPerspective(
        receipt,
        matrix,
        (background.shape[1], background.shape[0]),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255)
    )

    mask = np.zeros((background.shape[0], background.shape[1]), dtype=np.uint8)
    cv2.fillPoly(mask, [corners.astype(np.int32)], 255)
    mask = mask / 255.0
    mask_3d = np.stack([mask] * 3, axis=2)

    result = background.copy()
    result = (result * (1 - mask_3d) + transformed_receipt * mask_3d).astype(np.uint8)

    result_path = f"final_results/result_{bg_id}_{filename}"
    cv2.imwrite(result_path, result)
    print(f"   ✅ Сохранено: {result_path}")

    plt.figure(figsize=(12, 8))

    plt.subplot(1, 2, 1)
    corners_vis = background.copy()
    cv2.polylines(corners_vis, [corners.astype(np.int32)], True, (0, 255, 0), 3)
    for corner in corners:
        cv2.circle(corners_vis, tuple(corner.astype(int)), 8, (0, 0, 255), -1)
    plt.imshow(cv2.cvtColor(corners_vis, cv2.COLOR_BGR2RGB))
    plt.title(f"Углы из JSON - {filename}")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    plt.title(f"Результат наложения")
    plt.axis('off')

    plt.tight_layout()
    plt.savefig(f"debug_corners/comparison_{bg_id}_{filename}.png", dpi=150)
    plt.show()

print("\n" + "=" * 60)
print("🎉 ГОТОВО!")