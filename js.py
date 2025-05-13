import os
import re
from pathlib import Path
import rjsmin


def process_js_files(src_dir='src/components', dist_dir='build/js'):
    Path(dist_dir).mkdir(parents=True, exist_ok=True)

    init_content = []
    vendor_content = []
    vendor_dubak_content = []  # Для ProStoCMS.min.js (vendor + dubak)

    init_pattern = re.compile(r'.*-init\.js$')
    vendor_pattern = re.compile(r'.*-vendor\.js$')
    dubak_pattern = re.compile(r'.*-dubak\.js$')

    for root, _, files in os.walk(src_dir):
        for file in files:
            if not file.endswith('.js'):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if init_pattern.search(file):
                init_content.append(content)
            elif vendor_pattern.search(file):
                vendor_content.append(content)
                vendor_dubak_content.append(content)  # Добавляем в оба!
            elif dubak_pattern.search(file):
                vendor_dubak_content.append(content)

    # 1. init.js (без оптимизации)
    if init_content:
        with open(os.path.join(dist_dir, 'init.js'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(init_content))

    # 2. ProTo.min.js (только vendor, оптимизированный)
    if vendor_content:
        optimized = rjsmin.jsmin('\n'.join(vendor_content))
        with open(os.path.join(dist_dir, 'ProSto.min.js'), 'w', encoding='utf-8') as f:
            f.write(optimized)

    # 3. ProToD.min.js (vendor + dubak, оптимизированный)
    if vendor_dubak_content:
        optimized = rjsmin.jsmin('\n'.join(vendor_dubak_content))
        with open(os.path.join(dist_dir, 'ProStoCMS.min.js'), 'w', encoding='utf-8') as f:
            f.write(optimized)


if __name__ == '__main__':
    process_js_files()
    print("Сборка завершена!")
