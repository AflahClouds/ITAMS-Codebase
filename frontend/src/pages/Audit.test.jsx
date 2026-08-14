/**
 * Conformance tests for the Audit Trail surface.
 *
 * Each test carries a `Covers:` tag naming the requirements it demonstrates; those tags
 * feed docs/conformance/traceability-map.md alongside the backend ones.
 *
 * B8 FR-022 is the reason this file exists first. The backend was made to disclose that
 * an audit view is truncated, but the requirement is about what a *reader* can tell —
 * a UI that drops the disclosure defeats the fix while every backend test still passes.
 */
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../api/client', () => ({
  default: { get: vi.fn() },
}));

import AxiosInstance from '../api/client';
import Audit from './Audit';

const entry = (over = {}) => ({
  id: 1,
  date: '2026-08-13T09:00:00Z',
  username: 'alice',
  action: 'Create',
  module: 'Assets',
  old_value: '',
  new_value: 'AST-001',
  ip_address: '10.0.0.5',
  ...over,
});

const envelope = (results, over = {}) => ({
  data: { limit: 1000, total: results.length, omitted: 0, results, ...over },
});

describe('Audit trail', () => {
  beforeEach(() => {
    AxiosInstance.get.mockReset();
  });

  it('reads its rows from the disclosure envelope', async () => {
    // Covers: B8 FR-021, B8 FR-016.
    AxiosInstance.get.mockResolvedValue(envelope([entry()]));

    render(<Audit />);

    expect(await screen.findByText('alice')).toBeInTheDocument();
    expect(screen.getByText('AST-001')).toBeInTheDocument();
  });

  it('warns the reader when older matching events were omitted', async () => {
    // Covers: B8 FR-022.
    AxiosInstance.get.mockResolvedValue(
      envelope([entry()], { total: 1400, omitted: 400 }),
    );

    render(<Audit />);

    const warning = await screen.findByRole('alert');
    expect(warning).toHaveTextContent('1,000');
    expect(warning).toHaveTextContent('1,400');
    expect(warning).toHaveTextContent('400 older events are not shown');
  });

  it('shows no omission warning when the result set is complete', async () => {
    // Covers: B8 FR-022.
    // The warning has to mean something. If it appeared on every complete result it
    // would be ignored by the time it mattered.
    AxiosInstance.get.mockResolvedValue(envelope([entry()]));

    render(<Audit />);

    await screen.findByText('alice');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders an empty audit trail without failing', async () => {
    // Covers: B8 FR-021.
    // An empty result is a normal outcome, not an error.
    AxiosInstance.get.mockResolvedValue(envelope([]));

    render(<Audit />);

    await waitFor(() => expect(AxiosInstance.get).toHaveBeenCalledWith('/audit/'));
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
});
