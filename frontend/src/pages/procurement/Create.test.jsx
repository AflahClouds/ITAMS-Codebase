import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));
vi.mock('react-router', () => ({ useNavigate: () => vi.fn() }));
vi.mock('../../components/forms/TextForm', () => ({
  default: ({ label, name, value, onChange }) =>
    <input aria-label={label} name={name} value={value} onChange={onChange} />,
}));
vi.mock('../../components/forms/SelectForm', () => ({
  default: ({ label, name, value, onChange }) =>
    <input aria-label={label} name={name} value={value} onChange={onChange} />,
}));
vi.mock('../../components/forms/MultiSelectForm', () => ({
  default: ({ name, onChange }) =>
    <button type="button" onClick={() => onChange({ target: { name, value: [1, 2] } })}>
      Select assets
    </button>,
}));
vi.mock('../../components/forms/DateForm', () => ({ default: () => null }));
vi.mock('../../components/forms/ArrivalsForm', () => ({
  default: ({ selectedIds, onArrivalChange, onAttestChange }) =>
    <button type="button" onClick={() => {
      selectedIds.forEach((id) => {
        onArrivalChange(id, 'arrived_on', '2026-01-03');
        onArrivalChange(id, 'location', 9);
      });
      onAttestChange(true);
    }}>Attest arrivals</button>,
}));

import AxiosInstance from '../../api/client';
import ProcurementCreate from './Create';

describe('Procurement create invoice upload', () => {
  beforeEach(() => {
    AxiosInstance.get.mockImplementation((url) => Promise.resolve({
      data: url === '/asset/' ? [{ id: 1, asset_id: 'A' }, { id: 2, asset_id: 'B' }]
        : url === '/location/' ? [{ id: 9, name: 'Store' }]
          : [{ id: 3, name: 'Option', purchase_mode: 'Purchase' }],
    }));
    AxiosInstance.post.mockResolvedValue({ data: { id: 10 } });
  });

  it('keeps the invoice optional and sends it with the multi-asset multipart payload', async () => {
    render(<ProcurementCreate />);
    fireEvent.click(screen.getByRole('button', { name: 'Select assets' }));
    fireEvent.change(screen.getByLabelText('Purchase Mode'), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText('Vendor'), { target: { value: '4' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    const file = new File(['invoice'], 'purchase.pdf', { type: 'application/pdf' });
    fireEvent.change(screen.getByLabelText(/choose purchase invoice/i),
      { target: { files: [file] } });
    fireEvent.click(screen.getByRole('button', { name: 'Add Procurement' }));

    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalled());
    const [, form, config] = AxiosInstance.post.mock.calls[0];
    expect(form).toBeInstanceOf(FormData);
    expect(form.getAll('asset_ids')).toEqual(['1', '2']);
    expect(form.get('invoice_file')).toBe(file);
    expect(JSON.parse(form.get('arrivals'))).toHaveLength(2);
    expect(config.headers['Content-Type']).toBe('multipart/form-data');
  });

  it('renders the optional invoice selector without requiring a file', () => {
    AxiosInstance.get.mockReturnValue(new Promise(() => {}));
    render(<ProcurementCreate />);
    expect(screen.getByLabelText(/choose purchase invoice/i)).not.toBeRequired();
  });

  it('submits successfully without adding an invoice part', async () => {
    render(<ProcurementCreate />);
    fireEvent.click(screen.getByRole('button', { name: 'Select assets' }));
    fireEvent.change(screen.getByLabelText('Purchase Mode'), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText('Vendor'), { target: { value: '4' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    fireEvent.click(screen.getByRole('button', { name: 'Add Procurement' }));

    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalled());
    expect(AxiosInstance.post.mock.calls[0][1].has('invoice_file')).toBe(false);
  });

  it('shows the backend invoice validation message', async () => {
    AxiosInstance.post.mockRejectedValue({
      response: { data: { invoice_file: ['Unsupported document type.'] } },
    });
    render(<ProcurementCreate />);
    fireEvent.click(screen.getByRole('button', { name: 'Select assets' }));
    fireEvent.change(screen.getByLabelText('Purchase Mode'), { target: { value: '3' } });
    fireEvent.change(screen.getByLabelText('Vendor'), { target: { value: '4' } });
    fireEvent.click(screen.getByRole('button', { name: 'Attest arrivals' }));
    fireEvent.click(screen.getByRole('button', { name: 'Add Procurement' }));

    expect(await screen.findByText(/Unsupported document type/)).toBeInTheDocument();
  });
});
