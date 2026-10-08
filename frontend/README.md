# ITAMS frontend

This React/Vite client presents the IT Asset Management System. Its route entry
point is `src/App.jsx`; Asset details, temporary Checkout/Check-in, ongoing
Assign/Take Back, approval-gated Transfer, Service Records, reports, and
administration live under `src/pages/`. Route controls use permission codes;
the Django API enforces the corresponding authorization.

Read the repository's [`CONTEXT.md`](../CONTEXT.md) for domain terms and
[`specs/README.md`](../specs/README.md) for durable feature specifications.
Feature 014's accepted custody behavior is recorded in
[`specs/014-asset-assignments/`](../specs/014-asset-assignments/).

From this directory, with the dependencies in `package-lock.json` installed:

```powershell
npm test
npm run lint
npm run build
```

`npm test` runs Vitest with jsdom and React Testing Library. The React Compiler
plugin is configured for the client build and excluded from test transforms in
`vite.config.js`.
