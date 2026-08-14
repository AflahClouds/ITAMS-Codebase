/**
 * Conformance tests for the Procurement arrival-evidence form.
 *
 * B6 FR-009 (decision C7) resolved that arrival is enforced rather than assumed. The
 * backend refuses the save, but the requirement is about an operator attesting that the
 * goods are physically here — so the surface has to ask, per Asset, and has to make the
 * attestation a deliberate act rather than a hidden default.
 */
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import ArrivalsForm from './ArrivalsForm';

const ASSETS = [
  { id: 1, asset_id: 'AST-001', name: 'Latitude 5440' },
  { id: 2, asset_id: 'AST-002', name: '' },
  { id: 3, asset_id: 'AST-003', name: 'Unselected' },
];

const LOCATIONS = [
  { id: 10, name: 'Head Office' },
  { id: 11, name: 'Warehouse' },
];

function setup(props = {}) {
  const onArrivalChange = vi.fn();
  const onAttestChange = vi.fn();
  const view = render(
    <ArrivalsForm
      assets={ASSETS}
      selectedIds={[1, 2]}
      locations={LOCATIONS}
      arrivals={{}}
      attested={false}
      onArrivalChange={onArrivalChange}
      onAttestChange={onAttestChange}
      showAttestError={false}
      {...props}
    />,
  );
  return { ...view, onArrivalChange, onAttestChange };
}

describe('Procurement arrival evidence', () => {
  it('asks for an arrival row for every selected asset and no others', () => {
    // Covers: B6 FR-009.
    setup();

    expect(screen.getByText(/AST-001/)).toBeInTheDocument();
    expect(screen.getByText(/AST-002/)).toBeInTheDocument();
    expect(screen.queryByText(/AST-003/)).not.toBeInTheDocument();
  });

  it('offers a date and a location for each asset', () => {
    // Covers: B6 FR-009.
    // FR-009 names both: a date alone does not say where the goods went.
    setup();

    expect(screen.getAllByLabelText('Arrived at')).toHaveLength(2);

    // The date picker is asserted by role instead: MUI renders it as a segmented field
    // — a group of Year/Month/Day spinbuttons plus a hidden input — and both the group
    // and the input carry the label, so a label query counts two nodes per control.
    // That is MUI's own structure rather than an id defect in this codebase.
    expect(screen.getAllByRole('group')).toHaveLength(2);
    expect(screen.getAllByRole('spinbutton', { name: 'Day' })).toHaveLength(2);
  });

  it('starts with the attestation unticked', async () => {
    // Covers: B6 FR-009.
    // A pre-ticked box would make the attestation a formality rather than a statement
    // someone chose to make.
    setup();

    expect(screen.getByRole('checkbox')).not.toBeChecked();
  });

  it('reports the attestation when the operator ticks it', async () => {
    // Covers: B6 FR-009.
    const { onAttestChange } = setup();

    await userEvent.click(screen.getByRole('checkbox'));

    expect(onAttestChange).toHaveBeenCalledWith(true);
  });

  it('reports a location choice against the asset it belongs to', async () => {
    // Covers: B6 FR-009.
    const { onArrivalChange } = setup();

    await userEvent.click(screen.getAllByLabelText('Arrived at')[0]);
    await userEvent.click(await screen.findByRole('option', { name: 'Warehouse' }));

    expect(onArrivalChange).toHaveBeenCalledWith(1, 'location', 11);
  });

  it('explains what to do before any asset is selected', () => {
    // Covers: B6 FR-009, B6 FR-013.
    // FR-013 requires at least one Asset, so an empty state here is a step in the flow
    // rather than an error to report.
    setup({ selectedIds: [] });

    expect(screen.getByRole('alert')).toHaveTextContent(/select the assets/i);
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
  });

  it('states plainly why a save was refused when the attestation is missing', () => {
    // Covers: B6 FR-009.
    setup({ showAttestError: true });

    const alerts = screen.getAllByRole('alert');
    expect(alerts.some((a) => /confirm the assets have arrived/i.test(a.textContent)))
      .toBe(true);
  });
});
