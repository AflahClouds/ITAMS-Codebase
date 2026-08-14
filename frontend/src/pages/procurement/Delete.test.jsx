/**
 * Conformance tests for the Procurement removal surface.
 *
 * B6 FR-011 forbids destroying a purchase record; removal archives it. A screen that
 * still says "Delete" would describe an operation the system no longer performs, and
 * this is the screen where an operator decides whether to go ahead.
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({
  default: { get: vi.fn(), delete: vi.fn() },
}));

const navigate = vi.fn();
vi.mock('react-router', () => ({
  useNavigate: () => navigate,
  useParams: () => ({ id: '7' }),
}));

import AxiosInstance from '../../api/client';
import ProcurementDelete from './Delete';

const RECORD = {
  id: 7,
  invoice_number: 'INV-2026-014',
  vendor_details: { name: 'Acme Supplies' },
  mode_of_purchase_details: { purchase_mode: 'Purchase' },
  assets: [{ id: 1, asset_id: 'AST-001' }, { id: 2, asset_id: 'AST-002' }],
};

describe('Procurement removal', () => {
  beforeEach(() => {
    AxiosInstance.get.mockReset().mockResolvedValue({ data: RECORD });
    AxiosInstance.delete.mockReset().mockResolvedValue({ data: {} });
  });

  it('describes the operation as archiving rather than deleting', async () => {
    // Covers: B6 FR-011.
    render(<ProcurementDelete />);

    expect(await screen.findByText(/archive this procurement record/i))
      .toBeInTheDocument();
    expect(screen.getByRole('button', { name: /archive/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^delete$/i })).not.toBeInTheDocument();
  });

  it('explains why the record is kept and that the assets stay linked', async () => {
    // Covers: B6 FR-011.
    // The reason matters at the point of decision: an operator who thinks the record
    // is gone will record the purchase again.
    render(<ProcurementDelete />);

    expect(await screen.findByText(/archived rather than deleted/i)).toBeInTheDocument();
    expect(screen.getByText(/remain linked/i)).toBeInTheDocument();
  });

  it('still identifies the purchase being archived', async () => {
    // Covers: B6 FR-004, B6 FR-011.
    render(<ProcurementDelete />);

    expect(await screen.findByText('INV-2026-014')).toBeInTheDocument();
    expect(screen.getByText('Acme Supplies')).toBeInTheDocument();
    expect(screen.getByText('AST-001, AST-002')).toBeInTheDocument();
  });

  it('confirms the record was archived, not destroyed', async () => {
    // Covers: B6 FR-011.
    render(<ProcurementDelete />);
    await screen.findByText('INV-2026-014');

    await userEvent.click(screen.getByRole('button', { name: /archive/i }));

    await waitFor(() =>
      expect(AxiosInstance.delete).toHaveBeenCalledWith('/procurement/7/'));
    // Matched on the confirmation sentence specifically: the standing explanation on
    // the page also contains the word "archived".
    expect(await screen.findByText(/no longer in the working list/i))
      .toBeInTheDocument();
  });
});
