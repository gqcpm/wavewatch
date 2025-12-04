# 🤝 Contributing to WaveWatch

We welcome contributions! To keep the process smooth and code quality high, please follow this guide. Our workflow is designed to be minimal using automated tools.

## 🚀 Getting Started

1. **Fork** the repository.

2. **Clone** your fork:

   ```bash
   git clone https://github.com/your-username/wavewatch.git
   ```

3. **Install dependencies:**

   ```bash
   # Install Node.js dependencies
   npm install

   # Install Python dependencies
   pip install -r requirements.txt

   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Create a new branch** using the format `feature/my-new-feature` or `fix/critical-bug`.

## ✅ Contribution Requirements Checklist

Before pushing your branch or submitting a Pull Request (PR), **you must run and pass the following automated checks locally.**

### 1. Code Formatting

Ensure all code style is uniform. This command automatically fixes most formatting issues.

```bash
# Runs Prettier for JS/TS and Black for Python
npm run format
```

### 2. Code Quality (Linting & Testing)

The following script runs all linters and tests. It must report zero errors to proceed.

```bash
npm run check-all
```

This command will:
- Run ESLint on all JavaScript/JSX files
- Run Flake8 on all Python files
- Run unit tests
- Verify all checks pass

### Individual Commands

If you need to run checks individually:

```bash
# JavaScript/TypeScript linting
npm run lint:js

# JavaScript/TypeScript formatting
npm run format:js

# Python linting
npm run lint:py

# Python formatting
npm run format:py

# Run tests only
npm run test
```

## 📝 Pull Request Process

1. Ensure all automated checks pass (`npm run check-all`)
2. Update documentation if you've changed functionality
3. Write clear commit messages
4. Reference any related issues in your PR description
5. Wait for code review and address any feedback

## 🎯 Code Style Guidelines

- **JavaScript/React**: Follow ESLint and Prettier rules (automatically enforced)
- **Python**: Follow Black formatting and Flake8 linting rules (automatically enforced)
- Write meaningful commit messages
- Keep functions small and focused
- Add comments for complex logic

## 🐛 Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (OS, Node.js version, Python version)

## 💡 Suggesting Features

Feature suggestions are welcome! Please open an issue describing:
- The feature and its use case
- How it might be implemented (if you have ideas)
- Any potential impacts on existing functionality

Thank you for contributing to WaveWatch! 🌊

