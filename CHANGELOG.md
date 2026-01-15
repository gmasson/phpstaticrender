# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-01-15

### Added
- Recursive processing of PHP directories
- Execution of PHP files via CLI with stdout capture
- Copying of static files preserving metadata
- Configurable ignore system (prefixes and folders)
- Automatic PHP detection (Windows/Linux/macOS)
- XAMPP support on Windows
- Optional TOML configuration file support (PHPStaticRender.toml)
- Automatic conversion of internal .php links to .html in generated output
- Text replacement feature via TOML [replace] section
- Safe mode for PHP execution (disables risky functions)
- Support for Python 3.11+ built-in tomllib
- Backward compatibility with toml package for Python 3.6-3.10
- Enhanced documentation with TOML examples
- Validation to prevent accidental deletion of system directories
- Robust error handling with detailed feedback
- Processing statistics
- Complete documentation in Portuguese
- Support for UTF-8 and cp1252 encoding

### Features
- Zero external dependencies (only Python stdlib)
- Compatible with Python 3.6+
- Compatible with PHP 5.4+
- Cross-platform (Windows, Linux, macOS)
- Configuration via TOML file or script constants
- MIT License

### Fixed
- UTF-8 encoding issues on Windows console
- Symbolic link traversal security issue

[0.9.0]: https://github.com/gmasson/phpstaticrender/releases/tag/v0.9.0
