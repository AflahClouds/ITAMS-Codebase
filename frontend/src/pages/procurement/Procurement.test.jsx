/**
 * Conformance tests for the Procurement list's per-row action controls.
 *
 * B6 ALR-008 requires every frontend B6 action control to use the same permission as
 * the backend action. Finding OBS-AS-014 recorded this list as **Open**: it rendered
 * edit and delete on every row regardless of what the reader could do.
 *
 * The backend was never the hole — it refuses the action either way. The defect is that
 * an operator learns they cannot do something by clicking and being refused, and that a
 * screen offering an action implies permission the reader does not have. Hiding the
 * control is presentation; the backend check remains the decision.
 */
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn() } }));
vi.mock('../../api/downloadProtectedFile', () => ({
  downloadProtectedFile: vi.fn(),
}));
vi.mock('react-router', () => ({
  Link: ({ children, ...rest }) => <a {...rest}>{children}</a>,
}));

const permissions = { current: [] };
vi.mock('../../auth/useAuth', () => ({
  useAuth: () => ({ can: (code) => permissions.current.includes(code) }),
}));

import AxiosInstance from '../../api/client';
import { downloadProtectedFile } from '../../api/downloadProtectedFile';
import Procurement from './Procurement';

const ROW = {
  id: 7,
  assets: [{ id: 1, asset_id: 'AST-001' }],
  mode_of_purchase_details: { purchase_mode: 'Purchase' },
  vendor_details: { name: 'Acme Supplies' },
  purchase_date: '2026-01-01',
  invoice_number: 'INV-2026-014',
  po_number: 'PO-1',
};

async function renderWith(codes) {
  permissions.current = codes;
  render(<Procurement />);
  await screen.findByText('INV-2026-014');
}

describe('Procurement row actions', () => {
  beforeEach(() => {
    AxiosInstance.get.mockReset().mockResolvedValue({ data: [ROW] });
  });

  it('offers both controls to a reader holding both codes', async () => {
    // Covers: B6 ALR-008, B6 FR-016.
    await renderWith(['asset_view', 'asset_edit', 'asset_delete']);

    expect(screen.getByLabelText('Edit procurement')).toBeInTheDocument();
    expect(screen.getByLabelText('Archive procurement')).toBeInTheDocument();
  });

  it('offers no action control to a reader who may only look', async () => {
    // Covers: B6 ALR-008.
    await renderWith(['asset_view']);

    expect(screen.queryByLabelText('Edit procurement')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Archive procurement')).not.toBeInTheDocument();
  });

  it('offers edit but not archive when only the edit code is held', async () => {
    // Covers: B6 ALR-008.
    // The two controls map to different backend codes, so they have to be decided
    // separately rather than by one "can write anything" test.
    await renderWith(['asset_view', 'asset_edit']);

    expect(screen.getByLabelText('Edit procurement')).toBeInTheDocument();
    expect(screen.queryByLabelText('Archive procurement')).not.toBeInTheDocument();
  });

  it('offers archive but not edit when only the delete code is held', async () => {
    // Covers: B6 ALR-008.
    await renderWith(['asset_view', 'asset_delete']);

    expect(screen.queryByLabelText('Edit procurement')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Archive procurement')).toBeInTheDocument();
  });

  it('still shows the purchase itself to a reader who may only look', async () => {
    // Covers: B6 FR-015, B6 ALR-008.
    // Hiding the controls must not hide the data: `asset_view` reads B6 records.
    await renderWith(['asset_view']);

    expect(screen.getByText('Acme Supplies')).toBeInTheDocument();
    expect(screen.getByText('AST-001')).toBeInTheDocument();
  });

  it('names archive and explicit singleton permanent deletion separately', async () => {
    await renderWith(['asset_view', 'asset_delete']);

    await waitFor(() => expect(screen.getByLabelText('Permanently delete procurement')).toBeInTheDocument());
  });

  it('lets a read-only operator download the protected current invoice', async () => {
    AxiosInstance.get.mockResolvedValue({ data: [{
      ...ROW,
      current_invoice: {
        file_name: 'purchase.pdf', version: 1,
        download_url: '/procurement/7/invoice/',
      },
    }] });
    await renderWith(['asset_view']);

    fireEvent.click(screen.getByLabelText('Download purchase invoice'));
    expect(downloadProtectedFile).toHaveBeenCalledWith(
      '/procurement/7/invoice/', 'purchase.pdf');
  });
});
