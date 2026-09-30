# Frontend

React and TypeScript application for **Ma Collection**, built with Vite.

## Requirements

- Node.js 22.13 or newer for the installed Vitest and jsdom versions
- npm
- The backend API running at `http://localhost:8000` (see [the API README](../api/README.md))

## Install and run

From this directory:

```sh
npm ci
npm run dev
```

Vite serves the application at <http://localhost:5173>. The API base URL defaults to `http://localhost:8000`; set `VITE_API_BASE_URL` in `.env.local` to use a different address.

## Checks

```sh
npm test
npm run build
```

The source is organized into pages, reusable components, authentication and collection contexts, hooks, API services, and handwritten API types in `src/types/api.ts`.
