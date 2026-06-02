import time
import requests
import json
import os
from datetime import datetime

output_dir = "realistic_backgrounds_300"
os.makedirs(output_dir, exist_ok=True)
print(f"📁 Создана папка: {output_dir}")
print("-" * 70)

print("🔌 ПРОВЕРКА ПОДКЛЮЧЕНИЯ...")
try:
    resp = requests.get("http://0.0.0.0/object_info", timeout=5)
    if resp.status_code != 200:
        raise ConnectionError("Сервер не отвечает")
    print("✅ Подключение к серверу успешно")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    raise

materials = {
    "wood": [
        "reclaimed oak wood", "dark walnut wood", "natural maple wood", "distressed pine wood",
        "vintage teak wood", "bleached ash wood", "cherry wood", "mahogany wood",
        "bamboo wood", "rosewood", "ebony wood", "zebrawood",
        "olive wood", "cork wood", "plywood with grain", "pallets wood",
        "driftwood", "barn wood", "shou sugi ban burned wood", "white oak wood",
        "red oak wood", "hickory wood", "birch wood", "beech wood",
        "cedar wood", "redwood", "ipe wood", "acacia wood",
        "knotty pine", "butcher block end grain", "parquet flooring", "wood veneer",
        "MDF board with wood grain", "laminate flooring", "engineered wood", "wooden crate",
        "wine barrel stave wood", "old boat wood", "railroad tie wood", "tree stump slice"
    ],

    "stone": [
        "black slate stone", "grey slate stone", "green slate stone", "purple slate stone",
        "marble white carrara", "marble black nero", "marble calacatta gold", "marble emperador",
        "granite black galaxy", "granite white ice", "granite blue pearl", "granite red",
        "limestone", "travertine", "sandstone", "quartzite",
        "soapstone", "basalt", "gneiss", "schist",
        "cobblestone", "paving stone", "flagstone", "river rock",
        "pebble surface", "crushed stone", "terrazzo", "concrete polished",
        "concrete brushed", "concrete stamped", "cement board", "cinder block",
        "brick old red", "brick white washed", "brick grey", "clay tile",
        "terracotta", "mosaic stone", "stacked stone", "fieldstone"
    ],

    "metal": [
        "brushed stainless steel", "galvanized steel", "oxidized copper", "brass plate",
        "aluminum sheet", "cast iron", "wrought iron", "corrugated metal",
        "diamond plate aluminum", "expanded metal", "perforated metal", "wire mesh",
        "tin ceiling tile", "copper patina", "bronze aged", "chrome plated",
        "nickel satin", "titanium raw", "zinc plated", "lead sheet",
        "steel plate rusted", "cold rolled steel", "hot rolled steel", "corten steel",
        "silver plated", "gold leaf", "pewter", "tin sheet",
        "metal grating", "rebar grid"
    ],

    "fabric": [
        "linen natural", "cotton canvas", "jute burlap", "hemp fabric",
        "wool felt", "polyester microfiber", "nylon ripstop", "satin silk",
        "velvet crushed", "denim blue", "corduroy", "tweed herringbone",
        "flannel plaid", "leather black", "leather brown", "suede grey",
        "faux fur white", "sheepskin", "carpet berber", "carpet shag",
        "rug persian", "rug jute", "mat coir", "toweling terry cloth",
        "muslin unbleached", "gabardine", "poplin", "oxford cloth",
        "chambray", "seersucker", "organza", "lace white",
        "mesh fabric", "neoprene", "vinyl upholstery", "pleather",
        "felt craft", "flannel shirt material", "blanket wool", "quilt cotton"
    ],

    "plastic": [
        "white matte PVC", "black gloss acrylic", "clear polycarbonate", "frosted plexiglass",
        "HDPE cutting board", "polypropylene white", "nylon black", "delrin acetal",
        "teflon sheet", "silicone mat", "rubber black", "latex sheet",
        "epoxy resin", "fiberglass panel", "carbon fiber", "kevlar weave",
        "melamine board", "formica laminate", "corian solid surface", "hi-macs",
        "styrofoam board", "foam core", "eva foam", "polyethylene foam",
        "acrylic mirror", "perspex", "lexan", "plexi glass colored",
        "bakelite vintage", "g10 garolite"
    ],

    "paper": [
        "kraft paper brown", "cardboard corrugated", "watercolor paper cold press", "sketch paper smooth",
        "newsprint", "magazine glossy", "book page aged", "vellum parchment",
        "rice paper", "washi paper", "tissue paper", "wax paper",
        "butcher paper", "freezer paper", "sandpaper fine grit", "construction paper",
        "poster board", "mat board", "chipboard", "particle board",
        "fiberboard", "cardstock", "index card", "manila folder",
        "envelope paper", "paper bag", "coffee filter", "paper towel",
        "napkin linen-like", "wallpaper vinyl"
    ],

    "glass_ceramic": [
        "frosted glass", "clear float glass", "textured glass rain", "obscure glass",
        "tinted glass grey", "mirrored glass", "ceramic tile white", "ceramic tile blue",
        "porcelain matte", "porcelain gloss", "stoneware brown", "earthenware terracotta",
        "raku pottery", "crackle glaze", "majolica", "delftware",
        "china white", "bone china", "vitrified tile", "quarry tile",
        "glass block", "bottle glass green", "stained glass", "fused glass", "slumped glass"
    ],

    "natural": [
        "soil dark rich", "clay red", "sand fine beige", "gravel small",
        "pebbles smooth", "moss green", "dried leaves", "pine needles",
        "bark oak tree", "bark birch", "coconut coir", "straw hay",
        "wood chips", "sawdust", "charcoal pieces", "ash grey",
        "pumice stone", "lava rock", "coral reef", "seashells crushed",
        "salt coarse", "sugar white", "flour dusted", "coffee grounds",
        "tea leaves dried", "spice turmeric", "cinnamon ground", "cocoa powder",
        "pollen yellow", "pressed flowers", "herbs dried", "grass clippings",
        "hay bale", "compost", "mulch bark"
    ],

    "studio": [
        "seamless paper white", "seamless paper grey", "seamless paper black", "gradient background",
        "cyclorama white", "photo studio floor", "light tent fabric", "soft box surface",
        "reflector silver", "reflector gold", "diffuser white", "gel color red",
        "chroma key green", "chroma key blue", "infinity curve", "product table matte",
        "jewelry display pad", "watchmaker mat", "electronics mat anti-static", "soldering mat",
        "cutting mat green", "drafting board", "light table", "light box",
        "portfolio case", "display board foam", "exhibition panel", "museum mount board",
        "archive box", "storage bin lid"
    ]
}

lighting_styles = [
    "natural daylight from window", "soft overcast sky lighting", "warm golden hour sun", "cool morning light",
    "studio softbox left", "studio softbox right", "ring light diffused", "LED panel 45 degrees",
    "window light cloudy day", "skylight overhead", "fluorescent office lighting", "warm tungsten lamp",
    "candle warm glow", "fireplace ambient", "flash bounced", "continuous LED",
    "harsh direct sun", "shaded area", "dappled light through leaves", "reflected bounce card",
    "backlit silhouette", "rim light edge", "clamshell lighting", "butterfly lighting",
    "Rembrandt lighting", "split lighting", "loop lighting", "broad lighting",
    "short lighting", "available light only", "mixed lighting warm/cool", "moody dark shadows"
]

angles_compositions = [
    "Top-down view", "Slight overhead view (10°)", "Direct overhead view", "Nearly top-down view",
    "High-angle view (15°)", "Moderate overhead (20°)", "Aerial perspective", "Flat lay composition",
    "Bird's eye view", "Overhead with slight tilt", "From slightly above", "Looking straight down",
    "Parallel to surface", "Eye level angle", "Slight perspective 5°", "Minimal angle 3°"
]

placement_phrases = [
    "a single blank white square receipt paper (400x400px, perfectly flat) lies in the corner of the frame",
    "a small blank white square paper placed casually on the edge",
    "a single blank white square receipt lies flat on the surface",
    "a blank white square paper rests on the {material}",
    "the white square receipt is positioned near the border",
    "a tiny white square paper sits in the lower right area",
    "the small receipt paper is placed offset from center",
    "a blank square paper lies in the upper left quadrant",
    "the white 400x400px square is located at the frame's edge",
    "a single receipt paper sits quietly in the background corner"
]

negative_prompt = """curled, bent, warped, rolled, folded, creased, lifted corners, curved edges, wavy, distorted,
3D shape, non-flat, text, numbers, writing, qr code, dirty, low quality, extra objects, hands, people,
shadows on paper, blurry, out of focus, extreme perspective, steep angle, 45 degrees, worm's eye view,
looking from below, dramatic foreshortening, rectangular, narrow, elongated, portrait orientation,
landscape orientation, full table visible, wide shot, multiple papers, stack of papers, overlapping papers,
paper folds, paper edge curling, paper shadow, glossy reflection on paper, paper texture on receipt,
writing on paper, printed text, barcode, QR, stamp, logo, watermark, stains, tears, rips, holes,
scotch tape, staples, paper clips, binding, framing, borders, margins, grid lines, rulers, measurement marks"""

workflow_template = {
    "1": { "class_type": "EmptyLatentImage", "inputs": { "width": 512, "height": 512, "batch_size": 1 } },
    "2": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" } },
    "3": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" } },
    "4": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default" } },
    "5": { "class_type": "CLIPTextEncode", "inputs": { "text": "", "clip": ["4", 0] } },
    "6": { "class_type": "CLIPTextEncode", "inputs": { "text": negative_prompt, "clip": ["4", 0] } },
    "7": { "class_type": "KSampler", "inputs": {
        "seed": 42, "steps": 28, "cfg": 4.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        "model": ["3", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["1", 0]
    }},
    "8": { "class_type": "VAEDecode", "inputs": { "samples": ["7", 0], "vae": ["2", 0] } },
    "9": { "class_type": "SaveImage", "inputs": { "images": ["8", 0], "filename_prefix": "Realistic_BG" } }
}

def generate_prompt(category, material, variant_num):
    import random
    from random import choice

    lighting = choice(lighting_styles)
    angle = choice(angles_compositions)
    placement = choice(placement_phrases).replace("{material}", material)

    detail = ""
    if category == "wood":
        detail = f"Visible wood grain, {'scratches and wear' if variant_num % 3 == 0 else 'natural texture'}, {'dark stain' if variant_num % 4 == 0 else 'natural finish'}"
    elif category == "stone":
        detail = f"Natural cleft texture, {'subtle veins' if variant_num % 2 == 0 else 'mineral speckles'}, matte non-reflective finish"
    elif category == "metal":
        detail = f"{'Rivets and welds' if variant_num % 3 == 0 else 'Smooth surface'}, {'patina' if variant_num % 4 == 0 else 'brushed finish'}, industrial aesthetic"
    elif category == "fabric":
        detail = f"Soft matte textile texture, {'slight folds' if variant_num % 3 == 0 else 'perfectly stretched'}, even weave"
    elif category == "plastic":
        detail = f"{'Matte non-reflective' if variant_num % 2 == 0 else 'Slight sheen'} finish, clean surface, modern material"
    elif category == "paper":
        detail = f"{'Slight texture' if variant_num % 2 == 0 else 'Smooth finish'}, natural fiber appearance, {'aged' if variant_num % 5 == 0 else 'pristine'}"
    elif category == "glass_ceramic":
        detail = f"{'Glossy finish' if variant_num % 2 == 0 else 'Matte glaze'}, {'crackled effect' if variant_num % 3 == 0 else 'smooth surface'}"
    elif category == "natural":
        detail = f"Organic texture, {'moist' if variant_num % 3 == 0 else 'dry'} appearance, natural earth tones"
    else: 
        detail = f"Professional photography surface, {'seamless' if variant_num % 2 == 0 else 'textured'}, studio quality"

    prompt = f"""{angle} of a large {material} surface. {detail}.
{placement}. {lighting}.
The paper is small compared to the massive surface, realistic scale and proportions.
Photorealistic, 8k, ultra high quality, professional product photography style."""

    return prompt

print("\n🎨 НАЧАЛО ГЕНЕРАЦИИ 300 ФОНОВ")
print("=" * 70)

generated_files = []
failed_count = 0
start_time = time.time()

total_to_generate = 300
combinations = []
categories = list(materials.keys())

for i in range(total_to_generate):
    category = categories[i % len(categories)]
    material_list = materials[category]
    material = material_list[i % len(material_list)]
    combinations.append((category, material, i))

print(f"📊 План генерации: {total_to_generate} изображений")
print(f"   Категории: {', '.join(categories)}")
print(f"   Всего материалов: {sum(len(m) for m in materials.values())}")
print("-" * 70)

for idx, (category, material, variant) in enumerate(combinations):
    print(f"\n🎲 Генерация #{idx+1:03d}/{total_to_generate}")
    print(f"   Категория: {category.upper()}")
    print(f"   Материал: {material[:50]}...")

    prompt_text = generate_prompt(category, material, variant)

    current_workflow = json.loads(json.dumps(workflow_template))
    current_workflow["5"]["inputs"]["text"] = prompt_text

    seed = 1000000 + (idx * 7777) + int(time.time() * 1000) % 99999
    current_workflow["7"]["inputs"]["seed"] = seed

    try:
        resp = requests.post("http://0.0.0.0/prompt", json={"prompt": current_workflow}, timeout=30)
        if resp.status_code != 200:
            print(f"   ❌ Ошибка отправки: {resp.status_code}")
            failed_count += 1
            continue

        prompt_id = resp.json().get('prompt_id')
        print(f"   ⏳ Генерация... (ID: {prompt_id[:8]}..., seed: {seed})")

        success = False
        for attempt in range(15): 
            time.sleep(12)
            try:
                hist = requests.get(f"http://0.0.0.0/history/{prompt_id}", timeout=15)
                if hist.status_code == 200 and prompt_id in hist.json():
                    outputs = hist.json()[prompt_id].get('outputs', {})
                    for node_out in outputs.values():
                        if 'images' in node_out:
                            img_info = node_out['images'][0]
                            img_resp = requests.get("http://0.0.0.0/view", params={
                                'filename': img_info['filename'],
                                'subfolder': img_info.get('subfolder', ''),
                                'type': img_info.get('type', 'output')
                            }, timeout=20)
                            if img_resp.status_code == 200:
                                filename = f"bg_{idx+1:03d}_{category}_{variant+1:03d}.png"
                                filepath = os.path.join(output_dir, filename)
                                with open(filepath, "wb") as f:
                                    f.write(img_resp.content)
                                print(f"   💾 Сохранено: {filename}")
                                generated_files.append(filepath)
                                if (idx + 1) % 10 == 0:
                                    pass

                                success = True
                                break
                    if success:
                        break
            except requests.exceptions.Timeout:
                if attempt < 14:
                    print(f"   ⏳ Ожидание... ({attempt+1}/15)")
                continue

        if not success:
            print(f"   ⚠️ Таймаут - изображение не получено")
            failed_count += 1

    except requests.exceptions.Timeout:
        print(f"   ⏰ Таймаут соединения")
        failed_count += 1
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)[:100]}")
        failed_count += 1

    if (idx + 1) % 10 == 0:
        print(f"\n📊 Прогресс: {idx+1}/{total_to_generate} | Успешно: {len(generated_files)} | Ошибок: {failed_count}")
        time.sleep(5)
    else:
        time.sleep(2)

end_time = time.time()
elapsed_minutes = (end_time - start_time) / 60

print("\n" + "=" * 70)
print("📊 ФИНАЛЬНЫЙ ОТЧЕТ")
print("=" * 70)
print(f"✅ Успешно сгенерировано: {len(generated_files)}/{total_to_generate}")
print(f"❌ Ошибок: {failed_count}")
print(f"⏱️  Время выполнения: {elapsed_minutes:.1f} минут")
print(f"📁 Папка с результатами: {os.path.abspath(output_dir)}")
print(f"💾 Среднее время на фон: {elapsed_minutes * 60 / max(len(generated_files), 1):.1f} сек")

metadata_file = os.path.join(output_dir, "metadata.json")
metadata = {
    "generation_date": datetime.now().isoformat(),
    "total_generated": len(generated_files),
    "total_requested": total_to_generate,
    "failed": failed_count,
    "time_minutes": elapsed_minutes,
    "files": generated_files,
    "categories_used": list(materials.keys()),
    "negative_prompt": negative_prompt[:200] + "..."
}

with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"📋 Метаданные сохранены: {metadata_file}")

readme_file = os.path.join(output_dir, "README.txt")
with open(readme_file, "w", encoding="utf-8") as f:
    f.write(f"""ФОНЫ ДЛЯ ЧЕКОВ - 300 ИЗОБРАЖЕНИЙ
{'=' * 50}

Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Количество: {len(generated_files)}/{total_to_generate}
Время генерации: {elapsed_minutes:.1f} минут

СТРУКТУРА ФАЙЛОВ:
bg_XXX_категория_YYY.png
  XXX - номер от 001 до 300
  категория - тип поверхности (wood, stone, metal, fabric, plastic, paper, glass_ceramic, natural, studio)
  YYY - вариант материала

ХАРАКТЕРИСТИКИ:
- Размер: 512x512 пикселей
- Формат: PNG
- Реалистичные поверхности из реальных материалов
- На каждой картинке: белый квадрат 400x400px (чек)
- Соразмерность: чек маленький на большой поверхности
- Без текста, без искажений чека

ИСПОЛЬЗОВАННЫЕ КАТЕГОРИИ:
{', '.join(categories)}

Дополнительная информация в файле metadata.json
""")

print(f"📄 README создан: {readme_file}")

if len(generated_files) >= 5:
    print("\n🖼️  ПРИМЕРЫ СГЕНЕРИРОВАННЫХ ФОНОВ:")
    for i in range(min(5, len(generated_files))):
        print(f"   {i+1}. {os.path.basename(generated_files[i])}")

print("\n" + "=" * 70)
print("🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
print(f"📁 Все фоны сохранены в папку: {output_dir}")
print("=" * 70)