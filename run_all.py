#!/usr/bin/env python3
"""
Запуск всего пайплайна генерации датасета чеков
"""

import subprocess
import sys
import time
from pathlib import Path

def run_script(script_path, description):
    """Запускает Python скрипт"""
    print(f"\n{'='*60}")
    print(f"🏃‍♂️ {description}")
    print(f"📄 {script_path}")
    print(f"{'='*60}")
    
    start = time.time()
    
    if not Path(script_path).exists():
        print(f"❌ Файл не найден: {script_path}")
        return False
    
    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {description} завершён за {time.time()-start:.1f} сек")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("🎯 ЗАПУСК ПАЙПЛАЙНА ГЕНЕРАЦИИ ДАТАСЕТА")
    print("="*60)
    print("\n⚠️ ВНИМАНИЕ:")
    print("   1. Сервер Stable Diffusion должен быть запущен на http://0.0.0.0")
    print("   2. Все зависимости установлены: pip install -r requirements.txt")
    print()
    
    response = input("Продолжить? (y/n): ")
    if response.lower() != 'y':
        return
    
    scripts = [
        ("1_background_generation/generate_backgrounds.py", "Генерация фонов"),
        ("2_background_analysis/analyze_backgrounds.py", "Анализ фонов"),
        ("3_receipt_generation/generate_receipts.py", "Генерация чеков"),
        ("4_receipt_defects/apply_defects.py", "Добавление дефектов"),
        ("5_annotations/create_annotations.py", "Создание аннотаций"),
        ("6_composition/compose_images.py", "Наложение на фон"),
        ("7_final_effects/apply_final_effects.py", "Финальные эффекты"),
        ("8_final_annotations/create_final_annotations.py", "Финальные аннотации"),
    ]
    
    for script, desc in scripts:
        if not run_script(script, desc):
            print(f"\n❌ Остановлено на шаге: {desc}")
            break
    
    print("\n✅ Пайплайн завершён!")

if __name__ == "__main__":
    main()