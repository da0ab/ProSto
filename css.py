import re
from collections import defaultdict
import sass
import os
from pathlib import Path
from csscompressor import compress

# =============================================
# КОНФИГУРАЦИЯ
# =============================================
config = {
    'main': {
        'input_files': ['src/components/ProSto.scss'],
        'include_paths': ['src/components'],
        'combined_output': 'build/css/ProSto.css',
        'compressed_output': 'build/css/ProSto.min.css'
    },
    'dubak': {
        'input_files': [
            'src/components/ProSto.scss',
            'src/components/ProSto-CMS.scss'
        ],
        'include_paths': ['src/components'],
        'combined_output': 'build/css/ProStoCMS.css',
        'compressed_output': 'build/css/ProStoCMS.min.css'
    }
}

# =============================================
# ОСНОВНЫЕ ФУНКЦИИ
# =============================================
def ensure_directory_exists(filepath):
    """Создает директории, если они не существуют"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def compile_sass(input_files, include_paths):
    """Компилирует SASS/SCSS в CSS"""
    try:
        abs_include_paths = [str(Path(p).resolve()) for p in include_paths]
        return sass.compile(
            string='\n'.join(open(f, 'r', encoding='utf-8').read() for f in input_files),
            include_paths=abs_include_paths,
            output_style='expanded'
        )
    except Exception as e:
        print(f"Ошибка компиляции: {e}")
        return None

def protect_svg_data_urls(css_content):
    """
    Защищает SVG в data: URL от изменений при сжатии.
    Обрабатывает случаи:
    - background:url('data:image/svg+xml;utf8,<svg...')
    - background:url("data:image/svg+xml;charset=UTF-8,<svg...")
    - src:url(data:image/svg+xml;base64,...)
    """
    protected = {}
    counter = 0

    def replace_fn(match):
        nonlocal counter
        key = f'___SVG_DATA_URL_{counter}___'
        protected[key] = match.group(0)
        counter += 1
        return key

    # Регулярное выражение для поиска всех data: URL с SVG
    pattern = r'''
    url\(                                  # начало url(
    (['"]?)                                # необязательные кавычки
    data:image/svg\+xml                    # тип данных
    (;[^\s'"]+)?                           # параметры (charset, utf8 и т.д.)
    ,                                      # разделитель
    (?:[^)'"]|'[^']*'|"[^"]*")*           # содержимое SVG (с учетом кавычек)
    \1                                     # закрывающие кавычки (если были)
    \)                                     # закрывающая скобка
    '''
    protected_css = re.sub(
        pattern,
        replace_fn,
        css_content,
        flags=re.VERBOSE | re.IGNORECASE
    )

    return protected_css, protected

def restore_svg_data_urls(css_content, protected):
    """Восстанавливает оригинальные SVG data: URL после сжатия"""
    result = css_content
    for key, value in protected.items():
        result = result.replace(key, value)
    return result

def clean_empty_lines(css_content):
    """Удаляет пустые строки, сохраняя структуру"""
    cleaned = re.sub(r'\n\s*\n', '\n', css_content)
    return cleaned.strip()

def group_media_queries(css_content):
    """Группирует медиазапросы, сохраняя структуру CSS"""
    blocks = []
    current_block = []
    brace_level = 0

    for line in css_content.split('\n'):
        brace_level += line.count('{') - line.count('}')
        current_block.append(line)

        if brace_level == 0 and current_block:
            blocks.append('\n'.join(current_block))
            current_block = []

    media_dict = defaultdict(list)
    other_blocks = []

    for block in blocks:
        if block.strip().startswith('@media'):
            media_condition = block.split('{', 1)[0].strip()
            content = block.split('{', 1)[1].rsplit('}', 1)[0].strip()
            media_dict[media_condition].append(content)
        else:
            other_blocks.append(block.strip())

    result = other_blocks.copy()
    for condition, contents in media_dict.items():
        grouped_content = '  ' + '\n  '.join(contents)
        result.append(f"{condition} {{\n{grouped_content}\n}}")

    return '\n\n'.join(result)

def process_config(conf_name):
    """Обрабатывает одну конфигурацию"""
    conf = config[conf_name]
    print(f"\n🔧 Обработка {conf_name} конфигурации")

    # 1. Компиляция SASS
    print(f"⚙️ Компиляция {len(conf['input_files'])} файлов...")
    css = compile_sass(conf['input_files'], conf['include_paths'])
    if not css:
        return False

    # 2. Группировка медиазапросов
    print("🔄 Группировка медиазапросов...")
    grouped_css = group_media_queries(css)

    # 3. Очистка от пустых строк
    print("🧹 Удаление пустых строк...")
    cleaned_css = clean_empty_lines(grouped_css)

    # Сохраняем читаемую версию
    ensure_directory_exists(conf['combined_output'])
    with open(conf['combined_output'], 'w', encoding='utf-8') as f:
        f.write(cleaned_css)
    print(f"✅ Читаемая версия: {conf['combined_output']}")

    # 4. Сжатие с защитой SVG data: URL
    print("💾 Создание сжатой версии с защитой SVG...")

    # Защищаем SVG data: URL перед сжатием
    protected_css, protected_urls = protect_svg_data_urls(cleaned_css)

    # Сжимаем CSS
    compressed = compress(protected_css)

    # Восстанавливаем SVG data: URL
    final_css = restore_svg_data_urls(compressed, protected_urls)

    ensure_directory_exists(conf['compressed_output'])
    with open(conf['compressed_output'], 'w', encoding='utf-8') as f:
        f.write(final_css)
    print(f"✅ Сжатая версия с защищенными SVG: {conf['compressed_output']}")

    return True

# =============================================
# ЗАПУСК СКРИПТА
# =============================================
def main():
    print("="*50)
    print("🎨 SASS Компилятор v2.9 (с защитой SVG data: URL)")
    print("="*50)

    try:
        import sass
        from csscompressor import compress
    except ImportError as e:
        print(f"❌ Требуются зависимости: {e}")
        print("Установите: pip install libsass csscompressor")
        return

    success = all(process_config(conf) for conf in config)
    print("\n✨ Готово!" if success else "\n❌ Были ошибки!")

if __name__ == '__main__':
    main()
