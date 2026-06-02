import cv2
import numpy as np
import os
import random
import glob

print("🎭 НАЛОЖЕНИЕ РЕАЛИСТИЧНЫХ ЭФФЕКТОВ НА ВСЮ КАРТИНКУ")
print("=" * 60)

os.makedirs("final_results_augmented", exist_ok=True)

image_files = glob.glob("final_results/*.png")
print(f"📸 Найдено изображений: {len(image_files)}")

def add_lighting_gradient(image):
    h, w = image.shape[:2]
    result = image.copy().astype(np.float32)

    if random.random() < 0.7:
        light_type = random.choice(['left', 'right', 'top', 'corner'])

        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        xx, yy = np.meshgrid(x, y)

        if light_type == 'left':
            light_map = 0.7 + 0.4 * (1 - xx)
        elif light_type == 'right':
            light_map = 0.7 + 0.4 * xx
        elif light_type == 'top':
            light_map = 0.7 + 0.4 * (1 - yy)
        else: 
            light_map = 0.7 + 0.4 * (1 - xx * yy)

        intensity = random.uniform(0.85, 0.98)
        light_map = 1 - (1 - light_map) * (1 - intensity)

        for c in range(3):
            result[:, :, c] = result[:, :, c] * light_map

    return np.clip(result, 0, 255).astype(np.uint8)

def add_glare(image):
    h, w = image.shape[:2]
    result = image.copy().astype(np.float32)

    if random.random() < 0.4:
        glare_x = random.randint(w//4, 3*w//4)
        glare_y = random.randint(h//4, 3*h//4)
        glare_radius = random.randint(min(w, h)//6, min(w, h)//3)

        mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(mask, (glare_x, glare_y), glare_radius, 1, -1)
        mask = cv2.GaussianBlur(mask, (glare_radius//3*2+1, glare_radius//3*2+1), 0)

        glare_intensity = random.uniform(1.05, 1.15)

        for c in range(3):
            result[:, :, c] = result[:, :, c] * (1 + mask * (glare_intensity - 1))

    return np.clip(result, 0, 255).astype(np.uint8)

def add_shadow_from_object(image):
    h, w = image.shape[:2]
    result = image.copy().astype(np.float32)

    if random.random() < 0.5:
        shadow_corners = random.sample(['top-left', 'top-right', 'bottom-left', 'bottom-right'],
                                        random.randint(1, 2))

        shadow_map = np.ones((h, w), dtype=np.float32)
        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        xx, yy = np.meshgrid(x, y)

        for corner in shadow_corners:
            if corner == 'top-left':
                shadow = 1 - 0.15 * (1 - xx) * (1 - yy)
            elif corner == 'top-right':
                shadow = 1 - 0.15 * xx * (1 - yy)
            elif corner == 'bottom-left':
                shadow = 1 - 0.15 * (1 - xx) * yy
            else: 
                shadow = 1 - 0.15 * xx * yy

            shadow_map = shadow_map * shadow

        for c in range(3):
            result[:, :, c] = result[:, :, c] * shadow_map

    return np.clip(result, 0, 255).astype(np.uint8)

def add_noise(image):
    if random.random() < 0.6:
        noise = np.random.normal(0, random.uniform(1, 3), image.shape).astype(np.float32)
        result = image.astype(np.float32) + noise
        return np.clip(result, 0, 255).astype(np.uint8)
    return image

def add_color_temperature(image):
    result = image.copy().astype(np.float32)

    if random.random() < 0.5:
        if random.random() > 0.5:
            result[:, :, 0] = result[:, :, 0] * 0.95   
            result[:, :, 1] = result[:, :, 1] * 0.98   
            result[:, :, 2] = result[:, :, 2] * 1.02   
        else:
            result[:, :, 0] = result[:, :, 0] * 1.02   
            result[:, :, 1] = result[:, :, 1] * 0.99   
            result[:, :, 2] = result[:, :, 2] * 0.96   

    return np.clip(result, 0, 255).astype(np.uint8)

def add_subtle_blur(image):
    if random.random() < 0.25:
        kernel_size = random.choice([3, 5])
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0.5)
    return image

def add_dust_and_scratches(image):
    h, w = image.shape[:2]
    result = image.copy()

    if random.random() < 0.35:
        num_dust = random.randint(5, 20)
        for _ in range(num_dust):
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            radius = random.randint(1, 2)
            cv2.circle(result, (x, y), radius, (random.randint(80, 120),) * 3, -1)

    return result

def add_vignette(image):
    h, w = image.shape[:2]
    result = image.copy().astype(np.float32)

    if random.random() < 0.4:
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        xx, yy = np.meshgrid(x, y)
        radius = np.sqrt(xx**2 + yy**2)
        vignette = 1 - np.clip(radius * random.uniform(0.1, 0.2), 0, 0.15)

        for c in range(3):
            result[:, :, c] = result[:, :, c] * vignette

    return np.clip(result, 0, 255).astype(np.uint8)

def adjust_saturation(image):
    if random.random() < 0.4:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        sat_factor = random.uniform(0.85, 1.1)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return image

print("\n🔧 Применяем эффекты...")

for i, img_path in enumerate(image_files):
    image = cv2.imread(img_path)
    if image is None:
        continue

    result = image.copy()

    result = add_lighting_gradient(result)
    result = add_glare(result)
    result = add_color_temperature(result)
    result = adjust_saturation(result)
    result = add_shadow_from_object(result)
    result = add_vignette(result)
    result = add_dust_and_scratches(result)
    result = add_subtle_blur(result)
    result = add_noise(result)

    filename = os.path.basename(img_path)
    save_path = os.path.join("final_results_augmented", filename)
    cv2.imwrite(save_path, result)

    if (i + 1) % 10 == 0:
        print(f"   Обработано: {i+1}/{len(image_files)}")

print(f"\n✅ Готово! Обработано {len(image_files)} изображений")
print(f"📁 Результаты сохранены в папке: final_results_augmented/")