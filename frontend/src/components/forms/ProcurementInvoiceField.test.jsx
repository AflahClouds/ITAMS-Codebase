import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import ProcurementInvoiceField from './ProcurementInvoiceField';

describe('ProcurementInvoiceField', () => {
  it('presents an optional invoice selector with the accepted policy', () => {
    // Covers: CHG-B6-01 FR-001, FR-002, FR-011.
    render(<ProcurementInvoiceField file={null} onChange={() => {}} />);

    expect(screen.getByText(/purchase invoice \(optional\)/i)).toBeInTheDocument();
    expect(screen.getByText(/maximum 25 mb/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/choose purchase invoice/i)).not.toBeRequired();
    expect(screen.getByLabelText(/choose purchase invoice/i)).toHaveAttribute(
      'accept', '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.webp');
  });

  it('reports the selected filename through the public change callback', () => {
    // Covers: CHG-B6-01 FR-001, FR-003.
    const onChange = vi.fn();
    render(<ProcurementInvoiceField file={null} onChange={onChange} />);
    const invoice = new File(['invoice'], 'invoice.pdf', { type: 'application/pdf' });

    fireEvent.change(screen.getByLabelText(/choose purchase invoice/i), {
      target: { files: [invoice] },
    });

    expect(onChange).toHaveBeenCalledWith(invoice);
  });

  it('describes a later upload as a replacement and shows the current version', () => {
    // Covers: CHG-B6-01 FR-004, FR-005, FR-010.
    render(<ProcurementInvoiceField
      file={null}
      onChange={() => {}}
      currentInvoice={{ file_name: 'original.pdf', version: 3 }}
    />);

    expect(screen.getByText(/original\.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/version 3/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /choose replacement/i })).toBeInTheDocument();
    expect(screen.getByText(/leave empty to keep the current invoice/i)).toBeInTheDocument();
  });
});
