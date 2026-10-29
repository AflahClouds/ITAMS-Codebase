import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const state = vi.hoisted(() => ({ navigate: vi.fn(), permitted: true }));
vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() } }));
vi.mock('react-router', () => ({ useNavigate: () => state.navigate, useParams: () => ({ id: '7' }) }));
vi.mock('../../auth/useAuth', () => ({ useAuth: () => ({ can: () => state.permitted }) }));
import AxiosInstance from '../../api/client';
import ProcurementDelete from './Delete';

beforeEach(() => {
  state.permitted = true;
  state.navigate.mockReset();
  AxiosInstance.get.mockResolvedValue({ data: {
    id: 7, invoice_number: 'INV-7', assets: [{ id: 1, asset_id: 'ONLY' }],
  } });
  AxiosInstance.post.mockReset().mockResolvedValue({});
  AxiosInstance.delete.mockReset().mockResolvedValue({});
});

it('confirms permanent purchase invoice and history loss while retaining the Asset', async () => {
  render(<ProcurementDelete />);
  await userEvent.click(await screen.findByRole('button', { name: 'Permanently delete Procurement' }));
  expect(screen.getByText(/invoice versions and.*history.*permanently/i)).toBeInTheDocument();
  expect(screen.getByText(/Asset.*retained.*In Storage/i)).toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Confirm permanent deletion' }));
  await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalledWith('/procurement/7/permanent-delete/', {}));
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
  expect(state.navigate).toHaveBeenCalledWith('/asset/detail/1');
});

it('cancels without mutation and reports server failure without success navigation', async () => {
  AxiosInstance.post.mockRejectedValue({ response: { data: { detail: 'Asset custody changed. Reload.' } } });
  render(<ProcurementDelete />);
  await userEvent.click(await screen.findByRole('button', { name: 'Permanently delete Procurement' }));
  await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  await userEvent.click(screen.getByRole('button', { name: 'Permanently delete Procurement' }));
  await userEvent.click(screen.getByRole('button', { name: 'Confirm permanent deletion' }));
  expect(await screen.findByText('Asset custody changed. Reload.')).toBeInTheDocument();
  expect(state.navigate).not.toHaveBeenCalled();
});

it('shows the lifecycle rejection returned as a DRF validation list', async () => {
  const reason = 'Asset ONLY has protected lifecycle or custody state; resolve it before changing Procurement.';
  AxiosInstance.post.mockRejectedValue({ response: { data: [reason] } });
  render(<ProcurementDelete />);
  await userEvent.click(await screen.findByRole('button', { name: 'Permanently delete Procurement' }));
  await userEvent.click(screen.getByRole('button', { name: 'Confirm permanent deletion' }));
  expect(await screen.findByText(reason)).toBeInTheDocument();
  expect(state.navigate).not.toHaveBeenCalled();
});

it('offers ordinary archive but no permanent action without deletion permission', async () => {
  state.permitted = false;
  render(<ProcurementDelete />);
  await screen.findByText('INV-7');
  expect(screen.queryByRole('button', { name: 'Permanently delete Procurement' })).not.toBeInTheDocument();
});

it('does not offer permanent deletion for a multi-Asset purchase', async () => {
  AxiosInstance.get.mockResolvedValue({ data: {
    invoice_number: 'INV-7', assets: [{ id: 1, asset_id: 'ONE' }, { id: 2, asset_id: 'TWO' }],
  } });
  render(<ProcurementDelete />);
  await screen.findByText('INV-7');
  expect(screen.queryByRole('button', { name: 'Permanently delete Procurement' })).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Archive' })).toBeInTheDocument();
});

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

    expect(await screen.findByText(/Archive keeps the purchase/i)).toBeInTheDocument();
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
