/**
 * Tests for the shared select control's label association.
 *
 * Every instance used to carry the ids copied from the MUI documentation, so a page
 * with two selects emitted duplicate ids. The label then pointed at whichever control
 * the browser found first: a screen reader announced the wrong field, and a
 * label-based test query matched wrappers rather than controls — which is how this was
 * found.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import SelectForm from './SelectForm';

const LOCATIONS = [
  { id: 10, name: 'Head Office' },
  { id: 11, name: 'Warehouse' },
];

const DEPARTMENTS = [
  { id: 20, name: 'Finance' },
  { id: 21, name: 'IT' },
];

function renderTwo() {
  return render(
    <>
      <SelectForm label="Location" options={LOCATIONS} labelKey="name"
                  name="location" value="" onChange={() => {}} />
      <SelectForm label="Department" options={DEPARTMENTS} labelKey="name"
                  name="department" value="" onChange={() => {}} />
    </>,
  );
}

describe('SelectForm label association', () => {
  it('gives every instance on a page a distinct id', () => {
    renderTwo();

    const ids = Array.from(document.querySelectorAll('[id]'))
      .map((node) => node.id)
      .filter(Boolean);

    expect(ids.length).toBeGreaterThan(0);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('points each label at its own control', () => {
    renderTwo();

    const location = screen.getByLabelText('Location');
    const department = screen.getByLabelText('Department');

    expect(location).not.toBe(department);
  });

  it('finds a single control per label rather than a wrapper and an input', () => {
    // The symptom that exposed the duplicate ids: a label query returned more than one
    // node, so a test could not address a specific field.
    renderTwo();

    expect(screen.getAllByLabelText('Location')).toHaveLength(1);
    expect(screen.getAllByLabelText('Department')).toHaveLength(1);
  });

  it('reports a choice against the control that was changed', async () => {
    const onChange = vi.fn();
    render(
      <SelectForm label="Location" options={LOCATIONS} labelKey="name"
                  name="location" value="" onChange={onChange} />,
    );

    await userEvent.click(screen.getByRole('combobox'));
    await userEvent.click(await screen.findByRole('option', { name: 'Warehouse' }));

    expect(onChange).toHaveBeenCalled();
    expect(onChange.mock.calls[0][0].target).toMatchObject({
      name: 'location', value: 11,
    });
  });

  it('still works without a name', () => {
    // `useId` carries uniqueness on its own, so an unnamed instance is not a duplicate.
    render(
      <>
        <SelectForm label="First" options={LOCATIONS} labelKey="name"
                    value="" onChange={() => {}} />
        <SelectForm label="Second" options={LOCATIONS} labelKey="name"
                    value="" onChange={() => {}} />
      </>,
    );

    const ids = Array.from(document.querySelectorAll('[id]')).map((n) => n.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
