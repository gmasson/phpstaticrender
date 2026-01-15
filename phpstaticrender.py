#!/usr/bin/env python3
"""
PHP Static Render - Static Site Generator via PHP CLI.

This script recursively traverses a project directory, finds PHP files,
executes them using the system's PHP interpreter and saves the HTML output in a destination folder.
Non-PHP files are copied directly.

Author: Gabriel Masson
License: MIT License
Requirements: Python 3.6+ and PHP installed on the system (CLI).
Version: 0.9
"""

import os
import re
import shutil
import subprocess
import sys
import platform
from typing import Optional, List, Set, Dict, Any

# TOML parsing library (Python 3.11+ uses tomllib, older versions need toml package)
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None

# CONFIGURATION AREA (Edit as necessary)

# Name of the TOML configuration file (optional)
CONFIG_FILE_NAME: str = 'PHPStaticRender.toml'

# Folder where the final site will be generated. CAUTION: This folder is cleaned on each build.
CONFIG_OUTPUT_FOLDER: str = '_PHPStaticRender'

# Prefix for files that should be IGNORED entirely (e.g., pure includes).
# Example: '__header.php' will be ignored. '_menu.php' will be processed.
CONFIG_IGNORE_PREFIX: str = '__'

# Extension of files that should be interpreted by the PHP engine.
CONFIG_PHP_EXTENSION: str = '.php'

# List of system folders and files to be ignored to optimize the process.
CONFIG_IGNORE_SYSTEM: Set[str] = {
    '.git', '.gitignore', '.idea', '.vscode', '__pycache__', 'node_modules', 'vendor', '.DS_Store', 'Thumbs.db', '.env', '.env.local', '.env.production', '.key', CONFIG_OUTPUT_FOLDER, '.logs', '.tmp', '.temp', '.nyc_output', 'composer.lock', 'package-lock.json', 'yarn.lock', '.phpunit.result.cache', 'phpunit.xml', '.phpcs.cache'
}

# Subprocess PHP configurations
# 'utf-8' is the recommended standard. Change to 'cp1252' only on legacy Windows if it gives an error.
CONFIG_ENCODING: str = 'utf-8' 

# Optional safe mode for PHP execution. When enabled, it disables risky PHP functions
# and remote URL access during rendering. Leave False to preserve original behavior.
CONFIG_SAFE_MODE: bool = False

# Manual PHP path (if automatic detection fails). 
# Leave None to try to detect.
CONFIG_MANUAL_PHP_PATH: Optional[str] = None

# SYSTEM LOGIC

def load_config_from_toml(root_dir: str) -> Dict[str, Any]:
    """
    Loads configuration from PHPStaticRender.toml file if it exists.
    
    Args:
        root_dir (str): Project root directory.
    
    Returns:
        Dict[str, Any]: Dictionary with 'config' and 'replace' sections.
                        Returns empty dict if file doesn't exist or TOML library is not available.
    """
    toml_path = os.path.join(root_dir, CONFIG_FILE_NAME)
    
    if not os.path.exists(toml_path):
        return {'config': {}, 'replace': {}}
    
    if tomllib is None:
        print(f"INFO: TOML library not available. To use '{CONFIG_FILE_NAME}', install with: pip install toml")
        print(f"      Using default configuration from script.")
        return {'config': {}, 'replace': {}}
    
    try:
        # Python 3.11+ uses binary mode, older versions use text mode
        if hasattr(tomllib, 'loads'):
            with open(toml_path, 'rb') as f:
                config_data = tomllib.load(f)
        else:
            with open(toml_path, 'r', encoding='utf-8') as f:
                config_data = tomllib.load(f)
        
        print(f"Configuration loaded from: {CONFIG_FILE_NAME}")
        return config_data
    except Exception as e:
        print(f"WARNING: Error reading '{CONFIG_FILE_NAME}': {e}")
        print(f"         Using default configuration.")
        return {'config': {}, 'replace': {}}

def apply_config_from_toml(toml_data: Dict[str, Any]):
    """
    Applies configuration from TOML data to global CONFIG variables.
    
    Args:
        toml_data (Dict[str, Any]): Parsed TOML configuration data.
    """
    global CONFIG_OUTPUT_FOLDER, CONFIG_IGNORE_PREFIX, CONFIG_PHP_EXTENSION
    global CONFIG_IGNORE_SYSTEM, CONFIG_ENCODING, CONFIG_SAFE_MODE, CONFIG_MANUAL_PHP_PATH
    
    config = toml_data.get('config', {})
    
    if 'output_folder' in config:
        CONFIG_OUTPUT_FOLDER = config['output_folder']
    
    if 'ignore_prefix' in config:
        CONFIG_IGNORE_PREFIX = config['ignore_prefix']
    
    if 'php_extension' in config:
        CONFIG_PHP_EXTENSION = config['php_extension']
    
    if 'encoding' in config:
        CONFIG_ENCODING = config['encoding']
    
    if 'safe_mode' in config:
        CONFIG_SAFE_MODE = config['safe_mode']
    
    if 'manual_php_path' in config and config['manual_php_path']:
        CONFIG_MANUAL_PHP_PATH = config['manual_php_path']
    
    if 'ignore_system' in config:
        # Merge with default ignore list
        CONFIG_IGNORE_SYSTEM.update(config['ignore_system'])
        # Always ignore the output folder
        CONFIG_IGNORE_SYSTEM.add(CONFIG_OUTPUT_FOLDER)

def apply_replacements(html_content: str, replacements: Dict[str, str]) -> str:
    """
    Applies text replacements defined in TOML [replace] section.
    
    Args:
        html_content (str): HTML content to process.
        replacements (Dict[str, str]): Dictionary of search -> replace patterns.
    
    Returns:
        str: HTML content with replacements applied.
    """
    if not replacements:
        return html_content
    
    result = html_content
    for search_pattern, replacement_text in replacements.items():
        result = result.replace(search_pattern, replacement_text)
    
    return result

def configure_console_encoding():
    """
    Forces the terminal to use UTF-8 to avoid errors with emojis on Windows.
    """
    if sys.platform == "win32":
        try:
            # Python 3.7+ supports reconfigure
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # Fallback for older versions
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
        except Exception:
            pass # Continues if it can't be configured

def find_php_executable() -> Optional[str]:
    """
    Locates the PHP executable on the operating system.
    
    Tries to find PHP in the following order:
    1. Manual configuration (CONFIG_MANUAL_PHP_PATH).
    2. System PATH environment variable ('php' command).
    3. Default XAMPP paths on Windows.

    Returns:
        Optional[str]: Absolute path to the executable or None if not found.
    """
    # 1. Checks manual configuration
    if CONFIG_MANUAL_PHP_PATH and os.path.exists(CONFIG_MANUAL_PHP_PATH):
        return CONFIG_MANUAL_PHP_PATH

    # 2. Tries to find in global PATH (Linux/Mac/Windows configured)
    php_path = shutil.which('php')
    if php_path:
        return php_path

    # 3. Fallback for Windows (default XAMPP)
    if sys.platform == "win32":
        xampp_path = r"C:\xampp\php\php.exe"
        if os.path.exists(xampp_path):
            return xampp_path
            
    return None

def convert_internal_php_links(html_content: str) -> str:
    """
    Converts internal .php links to .html in the generated HTML.
    
    This function searches for common HTML attributes that may contain internal links
    (href, src, action, data-* attributes) and replaces .php extensions with .html.
    Only processes relative links (not external URLs with http/https/mailto/tel/ftp schemes).
    
    Args:
        html_content (str): The HTML content to process.
    
    Returns:
        str: HTML content with converted links.
    """
    # Pattern to match links in common HTML attributes (href, src, action, data-*)
    # Only converts if the link:
    # 1. Ends with .php (case-insensitive)
    # 2. Is not an external URL (doesn't start with http://, https://, mailto:, tel:, ftp://, //)
    # 3. Is not a PHP variable or template tag
    
    def replace_link(match):
        attr_name = match.group(1)
        quote = match.group(2)
        url = match.group(3)
        
        # Skip external URLs and special protocols
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'ftp://', '//', '#')):
            return match.group(0)
        
        # Skip PHP variables and template tags
        if '<?php' in url or '<?=' in url or '{' in url or '$' in url:
            return match.group(0)
        
        # Convert .php to .html (case-insensitive)
        if url.lower().endswith('.php'):
            converted_url = url[:-4] + '.html'
            return f'{attr_name}={quote}{converted_url}{quote}'
        
        # Also handle .php with query strings or anchors
        php_pattern = re.compile(r'\.php([?#])', re.IGNORECASE)
        if php_pattern.search(url):
            converted_url = php_pattern.sub(r'.html\1', url)
            return f'{attr_name}={quote}{converted_url}{quote}'
        
        return match.group(0)
    
    # Regex to match href, src, action, and data-* attributes
    pattern = re.compile(
        r'((?:href|src|action|data-[\w-]+))\s*=\s*(["\'])([^"\'>]+)\2',
        re.IGNORECASE
    )
    
    return pattern.sub(replace_link, html_content)

def render_php_file(php_exec: str, src_path: str, cwd: str) -> str:
    """
    Executes a PHP file and captures its output (stdout).

    Args:
        php_exec (str): Path to the PHP executable.
        src_path (str): Absolute path of the PHP file to be processed.
        cwd (str): Project root directory (so includes work).

    Returns:
        str: The generated HTML code.

    Raises:
        subprocess.CalledProcessError: If PHP returns a fatal error.
    """
    # Executes PHP. 
    # check=True raises exception if PHP errors (exit code != 0)
    php_args: List[str] = [php_exec]
    if CONFIG_SAFE_MODE:
        php_args.extend([
            '-d', 'disable_functions=exec,system,shell_exec,passthru,proc_open,popen',
            '-d', 'allow_url_fopen=0',
            '-d', 'allow_url_include=0'
        ])
    php_args.append(src_path)

    result = subprocess.run(
        php_args,
        capture_output=True,
        text=True,
        cwd=cwd, 
        check=True,
        encoding=CONFIG_ENCODING,
        errors='replace' # Replaces invalid characters instead of crashing
    )
    return result.stdout

def build_static_site():
    """
    Main function that orchestrates the static site generation.
    1. Loads configuration from PHPStaticRender.toml (if exists).
    2. Prepares directories.
    3. Scans files recursively.
    4. Processes PHP or copies static files.
    5. Applies replacements from TOML.
    6. Generates final report.
    """
    root_dir = os.getcwd()
    
    # Load TOML configuration
    toml_data = load_config_from_toml(root_dir)
    apply_config_from_toml(toml_data)
    replacements = toml_data.get('replace', {})
    
    dist_dir = os.path.join(root_dir, CONFIG_OUTPUT_FOLDER)
    script_filename = os.path.basename(__file__)
    
    print("=" * 60)
    print(f"PHP Static Render | System: {platform.system()} {platform.release()}")
    
    php_exec = find_php_executable()
    if not php_exec:
        print("CRITICAL ERROR: PHP executable not found.")
        print("   Make sure PHP is installed or configure 'CONFIG_MANUAL_PHP_PATH'.")
        sys.exit(1)
    
    print(f"PHP Engine: {php_exec}")
    print(f"Source: {root_dir}")
    print(f"Destination: {CONFIG_OUTPUT_FOLDER}")
    print("=" * 60)

    # --- Cleanup ---
    root_real = os.path.realpath(root_dir)
    dist_real = os.path.realpath(dist_dir)
    if not dist_real.startswith(root_real + os.sep) or dist_real == root_real:
        print("ERROR: Invalid output folder. It must be a subfolder of the project root.")
        print(f"   root: {root_real}")
        print(f"   output: {dist_real}")
        sys.exit(1)

    if os.path.exists(dist_dir):
        try:
            shutil.rmtree(dist_dir)
        except OSError as e:
            print(f"WARNING: Failed to clean old folder ({e}). Trying to continue...")
    
    try:
        os.makedirs(dist_dir, exist_ok=True)
    except OSError as e:
        print(f"ERROR: Could not create destination folder: {e}")
        sys.exit(1)

    # --- Counters for statistics ---
    stats = {'php': 0, 'static': 0, 'ignored': 0, 'errors': 0}

    # --- Processing Loop ---
    for current_root, dirs, files in os.walk(root_dir, followlinks=False):
        # Filters ignored folders in-place
        filtered_dirs = []
        for d in dirs:
            if d in CONFIG_IGNORE_SYSTEM or d.startswith('.'):
                continue
            dir_path = os.path.join(current_root, d)
            if os.path.islink(dir_path):
                stats['ignored'] += 1
                continue
            filtered_dirs.append(d)
        dirs[:] = filtered_dirs

        for file in files:
            # Skips the script itself and hidden files
            if file == script_filename or file in CONFIG_IGNORE_SYSTEM or file.startswith('.'):
                continue

            # Checks ignore prefix (e.g., __header.php)
            if file.startswith(CONFIG_IGNORE_PREFIX):
                stats['ignored'] += 1
                continue

            # Skips symbolic links to avoid external traversal
            if os.path.islink(os.path.join(current_root, file)):
                stats['ignored'] += 1
                continue
            
            # Paths
            src_file_path = os.path.join(current_root, file)
            rel_path = os.path.relpath(src_file_path, root_dir)
            dest_file_path = os.path.join(dist_dir, rel_path)
            
            # Creates subfolders in destination
            os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

            # Processing
            if file.lower().endswith(CONFIG_PHP_EXTENSION):
                # PHP case: Executes and Saves .html
                dest_html_path = os.path.splitext(dest_file_path)[0] + '.html'
                
                try:
                    html_content = render_php_file(php_exec, src_file_path, root_dir)
                    
                    # Convert internal .php links to .html
                    html_content = convert_internal_php_links(html_content)
                    
                    # Apply replacements from TOML configuration
                    html_content = apply_replacements(html_content, replacements)
                    
                    with open(dest_html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    print(f"[PHP] {rel_path} -> .html")
                    stats['php'] += 1

                except subprocess.CalledProcessError as e:
                    print(f"[PHP ERROR] {rel_path}")
                    # Displays only the last lines of the error for easier reading
                    err_msg = e.stderr.strip().split('\n')[-5:]
                    print("   └── " + "\n   └── ".join(err_msg))
                    stats['errors'] += 1
                except Exception as ex:
                    print(f"[IO ERROR] {rel_path}: {ex}")
                    stats['errors'] += 1
            else:
                # Static case: Simple copy
                try:
                    shutil.copy2(src_file_path, dest_file_path)
                    print(f"[COPY] {rel_path}")
                    stats['static'] += 1
                except Exception as ex:
                    print(f"[COPY ERROR] {rel_path}: {ex}")
                    stats['errors'] += 1

    # --- Finalization ---
    print("-" * 60)
    print(f"Process Completed!")
    print(f"Statistics: {stats['php']} Pages | {stats['static']} Files | {stats['ignored']} Ignored | {stats['errors']} Errors")
    print(f"Site available at: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    # Welcome message - displayed immediately before any configuration
    print("", flush=True)
    print("=" * 70, flush=True)
    print(r"  ____  _   _ ____  ____  _        _   _      ____                 _", flush=True)
    print(r" |  _ \| | | |  _ \/ ___|| |_ __ _| |_(_) ___| |  _ ___ _ __   __| | ___ _ __", flush=True)
    print(r" | |_) | |_| | |_) \___ \| __/ _` | __| |/ __| |_| / _ \ '_ \ / _` |/ _ \ '__|", flush=True)
    print(r" |  __/|  _  |  __/ ___) | || (_| | |_| | (__|  _ |  __/ | | | (_| |  __/ |", flush=True)
    print(r" |_|   |_| |_|_|   |____/ \__\__,_|\__|_|\___|_| \_\___|_| |_|\__,_|\___|_|", flush=True)
    print("", flush=True)
    print("  PHP Static Site Generator - Convert PHP to Static HTML", flush=True)
    print("  Author: Gabriel Masson | License: MIT | Version: 0.9", flush=True)
    print("=" * 70, flush=True)
    print("", flush=True)
    print("  Welcome! This tool will process your PHP files and generate a static website.", flush=True)
    print("  The rendering process will traverse your project directory recursively,", flush=True)
    print("  execute PHP files via CLI, and save the output as HTML.", flush=True)
    print("", flush=True)
    print("  Requirements:", flush=True)
    print("    - Python 3.6+ (installed)", flush=True)
    print("    - PHP CLI (must be available in your system)", flush=True)
    print("", flush=True)
    print("  Starting the build process...", flush=True)
    print("", flush=True)
    
    # Configures console encoding after welcome message
    configure_console_encoding()
    
    try:
        build_static_site()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        # Safe fallback in case the error itself contains non-printable characters
        try:
            print(f"\nUnhandled fatal error: {e}")
        except UnicodeEncodeError:
             print(f"\n[X] Unhandled fatal error (ASCII only): {e}")