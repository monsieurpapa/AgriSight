# Contributing to AgriSight

First off, thank you for considering contributing to AgriSight! It's people like you who make this platform a valuable tool for agriculture and humanitarian aid.

## 🌈 Code of Conduct
Please be respectful and professional in all interactions within the AgriSight community.

## 🛠️ Local Development Setup

### Backend (Django)
1. Navigate to `agrisight/backend`.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Set up `.env` from `.env.example`.
5. Run migrations: `python manage.py migrate`.
6. Start dev server: `python manage.py runserver`.

### Frontend (React)
1. Navigate to `agrisight/frontend`.
2. Install dependencies: `pnpm install`.
3. Start dev server: `pnpm dev`.

## 🌿 Branching Strategy
- `main`: Production-ready code.
- `develop`: Integration branch for features.
- `feature/*`: New features and enhancements.
- `bugfix/*`: Critical bug fixes.

## 📋 Coding Standards

### Python (Backend)
- Follow **PEP 8** style guidelines.
- Use **Flake8** for linting.
- Every new feature must include a corresponding test case in `tests.py`.

### JavaScript/React (Frontend)
- Utilize **ESLint** and **Prettier**.
- Components should be functional and follow React 19 best practices.
- Use **Radix UI** primitives for accessible components.

## 🚀 Pull Request Process

1. Fork the repo and create your branch from `develop`.
2. If you've added code that should be tested, add tests.
3. Ensure the test suite passes (`pytest` and `vitest`).
4. Update the documentation if you've changed functionality.
5. Issue a Pull Request against the `develop` branch.
6. A maintainer will review your PR and provide feedback.

## 📝 Commit Messages
- Use the imperative mood ("Add feature" not "Added feature").
- Keep the subject line short (under 50 chars).
- Reference issues/tickets at the end of the message.

---

AgriSight Maintainers
