# PHPStaticRender Documentation

## Index

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Detailed Configurations](#detailed-configurations)
- [Technical Requirements](#technical-requirements)
- [Troubleshooting](#troubleshooting-and-common-issues)
- [Security](#security)
- [Additional Resources](#additional-resources)
- [Contribution](#contribution-and-support)

---

## Overview

PHPStaticRender is a lightweight and efficient Python tool that converts dynamic PHP projects into static HTML websites. The tool recursively scans the entire project directory, executing PHP files via CLI and saving the output as HTML, while directly copying static files (CSS, JS, images, fonts) to the destination folder, preserving the original folder structure.

### Why Use It?

- **Performance**: Pre-rendered HTML eliminates server-side processing
- **SEO**: Better indexing by search engines
- **Hosting**: Free deployment on GitHub Pages, Netlify, Vercel
- **Security**: No PHP exposed in production
- **Use Cases**: Prototypes, documentation, blogs, portfolios

## How It Works

### Execution Flow

1. **PHP Detection**: Searches in `CONFIG_MANUAL_PHP_PATH`, global PATH, or `C:\xampp\php\php.exe`
2. **Preparation**: Cleans and recreates output folder
3. **Scanning**: Traverses directory ignoring configured folders/files
4. **Processing**:
   - **PHP**: Executes via `subprocess.run()` and saves stdout as `.html`
   - **Link Conversion**: Automatically converts internal `.php` links to `.html` in generated HTML
   - **Text Replacement**: Applies custom replacements from TOML `[replace]` section
   - **Static**: Copies with `shutil.copy2()` preserving metadata
5. **Report**: Statistics (files processed, copied, ignored, errors)

### Automatic Link Conversion

PHPStaticRender automatically converts internal `.php` links to `.html` in the generated HTML output. This ensures that all navigation links work correctly in the static site.

**What gets converted**:
- `href` attributes: `<a href="about.php">` → `<a href="about.html">`
- `src` attributes: `<script src="script.php">` → `<script src="script.html">`
- `action` attributes: `<form action="process.php">` → `<form action="process.html">`
- `data-*` attributes: `<div data-url="page.php">` → `<div data-url="page.html">`

**What does NOT get converted** (preserved as-is):
- External URLs: `https://example.com/page.php`
- Special protocols: `mailto:`, `tel:`, `ftp://`
- Anchors: `#section`
- PHP variables/templates: `<?php echo $url ?>`
- Query strings and anchors: `page.php?id=1` → `page.html?id=1`

**Example**:

Original PHP:
```php
<a href="contact.php">Contact</a>
<a href="products.php?cat=1">Products</a>
<a href="https://external.com/page.php">External</a>
```

Generated HTML:
```html
<a href="contact.html">Contact</a>
<a href="products.html?cat=1">Products</a>
<a href="https://external.com/page.php">External</a>
```

This conversion happens automatically - no configuration needed!

### Technology

- **Python 3.6+** with stdlib modules (zero dependencies)
- **PHP CLI** for file execution
- **Cross-platform**: Windows, Linux, macOS

## Detailed Configurations

PHPStaticRender offers two configuration methods:

1. **PHPStaticRender.toml** (Optional - Recommended) - Project-specific configuration file
2. **Script constants** - Direct editing of `phpstaticrender.py`

**Important**: The TOML configuration file is **completely optional**. The script works perfectly without it using default configurations defined in the script.

### Configuration via PHPStaticRender.toml (Optional)

Create a `PHPStaticRender.toml` file in your project root for per-project customization. This method is recommended because:

- ✅ No need to modify the Python script
- ✅ Easy to version control
- ✅ Project-specific settings
- ✅ Powerful text replacement feature

#### Basic Structure

```toml
[config]
output_folder = "_PHPStaticRender"
ignore_prefix = "__"
php_extension = ".php"
encoding = "utf-8"
safe_mode = false
manual_php_path = ""

ignore_system = [
    ".git", ".gitignore", ".idea", ".vscode",
    "node_modules", "vendor", ".env"
]

[replace]
# Add your custom replacements here
```

**Important**: You can define **only the parameters you want to customize**. All others will use default values from the script.

#### Minimal Configuration Examples

**Example 1: Change only output folder**
```toml
[config]
output_folder = "dist"

# All other parameters use defaults:
# ignore_prefix = "__"
# php_extension = ".php"
# encoding = "utf-8"
# safe_mode = false
# etc.
```

**Example 2: Only replacements (no config changes)**
```toml
# [config] section can be completely omitted!

[replace]
"http://localhost" = "https://example.com"
"/assets/" = "https://cdn.example.com/assets/"
```

**Example 3: Production settings**
```toml
[config]
output_folder = "dist"
safe_mode = true
# Other parameters use defaults

[replace]
"http://localhost" = "https://mysite.com"
"/assets/" = "https://cdn.mysite.com/assets/"
```

#### Configuration Options

**`output_folder`** (string)  
Folder where the site will be generated. Cleaned on each execution.
```toml
output_folder = "dist"  # or "build", "public", etc.
```

**`ignore_prefix`** (string)  
Files starting with this prefix are ignored.
```toml
ignore_prefix = "__"  # __header.php won't be processed
```

**`php_extension`** (string)  
Extension of files to process with PHP.
```toml
php_extension = ".php"
```

**`encoding`** (string)  
Character encoding for subprocess communication.
```toml
encoding = "utf-8"  # or "cp1252" for legacy Windows
```

**`safe_mode`** (boolean)  
Enables safer PHP execution (disables risky functions).
```toml
safe_mode = true
```

**`manual_php_path`** (string)  
Manual PHP path if auto-detection fails.
```toml
manual_php_path = "C:\\xampp\\php\\php.exe"  # Windows
# manual_php_path = "/usr/local/bin/php"  # Linux/macOS
```

**`ignore_system`** (array)  
Folders and files to ignore during scanning.
```toml
ignore_system = [
    ".git", "node_modules", "vendor",
    ".env", "uploads", "cache"
]
```

**Note**: Values defined here are **merged** with default ignore list from the script. You don't need to repeat default values - just add your custom folders.

#### Text Replacements with [replace]

The `[replace]` section allows you to replace text patterns in generated HTML. This is extremely useful for:

- Converting development URLs to production URLs
- Replacing API endpoints
- Updating CDN paths
- Substituting placeholder text
- Adjusting absolute paths

**Syntax**:
```toml
[replace]
"search_pattern" = "replacement_text"
```

**Common Examples**:

```toml
[replace]
# Replace localhost with production domain
"http://localhost" = "https://example.com"
"http://127.0.0.1" = "https://example.com"
"http://localhost:8080" = "https://example.com"

# Replace development paths with CDN
"/assets/" = "https://cdn.example.com/assets/"
"/images/" = "https://cdn.example.com/images/"

# Replace API endpoints
"http://localhost:8080/api" = "https://api.example.com"
"http://dev-api.local" = "https://api.production.com"

# Replace placeholder text
"COMPANY_NAME_PLACEHOLDER" = "Acme Corporation"
"YOUR_EMAIL_HERE" = "contact@example.com"
"SITE_TITLE" = "My Awesome Website"

# Replace environment-specific values
"data-env=\"development\"" = "data-env=\"production\""
"DEBUG_MODE" = "PRODUCTION_MODE"
```

**Advanced Example**:

```toml
[config]
output_folder = "dist"
safe_mode = true
encoding = "utf-8"

ignore_system = [
    ".git", "node_modules", "src",
    ".env", "uploads", "cache", "temp"
]

[replace]
# Domain replacements
"http://localhost" = "https://mysite.com"
"http://localhost:3000" = "https://mysite.com"

# CDN paths
"/css/" = "https://cdn.mysite.com/css/"
"/js/" = "https://cdn.mysite.com/js/"
"/images/" = "https://cdn.mysite.com/images/"

# API endpoints
"http://localhost:8080/api/v1" = "https://api.mysite.com/v1"

# Analytics and tracking (add production codes)
"UA-XXXXXXXXX-X" = "UA-12345678-1"
"GTM-XXXXXXX" = "GTM-ABC1234"

# Contact information
"contact@example.com" = "hello@mysite.com"
"+1-555-0000" = "+1-555-1234"

# Social media
"facebook.com/example" = "facebook.com/mycompany"
"twitter.com/example" = "twitter.com/mycompany"
```

**Important Notes**:
- Replacements are applied **after** PHP execution and link conversion
- Replacements are **case-sensitive** exact string matches
- Order doesn't matter (all replacements are independent)
- Use double quotes for TOML strings
- Escape backslashes in Windows paths: `"C:\\path"`

#### Requirements (Optional)

**The TOML file is optional**. If you don't create it, the script uses default configurations.

If you want to use `PHPStaticRender.toml`:

**Python 3.11+**: TOML support is built-in (no installation needed)

**Python 3.6-3.10**: Install the TOML library:
```bash
pip install toml
```

If the TOML library is not available and a TOML file exists, the script will display an info message and use default configurations from the script.

---

### Configuration via Script Constants

All configurations can also be edited directly at the top of the `phpstaticrender.py` file within the clearly marked section.

### `CONFIG_OUTPUT_FOLDER`
**Default**: `'_PHPStaticRender'`

Folder where the site will be generated. It is cleaned on each execution. Add to `.gitignore`.

```python
CONFIG_OUTPUT_FOLDER = 'dist'    # Common alternative
CONFIG_OUTPUT_FOLDER = 'build'   # Also common
```

---

### `CONFIG_IGNORE_PREFIX`
**Default**: `'__'`

Files with this prefix are ignored (e.g., `__header.php` is not processed). Useful for includes that should not generate their own HTML.

---

### `CONFIG_PHP_EXTENSION`
**Default**: `'.php'`

Extension of PHP files to process. In the current script behavior, the check **is not** case-sensitive.

---

### `CONFIG_IGNORE_SYSTEM`
Folders and files ignored during scanning (`.git`, `node_modules`, `vendor`, `.env`, etc.).

**Customize**:
```python
CONFIG_IGNORE_SYSTEM.add('uploads')  # Add folder
```

---

### `CONFIG_ENCODING`
**Default**: `'utf-8'`

Character encoding. Use `'cp1252'` if you have issues with accents on Windows.

---

### `CONFIG_MANUAL_PHP_PATH`
**Default**: `None`

Manual PHP path if detection fails.

```python
CONFIG_MANUAL_PHP_PATH = r'C:\xampp\php\php.exe'  # Windows
CONFIG_MANUAL_PHP_PATH = '/usr/local/bin/php'     # Linux/macOS
```

---

### `CONFIG_SAFE_MODE`
**Default**: `False`

When enabled, the PHP CLI is executed with safer flags that disable risky functions and remote URL inclusion.

```python
CONFIG_SAFE_MODE = True
```

## Technical Requirements

### Python
- **Version**: 3.6 or higher
- **Modules**: Only stdlib (no pip installations)
- **Verification**: `python --version`

### PHP
- **Version**: PHP 5.4+ (recommended 7.4+)
- **CLI required**: Executable for command line
- **Verification**: `php --version`

**Installation (summary)**:
- **Windows**: [XAMPP](https://www.apachefriends.org/) or [PHP Standalone](https://windows.php.net/download/)
- **Debian/Ubuntu**: `sudo apt install php-cli`
- **RHEL/CentOS/Fedora**: `sudo yum install php-cli` or `sudo dnf install php-cli`
- **macOS**: `brew install php`

**Includes**: Use paths relative to the project root:
```php
<?php
include 'includes/header.php';  // ✅ Correct
include '../includes/header.php';  // ❌ Avoid
?>
```

**Verify installation**:
```bash
php --version
```

---

### Operating System

#### Compatibility
| OS | Status | Notes |
|----|--------|-------|
| **Windows 10/11** | ✅ Tested | XAMPP detected automatically |
| **Windows 7/8** | ✅ Compatible | May need `CONFIG_ENCODING = 'cp1252'` |
| **Ubuntu 20.04+** | ✅ Tested | PHP via apt-get |
| **Debian 10+** | ✅ Compatible | PHP via apt |
| **macOS 10.15+** | ✅ Compatible | Homebrew recommended |
| **CentOS/RHEL** | ✅ Compatible | PHP via yum/dnf |

#### Required Permissions
- **Read**: Access to the project directory
- **Write**: Creation of the output folder
- **Execute**: Permission to run PHP and Python

**Linux/macOS**: If there is a permission error:
```bash
# Give execution permission to the script:
chmod +x phpstaticrender.py

# Execute:
python3 phpstaticrender.py
```

---

### Disk Space

#### Usage Estimate
- **Script**: ~10 KB
- **HTML Output**: Approximately 0.8x - 1.2x the size of the original project
- **Static Files**: Identical size (direct copies)

**Example**:
- PHP Project: 50 MB
- Generated static site: ~55 MB (HTML + copied assets)

## Troubleshooting and Common Issues

### Installation and Configuration Errors

#### ℹ️ Info: "TOML library not available"

**This is not an error** - the TOML file is optional. The script will work normally using default configurations.

If you want to use `PHPStaticRender.toml` for custom configurations:

**Solution 1**: Install TOML package (Python < 3.11):
```bash
pip install toml
```

**Solution 2**: Upgrade to Python 3.11+ (built-in TOML support)

**Solution 3**: Continue without TOML and edit `phpstaticrender.py` constants directly

---

#### ❌ Error: "PHP executable not found"

**Solutions**:
1. Check: `php --version`
2. Configure: `CONFIG_MANUAL_PHP_PATH = r'C:\xampp\php\php.exe'`
3. Windows: Add PHP to PATH in Environment Variables

---

#### ❌ PHP files are not processed

**Causes**: Incorrect extension (case-sensitive) or `__` prefix
**Solution**: Check `CONFIG_PHP_EXTENSION` and rename if necessary

---

#### ❌ PHP includes don't work

**Solution**: Use paths relative to the project root:
```php
<?php
include 'includes/header.php';  // ✅ Correct
// include '../includes/header.php';  // ❌ Avoid
?>
```

---

### Encoding Issues

#### ❌ Broken characters (�, ã¡, etc.)

**Solution**: Change `CONFIG_ENCODING = 'cp1252'` (Windows) or `'utf-8'` (modern)

Add in PHP:
```php
<?php
header('Content-Type: text/html; charset=UTF-8');
?>
```

---

### Permission Issues

**Windows**: Run as Administrator  
**Linux/macOS**: `chmod -R 755 /path/to/project`

---

### PHP Execution Errors

#### ❌ Fatal Error in PHP
**Solution**: Test with `php -l file.php` and fix the code

#### ❌ Warning: Cannot modify header information
**Solution**: Use meta refresh or JavaScript instead of `header()`
```php
echo '<meta http-equiv="refresh" content="0;url=other.html">';
?>
```

---

### Performance Issues

**Slow?** Add folders to ignore:
```python
CONFIG_IGNORE_SYSTEM.add('uploads')
CONFIG_IGNORE_SYSTEM.add('cache')
```

**Large output?** Ignore development assets:
```python
CONFIG_IGNORE_SYSTEM.add('src')
CONFIG_IGNORE_SYSTEM.add('raw-assets')
```

---

### System-Specific Issues (Summary)

- **Windows**: if encoding error, use `CONFIG_ENCODING = 'cp1252'`.
- **Linux/macOS**: if running as script, ensure permission and use `python3 phpstaticrender.py`.
- **macOS**: if PHP not found, check Homebrew PATH.

---

### Quick Debug

- **Test file**: `php -f your-file.php`
- **Generate HTML directly**: `php your-file.php > test-output.html`

## Security

### Important
**Important**: The script **executes PHP as is**. If the PHP code contains:
- Backdoors or malware
- `exec()`, `system()`, `shell_exec()` commands
- Downloads from external URLs
- Writing malicious files

**These will be executed during generation.**

**Recommendations**:
1. ✅ Only process trusted projects
2. ✅ Review third-party code beforehand
3. ✅ Run in isolated environment (VM/Docker) if necessary
4. ✅ Always ignore credentials
```python
CONFIG_IGNORE_SYSTEM.update({
    '.env', 'config.php', '.key', '.pem'
})
```

5. ✅ Enable safe mode when possible
```python
CONFIG_SAFE_MODE = True
```

---

### Output Folder Safety

The output folder is validated before cleanup to ensure it is a subfolder of the project root.
This prevents accidental deletion of system or parent directories.

---

### Symbolic Links

Symbolic links (files and folders) are ignored by default to prevent traversing outside the project.

---

### Checklist

- [ ] Code from trusted source
- [ ] No hardcoded credentials
- [ ] `.env` in `.gitignore`
- [ ] Review generated HTML before deploy

---

## Additional Resources

### Related Documentation
- [README.md](README.md) - Quick start guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

### Technical References
- [Python subprocess](https://docs.python.org/3/library/subprocess.html) - Official documentation
- [PHP CLI](https://www.php.net/manual/en/features.commandline.php) - PHP manual
- [OWASP Secure Coding](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/) - Security practices

### Complementary Tools
- **HTML Validator**: [W3C Validator](https://validator.w3.org/)
- **Performance Testing**: [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- **SEO Checker**: [SEO Site Checkup](https://seositecheckup.com/)

---

## Contribution and Support

### How to Contribute
- **Issues**: Report bugs or suggestions on [GitHub Issues](https://github.com/gmasson/phpstaticrender/issues)
- **Pull Requests**: Follow guidelines in [CONTRIBUTING.md](CONTRIBUTING.md)
- **Discussions**: Use GitHub Discussions for general questions

### Report Bugs
Include in issues:
1. Python and PHP version (`--version`)
2. Operating system
3. Executed command
4. Complete error output
5. Snippet of problematic PHP code (if relevant)

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

**Summary**:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed

---

**Last Update**: January 2026 | **Version**: 0.9
