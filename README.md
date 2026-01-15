# PHPStaticRender

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![PHP](https://img.shields.io/badge/PHP-5.4%2B-purple)](https://www.php.net/)

PHPStaticRender is a Python tool that converts dynamic PHP projects into static HTML websites. It recursively traverses a directory, executes PHP files using the system's interpreter, and saves the output as HTML, while directly copying static files. Ideal for performance optimization and hosting on servers without PHP.

## Features

- **Complete Rendering**: Processes an entire PHP project recursively.
- **Automatic PHP Detection**: Finds the PHP executable on the system (XAMPP support on Windows).
- **Link Conversion**: Automatically converts internal `.php` links to `.html` in generated HTML.
- **Text Replacement**: Custom find-and-replace patterns via TOML configuration (URLs, placeholders, etc.).
- **Static File Copying**: Keeps CSS, JS, images, and other files intact.
- **Ignore System**: Configurable prefixes to ignore files (e.g., `__header.php`).
- **Flexible Configurations**: Customize output folders, extensions, and more via TOML file or script constants.
- **Detailed Reports**: Processing statistics and error handling.
- **Compatibility**: Works on Windows, Linux, and macOS.

## Requirements

- **Python**: 3.6 or higher.
- **PHP**: Installed on the system (CLI) with command-line execution support.
- **Operating System**: Windows, Linux, or macOS.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gmasson/phpstaticrender.git
   cd phpstaticrender
   ```
   or download the ZIP file from the repository and extract it.

2. **Ensure Python 3.x is installed**:
   ```bash
   python --version  # Should show 3.6+
   ```

3. **Check if PHP is installed**:
   ```bash
   php --version
   ```
   - On Windows, install [XAMPP](https://www.apachefriends.org/) if necessary.

## Basic Usage

1. **Copy the `phpstaticrender.py` script** to the root directory of your project (e.g., `index.php`, `about.php`, etc.).

2. **Run the script**:
   ```bash
   python phpstaticrender.py
   ```

3. **Done!** The static site will be generated in the `_PHPStaticRender` folder.

### Project Structure Example
```
my-project/
├── index.php
├── about.php
├── css/
│   └── style.css
├── js/
│   └── script.js
└── phpstaticrender.py
```

After execution:
```
my-project/
├── _PHPStaticRender/
│   ├── index.html
│   ├── about.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── ...
```

## Configurations

### Option 1: Using PHPStaticRender.toml (Optional - Recommended)

Create a `PHPStaticRender.toml` file in your project root to customize settings per project.
**This file is completely optional** - the script works perfectly without it using default settings.

```toml
[config]
output_folder = "_PHPStaticRender"
ignore_prefix = "__"
php_extension = ".php"
encoding = "utf-8"
safe_mode = false
manual_php_path = ""  # Auto-detect by default

ignore_system = [
    ".git", "node_modules", ".env"
]

# Replace patterns in generated HTML
[replace]
"http://localhost" = "https://example.com"
"http://127.0.0.1" = "https://example.com"
"/assets/" = "https://cdn.example.com/assets/"
"COMPANY_NAME" = "My Company Inc."
```

**Minimal Configuration**: Define only what you need:
```toml
[config]
output_folder = "dist"  # Only change output folder

[replace]
"http://localhost" = "https://mysite.com"  # Only one replacement
```

All other parameters use default values from the script.

**Benefits**:
- Project-specific configurations
- No need to edit Python code
- Easy text replacements (URLs, paths, placeholders)
- Version control friendly

**Requirements**: Install TOML library for Python < 3.11:
```bash
pip install toml
```

### Option 2: Edit phpstaticrender.py

Edit the constants at the top of `phpstaticrender.py`:

- **`CONFIG_OUTPUT_FOLDER`**: Destination folder (default: `_PHPStaticRender`)
- **`CONFIG_IGNORE_PREFIX`**: Prefix to ignore files (default: `__`)
- **`CONFIG_PHP_EXTENSION`**: PHP extension (default: `.php`)
- **`CONFIG_IGNORE_SYSTEM`**: Folders/files to ignore (e.g., `.git`, `node_modules`)
- **`CONFIG_ENCODING`**: Encoding (default: `utf-8`)
- **`CONFIG_MANUAL_PHP_PATH`**: Manual PHP path if detection fails
- **`CONFIG_SAFE_MODE`**: Safer PHP execution (default: `False`)

For detailed configurations, see [DOCUMENTATION.md](DOCUMENTATION.md#detailed-configurations).

## Troubleshooting

- **Error: "PHP executable not found"**: Install PHP or configure `CONFIG_MANUAL_PHP_PATH`
- **PHP files not processed**: Check if the extension is `.php` (case-sensitive)
- **Includes don't work**: Ensure relative paths are correct in PHP code
- **Encoding issues**: Change `CONFIG_ENCODING` to `cp1252` on legacy Windows

For detailed solutions, see [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting-and-common-issues).

## Contribution

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- [Report Bug](https://github.com/gmasson/phpstaticrender/issues/new?labels=bug)
- [Suggest Feature](https://github.com/gmasson/phpstaticrender/issues/new?labels=enhancement)
- [Improve Documentation](https://github.com/gmasson/phpstaticrender/issues/new?labels=documentation)

## Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
