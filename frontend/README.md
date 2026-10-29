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
The master-data page selects and displays a Model's Brand. The backend enforces
normalized catalog identities, accounts for direct Audit Trail access and every
administrative Setting mutation, and preserves literal text in PDF/Excel exports.
The accepted scope and regression evidence are in
[`specs/015-standards-remediation/`](../specs/015-standards-remediation/).

New Assets start **In Storage** and become **Available** when valid Procurement
is added. Asset deletion explains that any Procurement link must be removed
first. Procurement editing supports reasoned detachment while other Assets
remain; its last eligible Asset is released through the separate confirmed
**Permanently delete** action. That action removes the purchase and its owned
history/invoices, retains the Asset In Storage, and opens its refreshed detail
page. Ordinary **Archive** remains separate. Existing permissions and custody
history safeguards apply. Scope and validation evidence are in
[`specs/016-asset-procurement-lifecycle/`](../specs/016-asset-procurement-lifecycle/).

From this directory, with the dependencies in `package-lock.json` installed:

```powershell
npm test
npm run lint
npm run build
```

For a serial full test run, use
`npm test -- --maxWorkers=1 --no-file-parallelism --testTimeout=60000`.

`npm test` runs Vitest with jsdom and React Testing Library. The React Compiler
plugin is configured for the client build and excluded from test transforms in
`vite.config.js`.
