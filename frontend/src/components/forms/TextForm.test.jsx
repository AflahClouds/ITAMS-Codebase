/**
 * Tests for the shared text and description controls' label association.
 *
 * Both carried an id copied from the MUI documentation — "standard-basic" and
 * "outlined-multiline-static" — on every instance. A form with several text fields
 * therefore emitted the same id a dozen times, so the label pointed at whichever
 * control the browser found first: a screen reader announced the wrong field, and no
 * label-based query could address one field rather than another.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import DescriptionForm from './DescriptionForm';
import TextForm from './TextForm';

// MUI's TextField emits two id-bearing nodes per field — the input and its label —
// so the count is twice the number of controls. Uniqueness is the property that
// matters, and the one that was broken.
const uniqueIds = (root) => {
  const ids = Array.from(root.querySelectorAll('[id]')).map((n) => n.id).filter(Boolean);
  return { ids, distinct: new Set(ids).size };
};

describe('TextForm label association', () => {
  it('gives every instance on a form a distinct id', () => {
    const { container } = render(
      <>
        <TextForm label="Invoice Number" name="invoice_number" value=""
                  onChange={() => {}} />
        <TextForm label="PO Number" name="po_number" value="" onChange={() => {}} />
        <TextForm label="Purchase Cost" name="purchase_cost" value=""
                  onChange={() => {}} />
      </>,
    );

    const { ids, distinct } = uniqueIds(container);
    expect(distinct).toBe(ids.length);
    expect(screen.getAllByRole('textbox')).toHaveLength(3);
  });

  it('points each label at its own control', () => {
    render(
      <>
        <TextForm label="Invoice Number" name="invoice_number" value=""
                  onChange={() => {}} />
        <TextForm label="PO Number" name="po_number" value="" onChange={() => {}} />
      </>,
    );

    const invoice = screen.getByLabelText('Invoice Number');
    const po = screen.getByLabelText('PO Number');

    expect(invoice).not.toBe(po);
    expect(invoice.id).not.toBe(po.id);
  });

  it('types into the field the label names, not a namesake', async () => {
    // The behavioural consequence of the defect: with a shared id, addressing a field
    // by its label could reach a different one.
    const onChange = vi.fn();
    render(
      <>
        <TextForm label="Invoice Number" name="invoice_number" value=""
                  onChange={onChange} />
        <TextForm label="PO Number" name="po_number" value="" onChange={onChange} />
      </>,
    );

    await userEvent.type(screen.getByLabelText('PO Number'), 'X');

    expect(onChange).toHaveBeenCalled();
    expect(onChange.mock.calls[0][0].target.name).toBe('po_number');
  });

  it('stays unique without a name', () => {
    const { container } = render(
      <>
        <TextForm label="First" value="" onChange={() => {}} />
        <TextForm label="Second" value="" onChange={() => {}} />
      </>,
    );

    const { ids, distinct } = uniqueIds(container);
    expect(distinct).toBe(ids.length);
  });
});

describe('DescriptionForm label association', () => {
  it('gives every instance a distinct id', () => {
    const { container } = render(
      <>
        <DescriptionForm label="Notes" name="notes" rows={3} value=""
                         onChange={() => {}} />
        <DescriptionForm label="Remarks" name="remarks" rows={3} value=""
                         onChange={() => {}} />
      </>,
    );

    const { ids, distinct } = uniqueIds(container);
    expect(distinct).toBe(ids.length);
    expect(screen.getAllByRole('textbox')).toHaveLength(2);
  });

  it('does not collide with a TextForm on the same page', () => {
    // The original ids were different strings, so these two never clashed with each
    // other — but each clashed with its own kind, and both are fixed the same way.
    const { container } = render(
      <>
        <TextForm label="Invoice Number" name="invoice_number" value=""
                  onChange={() => {}} />
        <DescriptionForm label="Notes" name="notes" rows={3} value=""
                         onChange={() => {}} />
      </>,
    );

    const { ids, distinct } = uniqueIds(container);
    expect(distinct).toBe(ids.length);
    expect(screen.getByLabelText('Invoice Number')).toBeInTheDocument();
    expect(screen.getByLabelText('Notes')).toBeInTheDocument();
  });
});
