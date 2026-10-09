import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({
  default: { get: vi.fn(), put: vi.fn() },
}));
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(), useParams: () => ({ id: '7' }),
}));
vi.mock('../../components/forms/TextForm', () => ({
  default: ({ label, name, value, onChange }) =>
    <input aria-label={label} name={name} value={value || ''} onChange={onChange} />,
}));
vi.mock('../../components/forms/SelectForm', () => ({
  default: ({ label, name, value, onChange }) =>
    <input aria-label={label} name={name} value={value || ''} onChange={onChange} />,
}));
vi.mock('../../components/forms/MultiSelectForm', () => ({
  default: () => <div>Linked assets</div>,
}));
vi.mock('../../components/forms/DateForm', () => ({ default: () => null }));
vi.mock('../../components/forms/ArrivalsForm', () => ({
  default: ({ onAttestChange }) =>
    <button type="button" onClick={() => onAttestChange(true)}>Attest arrivals</button>,
}));

import AxiosInstance from '../../api/client';
import ProcurementEdit from './Edit';

const PROCUREMENT = {
  id: 7,
  assets: [{ id: 1, asset_id: 'A', has_procurement: true }],
  asset_ids: [1],
  mode_of_purchase: 3,
  vendor: 4,
  purchase_date: '2026-01-01',
  invoice_date: '2026-01-02',
  invoice_number: 'INV-7',
  po_number: 'PO-7',
  current_invoice: { file_name: 'existing.pdf', version: 2 },
};

describe('Procurement edit invoice replacement', () => {
  beforeEach(() => {
    AxiosInstance.get.mockImplementation((url) => Promise.resolve({
      data: url === '/procurement/7/' ? PROCUREMENT
        : url === '/asset/' ? PROCUREMENT.assets : [],
    }));
    AxiosInstance.put.mockResolvedValue({ data: PROCUREMENT });
  });

  it('shows the current invoice and preserves it when no replacement is selected', async () => {
    render(<ProcurementEdit />);
    expect(await screen.findByText(/existing\.pdf/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    fireEvent.click(screen.getByRole('button', { name: 'Update Procurement' }));

    await waitFor(() => expect(AxiosInstance.put).toHaveBeenCalled());
    const [, form] = AxiosInstance.put.mock.calls[0];
    expect(form.has('invoice_file')).toBe(false);
  });

  it('includes a selected replacement in the multipart update', async () => {
    render(<ProcurementEdit />);
    await screen.findByText(/existing\.pdf/);
    const replacement = new File(['new'], 'replacement.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/choose purchase invoice/i),
      { target: { files: [replacement] } });
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    fireEvent.click(screen.getByRole('button', { name: 'Update Procurement' }));

    await waitFor(() => expect(AxiosInstance.put).toHaveBeenCalled());
    expect(AxiosInstance.put.mock.calls[0][1].get('invoice_file')).toBe(replacement);
  });

  it('shows an actionable replacement upload error', async () => {
    AxiosInstance.put.mockRejectedValue({
      response: { data: { invoice_file: ['Purchase invoices must be 25 MB or smaller.'] } },
    });
    render(<ProcurementEdit />);
    await screen.findByText(/existing\.pdf/);
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    fireEvent.click(screen.getByRole('button', { name: 'Update Procurement' }));

    expect(await screen.findByText(/25 MB or smaller/)).toBeInTheDocument();
  });
});
