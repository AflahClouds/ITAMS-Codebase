import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({ id: '4' }),
}));
vi.mock('material-react-table', () => ({
  MaterialReactTable: ({ data, columns, renderRowActions }) => <table><tbody>{data.map((row) =>
    <tr key={row.id}>{columns.map((column) => <td key={column.id || column.accessorKey}>
      {column.accessorFn ? column.accessorFn(row) : row[column.accessorKey]}
    </td>)}{renderRowActions && <td>{renderRowActions({ row: { original: row } })}</td>}</tr>)}</tbody></table>,
}));

const permissions = { current: [] };
vi.mock('../../auth/useAuth', () => ({
  useAuth: () => ({ can: (code) => permissions.current.includes(code) }),
}));

import AxiosInstance from '../../api/client';
import CheckoutCreate from './Create';
import Checkouts from './Checkouts';
import AssetDetail from '../asset/Detail';

const asset = { id: 4, asset_id: 'AST-004', status: 'Assigned', condition: 'Good',
  custody_type: 'Temporary', custodian_details: { user_name: 'Asha' } };
const holder = { id: 7, user_name: 'Asha' };
const checkout = { id: 15, asset_details: asset, user_details: holder,
  approved_by_details: { user_name: 'IT operator' }, status: 'Open',
  classification: 'Temporary', purpose: 'On-call spare',
  expected_return_date: '2026-11-01', checkout_date: '2026-10-07T10:00:00Z' };

describe('temporary Checkout and physical Check-in', () => {
  beforeEach(() => {
    permissions.current = ['asset_view', 'asset_custody_manage'];
    AxiosInstance.get.mockReset().mockImplementation((path) => {
      if (path === '/asset/?status=Available') return Promise.resolve({ data: [
        { id: 3, asset_id: 'AST-003', status: 'Available' },
      ] });
      if (path === '/user/directory/') return Promise.resolve({ data: [holder] });
      if (path === '/checkout/') return Promise.resolve({ data: [checkout] });
      if (path === '/asset/4/') return Promise.resolve({ data: asset });
      if (path === '/asset/4/history/') return Promise.resolve({ data: {
        assignments: [], checkouts: [checkout], transfers: [], condition_logs: [],
        services: [], amc_contracts: [],
      } });
      return Promise.resolve({ data: [] });
    });
    AxiosInstance.post.mockReset().mockResolvedValue({ data: { id: 16 } });
  });

  it('presents a temporary loan with purpose and optional expected return date', async () => {
    render(<CheckoutCreate />);
    expect(await screen.findByText('New Temporary Checkout')).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Purpose' })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: 'Expected Return Date (optional)' })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('combobox', { name: 'Asset (available only)' }));
    await userEvent.click(screen.getByRole('option', { name: 'AST-003' }));
    await userEvent.click(screen.getByRole('combobox', { name: 'User' }));
    await userEvent.click(screen.getByRole('option', { name: 'Asha' }));
    await userEvent.type(screen.getByRole('textbox', { name: 'Purpose' }), 'On-call spare');
    await userEvent.click(screen.getByRole('button', { name: 'Checkout Asset' }));
    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalledWith('/checkout/',
      expect.objectContaining({ asset: 3, user: 7, purpose: 'On-call spare',
        expected_return_date: null })));
  }, 15000);

  it('labels the temporary Checkout list and offers Check-in rather than Take Back', async () => {
    render(<Checkouts />);
    expect(await screen.findByText('Temporary')).toBeInTheDocument();
    expect(screen.getByText('On-call spare')).toBeInTheDocument();
    expect(screen.getByText('2026-11-01')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Check In AST-004' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Take Back/ })).not.toBeInTheDocument();
  });

  it('does not report an interrupted temporary loan as a physical Check-in', async () => {
    AxiosInstance.get.mockImplementation((path) => Promise.resolve({ data:
      path === '/checkout/' ? [{ ...checkout, status: 'Returned',
        closed_as_interrupted: true, return_date: '2026-10-09T10:00:00Z' }] : [],
    }));
    render(<Checkouts />);
    expect(await screen.findByText('Interrupted')).toBeInTheDocument();
    expect(screen.queryByText('2026-10-09T10:00:00Z')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Check In AST-004' })).not.toBeInTheDocument();
  });

  it('shows temporary purpose, issuer and Check-in in Asset custody history', async () => {
    render(<AssetDetail />);
    expect(await screen.findByText('Temporary Checkout #15')).toBeInTheDocument();
    expect(screen.getByText(/On-call spare/)).toBeInTheDocument();
    expect(screen.getByText(/IT operator/)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Check In' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Take Back' })).not.toBeInTheDocument();
  });
});
