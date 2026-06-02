import cv2
import numpy as np
import random
import os

print("🎭 Применяем дефекты...")

def add_printer_uneven_lines(image):
    try:
        h, w = image.shape[:2]
        result = image.copy().astype(np.float32)

        if random.random() < 0.40:
            num_bands = random.choice([1, 2])
            margin = random.randint(15, 40)
            band_width = random.randint(int(w * 0.06), int(w * 0.12))
            positions = []

            if num_bands == 1:
                max_start = w - band_width - margin
                if max_start > margin:
                    x_start = random.randint(margin, max_start)
                    positions.append(x_start)
            else:
                third = w // 3
                x_start1 = random.randint(margin, third - band_width)
                x_start2 = random.randint(third * 2, w - band_width - margin)
                positions.append(x_start1)
                positions.append(x_start2)

            for x_start in positions:
                x_end = min(w, x_start + band_width)

                if num_bands == 2:
                    for x in range(x_start, x_end):
                        dist_from_edge = min(x - x_start, x_end - x - 1)
                        distance_to_edge = min(dist_from_edge, band_width - dist_from_edge)

                        if distance_to_edge < 4:
                            dark_factor = random.uniform(0.68, 0.78)
                        elif distance_to_edge < 10:
                            dark_factor = random.uniform(0.78, 0.85)
                        else:
                            dark_factor = random.uniform(0.85, 0.92)

                        wave = np.sin(x * 0.15) * 0.02
                        dark_factor = min(0.92, max(0.68, dark_factor + wave))

                        result[:, x:x+1, :] = result[:, x:x+1, :] * dark_factor

                    num_blobs = random.randint(1, 2)
                    for _ in range(num_blobs):
                        blob_x = random.randint(x_start + 5, x_end - 5)
                        blob_width = random.randint(3, 6)
                        blob_factor = random.uniform(0.70, 0.82)

                        for bx in range(blob_x, min(blob_x + blob_width, x_end)):
                            result[:, bx:bx+1, :] = result[:, bx:bx+1, :] * blob_factor

                else:
                    for x in range(x_start, x_end):
                        dark_factor = random.uniform(0.75, 0.95)
                        wave = np.sin(x * 0.1) * 0.03
                        dark_factor = min(0.95, max(0.75, dark_factor + wave))
                        result[:, x:x+1, :] = result[:, x:x+1, :] * dark_factor

                    num_blobs = random.randint(1, 3)
                    for _ in range(num_blobs):
                        blob_x = random.randint(x_start, x_end - 5)
                        blob_width = random.randint(3, 8)
                        blob_factor = random.uniform(0.65, 0.80)

                        for bx in range(blob_x, min(blob_x + blob_width, x_end)):
                            result[:, bx:bx+1, :] = result[:, bx:bx+1, :] * blob_factor

        return np.clip(result, 0, 255).astype(np.uint8)
    except:
        return image

def add_subtle_stains(image):
    try:
        h, w = image.shape[:2]
        result = image.copy().astype(np.float32)

        if random.random() < 0.3:
            num_stains = random.randint(1, 2)

            for _ in range(num_stains):
                center_x = random.randint(30, w-30)
                center_y = random.randint(30, h-30)
                radius = random.randint(5, 15)

                mask = np.zeros((h, w), dtype=np.float32)
                cv2.circle(mask, (center_x, center_y), radius, 1.0, -1)
                mask = cv2.GaussianBlur(mask, (7, 7), 0)

                intensity = random.uniform(0.06, 0.10)
                stain_color = np.array([90, 85, 80])

                for c in range(3):
                    result[:, :, c] = result[:, :, c] * (1 - mask * intensity) + stain_color[c] * mask * intensity

        return np.clip(result, 0, 255).astype(np.uint8)
    except:
        return image

def add_subtle_folds(image):
    try:
        h, w = image.shape[:2]
        result = image.copy().astype(np.float32)

        if random.random() < 0.2:
            if random.random() > 0.5:
                fold_x = random.randint(w//3, 2*w//3)
                fold_width = random.randint(2, 4)

                for x in range(max(0, fold_x - fold_width), min(w, fold_x + fold_width)):
                    distance = abs(x - fold_x)
                    intensity = 1 - (distance / fold_width) * 0.06
                    result[:, x] = result[:, x] * intensity
            else:
                fold_y = random.randint(h//3, 2*h//3)
                fold_height = random.randint(2, 4)

                for y in range(max(0, fold_y - fold_height), min(h, fold_y + fold_height)):
                    distance = abs(y - fold_y)
                    intensity = 1 - (distance / fold_height) * 0.06
                    result[y, :] = result[y, :] * intensity

        return np.clip(result, 0, 255).astype(np.uint8)
    except:
        return image

def add_subtle_scuffs(image):
    try:
        h, w = image.shape[:2]
        result = image.copy().astype(np.float32)

        if random.random() < 0.25:
            num_scuffs = random.randint(1, 2)

            for _ in range(num_scuffs):
                length = random.randint(20, 60)
                angle = random.uniform(0, 360)
                start_x = random.randint(40, w-40)
                start_y = random.randint(40, h-40)

                end_x = int(start_x + length * np.cos(np.radians(angle)))
                end_y = int(start_y + length * np.sin(np.radians(angle)))

                mask = np.zeros((h, w), dtype=np.float32)
                cv2.line(mask, (start_x, start_y), (end_x, end_y), 1.0, thickness=1)
                mask = cv2.GaussianBlur(mask, (5, 5), 0)

                intensity = random.uniform(0.04, 0.07)
                for c in range(3):
                    result[:, :, c] = result[:, :, c] * (1 + mask * intensity)

        return np.clip(result, 0, 255).astype(np.uint8)
    except:
        return image

print("🔧 Применяем дефекты...")
augmented_count = 0

images_path = "generated_receipts_dataset/images"

if os.path.exists(images_path):
    image_files = [f for f in os.listdir(images_path) if f.endswith('.png')]
    print(f"📊 Найдено изображений: {len(image_files)}")

    for img_name in image_files:
        img_path = os.path.join(images_path, img_name)

        image = cv2.imread(img_path)
        if image is None:
            continue

        try:
            result = image.copy()
            result = add_printer_uneven_lines(result)
            result = add_subtle_stains(result)
            result = add_subtle_scuffs(result)
            result = add_subtle_folds(result)

            cv2.imwrite(img_path, result)

            augmented_count += 1
            if augmented_count % 20 == 0:
                print(f"✅ Обработано: {augmented_count}/{len(image_files)}")

        except Exception as e:
            print(f"⚠️ Ошибка в {img_name}: {e}")
            cv2.imwrite(img_path, image)
            augmented_count += 1

    print(f"\n🎉 Обработано {augmented_count} изображений")
    print("✅ Дефекты применены")

else:
    print(f"❌ Папка не найдена: {images_path}")