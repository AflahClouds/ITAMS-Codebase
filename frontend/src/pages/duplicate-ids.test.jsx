/**
 * A duplicate-id sweep over the real form pages.
 *
 * The shared form controls each carried an id copied from the MUI documentation, so a
 * page emitted the same id once per field. This is the check that measured it — Asset
 * Create had 41 ids of which only 29 were distinct — and it stays as a test so the next
 * component built from a documentation snippet is caught here rather than by someone
 * using a screen reader.
 */
import { act, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('../api/client', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: [] }) },
}));

vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/transfer/create' }),
  useParams: () => ({ id: '1' }),
  Link: ({ children, ...rest }) => <a {...rest}>{children}</a>,
}));

vi.mock('../auth/useAuth', () => ({
  useAuth: () => ({ can: () => true }),
}));

import AssetCreate from './asset/Create';
import CheckoutCreate from './checkout/Create';
import ProcurementCreate from './procurement/Create';
import ServiceCreate from './service/Create';
import TransferCreate from './transfer/Create';
import UserCreate from './user/Create';

const PAGES = [
  ['Asset create', AssetCreate],
  ['Procurement create', ProcurementCreate],
  ['User create', UserCreate],
  ['Checkout create', CheckoutCreate],
  ['Service create', ServiceCreate],
  ['Transfer create', TransferCreate],
];

describe('form pages emit no duplicate element ids', () => {
  it.each(PAGES)('%s', async (_name, Page) => {
    // These pages fetch their master data on mount, so rendering leaves state updates
    // in flight. An async `act` flushes them, which both settles the tree into the one
    // an operator would see and keeps React from warning that updates escaped it — a
    // bare timeout waits the same wall-clock time but lets the updates land outside.
    let container;
    await act(async () => {
      ({ container } = render(<Page />));
    });

    const ids = Array.from(container.querySelectorAll('[id]'))
      .map((node) => node.id)
      .filter(Boolean);
    const duplicates = [...new Set(ids.filter((v, i) => ids.indexOf(v) !== i))];

    expect(duplicates).toEqual([]);
    expect(ids.length).toBeGreaterThan(0);
  });
});
