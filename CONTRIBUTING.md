# Contributing to AgriResolve Application Workspace

Thank you for your interest in contributing to **AgriResolve**! This project powers agricultural trade protection and autonomous dispute resolution on the Stellar network.

## Getting Started

1. **Fork the repository** on GitHub: `https://github.com/AgriResolve/AgriResolve-app`
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/<your-username>/AgriResolve-app.git
   cd AgriResolve-app
   ```
3. **Install dependencies**:
   ```bash
   pnpm install
   ```

## Development Workflow

- **SDK Package** (`packages/sdk`):
  ```bash
  pnpm --filter @agriresolve/sdk build
  pnpm --filter @agriresolve/sdk test
  ```
- **Web Application** (`apps/web`):
  ```bash
  pnpm --filter agriresolve-web dev
  pnpm --filter agriresolve-web build
  ```
- **Indexer & AI Oracle** (`indexer`):
  ```bash
  pnpm --filter @agriresolve/indexer dev
  pnpm --filter @agriresolve/indexer test
  ```

## Design & UI/UX Guidelines

When contributing to `apps/web`:
- Do NOT use purple, pink, or blue gradients. Use flat solid fills.
- Do NOT use glassmorphism (`backdrop-blur`).
- Use crisp 1px solid borders (`border-[#D1D9D1]` or `border-stone-200`) on white cards.
- Keep landing page copy free of blockchain/crypto jargon.

## Commit Message Conventions

We adhere to Conventional Commits:
- `feat(scope): ...`
- `fix(scope): ...`
- `test(scope): ...`
- `docs(scope): ...`
- `chore(scope): ...`

## Pull Request Guidelines

1. Ensure all tests and typechecks pass:
   ```bash
   pnpm build
   pnpm test
   pnpm typecheck
   ```
2. Link the PR to an existing issue from [our open issues](https://github.com/AgriResolve/agriresolve-app/issues).
3. Ensure single-responsibility commits without bundling unrelated packages.
