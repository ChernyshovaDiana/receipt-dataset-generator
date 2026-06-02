import cv2
import numpy as np
import json
import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt

print("🎯 ПАКЕТНАЯ ОБРАБОТКА ФОНОВ")
print("=" * 60)

print("\n1️⃣ Загружаем фоны из папки realistic_backgrounds_300/")

backgrounds_folder = "realistic_backgrounds_300"
uploaded = {}

if Path(backgrounds_folder).exists():
    for img_path in glob.glob(f"{backgrounds_folder}/*.png"):
        with open(img_path, "rb") as f:
            uploaded[Path(img_path).name] = f.read()
    print(f"✅ Загружено {len(uploaded)} фонов из папки")
else:
    print(f"❌ Папка {backgrounds_folder} не найдена!")
    print("   Сначала запустите шаг 1 (генерация фонов)")
    exit(1)

MIN_HEIGHTS = {
    "ШЕСТЕРОЧКА": 564,
    "МАГНАТ": 437,
    "АШАНЧИК": 341,
    "АПТЕКА 37.7": 630,
    "РИГЛАЙФ": 630,
    "АЛЛЕНТА": 526,
    "ПЕРЕКРЕСТКИ": 450,
    "ВИЛЛАЗБУКА": 613,
    "ВКУСОЛЕНД": 283,
    "ЗДОРОВУМ": 630,
    "ФАРМТЭК": 630,
    "МОНЕТИКА": 377,
    "СТАРТ": 395,
    "ДВОЙКА": 341,
    "СЕМЬ ДОРОГ": 512,
}

def find_best_quadrilateral(contour):
    for epsilon in np.arange(0.005, 0.02, 0.002):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > 1000:
                return approx
    return None

def order_corners_correct(pts):
    pts = pts.reshape(4, 2)
    center = np.mean(pts, axis=0)
    angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    sorted_indices = np.argsort(angles)
    sorted_pts = pts[sorted_indices]

    if sorted_pts[0][0] + sorted_pts[0][1] < sorted_pts[1][0] + sorted_pts[1][1]:
        top_left = sorted_pts[0]
        top_right = sorted_pts[1]
    else:
        top_left = sorted_pts[1]
        top_right = sorted_pts[0]

    if sorted_pts[2][0] + sorted_pts[2][1] < sorted_pts[3][0] + sorted_pts[3][1]:
        bottom_left = sorted_pts[2]
        bottom_right = sorted_pts[3]
    else:
        bottom_left = sorted_pts[3]
        bottom_right = sorted_pts[2]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

def detect_corners_and_size(image):
    """Находит углы и размеры белого прямоугольника на изображении"""
    bg_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bg_blur = cv2.GaussianBlur(bg_gray, (7, 7), 0)
    _, light_mask = cv2.threshold(bg_blur, 200, 255, cv2.THRESH_BINARY)
    kernel = np.ones((15, 15), np.uint8)
    light_mask = cv2.morphologyEx(light_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(light_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None, None, None

    largest = max(contours, key=cv2.contourArea)
    quad = find_best_quadrilateral(largest)

    if quad is None:
        x, y, w, h = cv2.boundingRect(largest)
        quad = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])

    corners = order_corners_correct(quad)
    width = int(np.linalg.norm(corners[1] - corners[0]))
    height = int(np.linalg.norm(corners[3] - corners[0]))

    return corners, width, height, quad

print("\n🔍 Обработка фонов...")

backgrounds_info = []

for idx, (filename, content) in enumerate(uploaded.items()):
    print(f"   Обработка {idx+1}/{len(uploaded)}: {filename}")

    file_bytes = np.asarray(bytearray(content), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        print(f"      ⚠️ Не удалось прочитать {filename}")
        continue

    corners, width, height, quad = detect_corners_and_size(image)

    if corners is None:
        print(f"      ⚠️ Не удалось найти прямоугольник в {filename}")
        continue

    suitable_shops = []
    for shop_name, min_height in MIN_HEIGHTS.items():
        if height >= min_height:
            suitable_shops.append(shop_name)

    backgrounds_info.append({
        "id": idx + 1,
        "filename": filename,
        "width": width,
        "height": height,
        "corners": corners.tolist(),
        "image_size": f"{image.shape[1]}x{image.shape[0]}",
        "suitable_shops": suitable_shops,
        "suitable_count": len(suitable_shops)
    })

    print(f"      📏 Размер: {width} x {height} px")
    print(f"      ✅ Подходит для {len(suitable_shops)} магазинов")

print(f"\n✅ Успешно обработано: {len(backgrounds_info)} из {len(uploaded)}")

backgrounds_info.sort(key=lambda x: x["suitable_count"], reverse=True)

print("\n💾 Сохраняем результаты...")

result_json = {
    "total": len(backgrounds_info),
    "min_heights": MIN_HEIGHTS, 
    "backgrounds": backgrounds_info
}

json_str = json.dumps(result_json, ensure_ascii=False, indent=2)

with open("backgrounds_sizes_with_shops.json", "w", encoding="utf-8") as f:
    f.write(json_str)

print(f"✅ Файл backgrounds_sizes_with_shops.json создан")

print("\n" + "=" * 80)
print("📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ (отсортировано по подходящим магазинам):")
print("=" * 80)
print(f"{'№':<4} {'Название файла':<30} {'Размер':<12} {'Подходит для':<20}")
print("-" * 80)

for info in backgrounds_info:
    shops_preview = ', '.join(info['suitable_shops'][:3])
    if info['suitable_count'] > 3:
        shops_preview += f" +{info['suitable_count'] - 3}"
    print(f"{info['id']:<4} {info['filename']:<30} {info['width']}x{info['height']:<5} {shops_preview}")

print("\n" + "=" * 80)
print("📊 СТАТИСТИКА:")
print("=" * 80)

total_bgs = len(backgrounds_info)
if total_bgs > 0:
    avg_suitable = sum(bg["suitable_count"] for bg in backgrounds_info) / total_bgs
    print(f"Всего фонов: {total_bgs}")
    print(f"Среднее количество подходящих магазинов: {avg_suitable:.1f}")
    print(f"\n🏆 Лучшие фоны (больше всего подходит магазинов):")
    for bg in backgrounds_info[:3]:
        print(f"   - {bg['filename']}: {bg['suitable_count']} магазинов")
    print(f"\n📉 Худшие фоны (меньше всего подходит):")
    for bg in backgrounds_info[-3:]:
        print(f"   - {bg['filename']}: {bg['suitable_count']} магазинов")

print("\n📸 Показываю фоны с найденными углами...")

for i, info in enumerate(backgrounds_info):
    file_bytes = np.asarray(bytearray(uploaded[info['filename']]), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    corners = np.array(info['corners'])
    width = info['width']
    height = info['height']

    vis = image.copy()

    quad = np.array(corners, dtype=np.int32)
    cv2.drawContours(vis, [quad], -1, (0, 255, 0), 3)

    colors = [(0, 0, 255), (255, 0, 0), (0, 255, 255), (255, 255, 0)]

    for j, corner in enumerate(corners):
        cv2.circle(vis, tuple(corner.astype(int)), 10, colors[j], -1)
        cv2.circle(vis, tuple(corner.astype(int)), 12, (255, 255, 255), 2)

    cv2.putText(vis, f"{width}x{height} | Подходит для {info['suitable_count']} магазинов", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(vis, info['filename'][:25], (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    plt.figure(figsize=(8, 8))
    plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    plt.title(f"Фон {i+1}: {info['filename']} | Размер: {width}x{height} | Магазинов: {info['suitable_count']}")
    plt.axis('off')
    plt.show()

print("\n" + "=" * 60)
print("🎉 ГОТОВО!")
print("=" * 60)
print(f"✅ Обработано фонов: {len(backgrounds_info)}")
print(f"✅ Результаты сохранены в backgrounds_sizes_with_shops.json")
print("\n📋 Структура JSON файла:")
print("   - total: количество фонов")
print("   - min_heights: справочник минимальных высот для каждого магазина")
print("   - backgrounds: список фонов")
print("     - id: номер фона")
print("     - filename: имя файла")
print("     - width: ширина прямоугольника")
print("     - height: высота прямоугольника")
print("     - corners: координаты 4 углов")
print("     - suitable_shops: список подходящих магазинов")
print("     - suitable_count: количество подходящих магазинов")