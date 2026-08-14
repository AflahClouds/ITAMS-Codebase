/**
 * A duplicate-id sweep over the real form pages.
 *
 * The shared form controls each carried an id copied from the MUI documentation, so a
 * page emitted the same id once per field. This is the check that measured it — Asset
 * Create had 41 ids of which only 29 were distinct — and it stays as a test so the next
 * component built from a documentation snippet is caught here rather than by someone
 * using a screen reader.
 */
import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('../api/client', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: [] }) },
}));

vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({ id: '1' }),
  Link: ({ children, ...rest }) => <a {...rest}>{children}</a>,
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
    const { container } = render(<Page />);
    // The pages load their master data on mount; let those resolve so the rendered
    // tree is the one an operator would see.
    await new Promise((resolve) => setTimeout(resolve, 50));

    const ids = Array.from(container.querySelectorAll('[id]'))
      .map((node) => node.id)
      .filter(Boolean);
    const duplicates = [...new Set(ids.filter((v, i) => ids.indexOf(v) !== i))];

    expect(duplicates).toEqual([]);
    expect(ids.length).toBeGreaterThan(0);
  });
});
