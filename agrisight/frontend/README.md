# AgriSight Frontend — React version note

This small file explains why the frontend is pinned to React 18.x and how to update/install frontend dependencies.

Why pin to React 18.x
- The project documentation and several UI libraries used in this repo were tested against React 18.
- Pinning to React 18 reduces the risk of runtime incompatibilities in `react-leaflet`, Radix UI integrations, and other ecosystem packages that may not yet be fully compatible with React 19.

What changed
- `package.json` now pins `react` and `react-dom` to `^18.2.0`.
- Dev dependencies `@types/react` and `@types/react-dom` were updated to `^18.2.0` to match typings.

How to update dependencies locally (using pnpm)

Open a terminal at `agrisight/frontend` and run:

```powershell
pnpm install
pnpm dev
```

Notes
- If you intentionally want React 19, please run the app and tests in a safe environment and update packages that require changes; I recommended keeping 18 for stability unless you have a specific need to upgrade.
- After `pnpm install`, verify the app by visiting the Vite dev server (default port 5173) or by running the Docker Compose dev stack as documented in the repo.

If you'd like, I can prepare a follow-up PR that updates other dependent packages (and run a smoke test) to validate React 19 compatibility instead of pinning to 18.
