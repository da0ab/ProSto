import re
import json
import sys
import shutil
from pathlib import Path
from urllib.parse import urlparse

# ================= CONFIG =================
SRC_DIR = 'src'                      # HTML source directory
DIST_DIR = 'build'                    # Output directory
CSS_SOURCE = 'build/css/style.css'    # Main CSS file to copy
CSS_OUTPUT_DIR = 'build/css'          # Directory for domain CSS copies
# =========================================

def sanitize_domain(url):
    """Convert URL to safe filename"""
    domain = urlparse(url).netloc or urlparse(url).path
    domain = re.sub(r'^https?://(www\.)?', '', domain)
    return re.sub(r'[^\w\-\.]', '_', domain).rstrip('.')

def copy_css_file(url_param):
    """Copy CSS file with domain name"""
    if not url_param:
        return None

    source = Path(CSS_SOURCE)
    if not source.exists():
        print(f"⚠️ Source CSS not found: {source}")
        return None

    domain = sanitize_domain(url_param)
    css_dir = Path(CSS_OUTPUT_DIR)
    css_dir.mkdir(parents=True, exist_ok=True)
    destination = css_dir / f"{domain}.css"

    try:
        shutil.copy2(source, destination)
        print(f"✅ CSS copied: {source} → {destination}")
        return f"css/{domain}.css"
    except Exception as e:
        print(f"❌ CSS copy error: {e}")
        return None

def fix_json(json_str):
    """Fix common JSON issues in includes"""
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return re.sub(r"'([^']+)'", r'"\1"', json_str)

def replace_placeholders(content, params):
    """Replace all placeholders in content"""
    for key, value in params.items():
        content = content.replace(f'@@{key}', str(value))
        content = content.replace(f'{{{{{key}}}}}', str(value))
    return content

def process_includes(content, base_dir, variables=None):
    """Process @@include directives"""
    def handle_include(match):
        file_path, json_params = match.groups()
        full_path = (base_dir / file_path).resolve()

        if not full_path.exists():
            return f"<!-- File not found: {file_path} -->"

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                included_content = f.read()

            params = json.loads(fix_json(json_params or '{}'))
            if variables:
                params.update(variables)  # Merge with global variables

            processed = replace_placeholders(included_content, params)
            return process_includes(processed, full_path.parent, variables)
        except Exception as e:
            return f"<!-- Processing error: {str(e)} -->"

    return re.sub(
        r'@@include\(\'(.*?)\'(?:,\s*({.*?})\s*)?\)',
        handle_include,
        content,
        flags=re.DOTALL
    )

def build_project():
    """Main build function"""
    # Parse command line arguments
    params = {'url': ''}  # Default empty URL
    if len(sys.argv) > 1:
        params['url'] = sys.argv[1]  # First argument is always URL
        for arg in sys.argv[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                params[key] = value

    # Copy CSS if URL provided
    if params['url']:
        css_path = copy_css_file(params['url'])
        if css_path:
            params['css_path'] = css_path

    # Process HTML files
    dist_dir = Path(DIST_DIR)
    dist_dir.mkdir(exist_ok=True)

    for html_file in Path(SRC_DIR).glob('*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process includes first
        processed = process_includes(content, html_file.parent, params)
        # Then replace remaining placeholders
        processed = replace_placeholders(processed, params)

        output_file = dist_dir / html_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed)

        print(f"🛠 Processed: {html_file} → {output_file}")

    # Verify URL was inserted
    if params['url']:
        print(f"\n🔍 URL parameter check:")
        print(f" - Parameter value: {params['url']}")
        sample_output = list(dist_dir.glob('*.html'))[0]
        with open(sample_output, 'r', encoding='utf-8') as f:
            if params['url'] in f.read():
                print(f"✅ URL found in {sample_output.name}")
            else:
                print(f"❌ URL NOT found in output files!")

if __name__ == '__main__':
    build_project()
