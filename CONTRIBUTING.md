# Contributing Guide

Thank you for your interest in contributing!

## How to Contribute

### Report Bugs

Open an [issue](https://github.com/gmasson/phpstaticrender/issues/new?labels=bug) including:
- Clear description of the problem
- Steps to reproduce
- Environment (OS, Python/PHP version)
- Error logs

### Suggest Features

Open an [issue](https://github.com/gmasson/phpstaticrender/issues/new?labels=enhancement) describing:
- Problem it solves
- Real use case
- Implementation example

### Submit Pull Request

1. Fork the repository
2. Clone: `git clone https://github.com/YOUR_USER/phpstaticrender.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Implement and test your changes
5. Commit: `git commit -m 'feat: add new feature'`
6. Push: `git push origin feature/my-feature`
7. Open the Pull Request

**Commit standard** ([Conventional Commits](https://www.conventionalcommits.org/)):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring

## Code Guidelines

**Python Standards (PEP 8)**:
- Indentation: 4 spaces
- Max line length: 100 characters
- Docstrings in public functions
- Type hints when possible
- Naming: `snake_case` for functions/variables

**Best practices**:
- Clear and self-explanatory code
- Error handling with informative messages
- Python 3.6+ compatibility
- Zero external dependencies
- Validate user inputs

## Development

**Setup**:
```bash
git clone https://github.com/gmasson/phpstaticrender.git
cd phpstaticrender
python --version  # 3.6+
php --version     # 5.4+
```

**Test**:
```bash
mkdir test-project && cd test-project
echo "<?php echo 'Test'; ?>" > index.php
cp ../phpstaticrender.py .
python phpstaticrender.py
```

**Validate**:
```bash
python -m py_compile phpstaticrender.py
```

## License

By contributing to this project, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

**Thank you for contributing!** 🎉
