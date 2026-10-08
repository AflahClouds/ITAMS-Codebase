import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
const route = { current: '/transfer/assign' };
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: route.current }),
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
import TransferCreate from './Create';
import Transfers from './Transfers';

const available = { id: 3, asset_id: 'AST-003', status: 'Available', custody_type: 'None' };
const held = { id: 4, asset_id: 'AST-004', status: 'Assigned', custody_type: 'Ongoing' };
const employee = { id: 7, user_name: 'Asha' };

describe('Assign ongoing custody', () => {
  beforeEach(() => {
    route.current = '/transfer/assign';
    permissions.current = ['asset_view', 'asset_custody_manage'];
    AxiosInstance.get.mockReset().mockImplementation((path) => {
      if (path.startsWith('/asset/')) return Promise.resolve({ data: [available, held] });
      // The real directory endpoint includes active employees only.
      if (path === '/user/directory/') return Promise.resolve({ data: [employee] });
      if (path === '/department/') return Promise.resolve({ data: [] });
      if (path === '/assignment/') return Promise.resolve({ data: [
        { id: 11, asset_details: held, user_details: employee, status: 'Open',
          issued_at: '2026-09-29T10:00:00Z', issue_condition: 'Good' },
      ] });
      if (path === '/transfer/') return Promise.resolve({ data: [] });
      return Promise.resolve({ data: [] });
    });
    AxiosInstance.post.mockReset().mockResolvedValue({ data: { id: 12 } });
  });

  it('shows only eligible available assets and active employees, then posts an Assign', async () => {
    render(<TransferCreate />);
    expect(await screen.findByText('Assign Ongoing Asset')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('combobox', { name: 'Asset' }));
    expect(screen.getByRole('option', { name: 'AST-003' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'AST-004' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('option', { name: 'AST-003' }));
    await userEvent.click(screen.getByRole('combobox', { name: 'Employee' }));
    expect(screen.getByRole('option', { name: 'Asha' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'Former employee' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('option', { name: 'Asha' }));
    await userEvent.click(screen.getByRole('button', { name: 'Assign Asset' }));
    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalledWith('/assignment/', {
      asset: 3, user: 7, remarks: '',
    }));
  }, 15000);

  it('gates the Assign action by custody permission and labels ongoing history', async () => {
    permissions.current = ['asset_view'];
    const { unmount } = render(<Transfers />);
    expect(await screen.findByText('Ongoing Assignments')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Assign Asset' })).not.toBeInTheDocument();
    unmount();
    permissions.current = ['asset_view', 'asset_custody_manage'];
    render(<Transfers />);
    expect(await screen.findByRole('link', { name: 'Assign Asset' })).toHaveAttribute(
      'href', '/transfer/assign');
    expect(screen.getByText('Ongoing Assignments')).toBeInTheDocument();
  });
});

describe('Take Back ongoing custody', () => {
  beforeEach(() => {
    route.current = '/transfer/assign';
    permissions.current = ['asset_view', 'asset_custody_manage'];
    AxiosInstance.get.mockReset().mockImplementation((path) => {
      if (path === '/assignment/') return Promise.resolve({ data: [
        { id: 11, asset_details: held, user_details: employee, status: 'Open',
          issued_at: '2026-09-29T10:00:00Z', issue_condition: 'Good' },
      ] });
      return Promise.resolve({ data: [] });
    });
    AxiosInstance.post.mockReset().mockResolvedValue({ data: {
      id: 11, status: 'Closed', return_condition: 'Damaged', asset_details: {
        ...held, status: 'Available', condition: 'Damaged', custody_type: 'None',
      },
    } });
  });

  it('requires an explicit condition and deterioration remarks, then shows actual return', async () => {
    render(<Transfers />);
    await userEvent.click(await screen.findByRole('button', { name: 'Take Back AST-004' }));
    expect(screen.getByRole('heading', { name: /Take Back AST-004.*Assignment #11/ })).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: 'Actual return condition' })).toHaveValue('');
    await userEvent.click(screen.getByRole('button', { name: 'Record Take Back' }));
    expect(AxiosInstance.post).not.toHaveBeenCalled();
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Actual return condition' }), 'Damaged');
    await userEvent.click(screen.getByRole('button', { name: 'Record Take Back' }));
    expect(AxiosInstance.post).not.toHaveBeenCalled();
    await userEvent.type(screen.getByRole('textbox', { name: 'Return remarks' }), 'Screen cracked');
    await userEvent.click(screen.getByRole('button', { name: 'Record Take Back' }));
    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalledWith(
      '/assignment/11/take-back/', { condition: 'Damaged', remarks: 'Screen cracked' }));
    expect(await screen.findByText(/Available.*Damaged/)).toBeInTheDocument();
  });

  it('shows the Pending Transfer error and keeps the return form open', async () => {
    AxiosInstance.post.mockRejectedValueOnce({ response: { data: {
      detail: 'Transfer request is not closed.',
    } } });
    render(<Transfers />);
    await userEvent.click(await screen.findByRole('button', { name: 'Take Back AST-004' }));
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Actual return condition' }), 'Good');
    await userEvent.click(screen.getByRole('button', { name: 'Record Take Back' }));
    expect(await screen.findByText('Transfer request is not closed.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Record Take Back' })).toBeInTheDocument();
  });

  it('hides Take Back when custody permission is absent', async () => {
    permissions.current = ['asset_view'];
    render(<Transfers />);
    expect(await screen.findByText('Ongoing Assignments')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Take Back AST-004' })).not.toBeInTheDocument();
  });

  it('shows the return operator, time and inspection in ongoing history', async () => {
    const closedAt = '2026-10-06T10:00:00Z';
    AxiosInstance.get.mockImplementation((path) => Promise.resolve({ data:
      path === '/assignment/' ? [{
        id: 11, asset_details: { ...held, status: 'Available', condition: 'Damaged' },
        user_details: employee, status: 'Closed', closure_reason: 'Take Back',
        issued_at: '2026-09-29T10:00:00Z', issue_condition: 'Good',
        closed_at: closedAt, closed_by_details: { user_name: 'IT operator' },
        return_condition: 'Damaged', return_remarks: 'Screen cracked',
      }] : [],
    }));
    render(<Transfers />);
    expect(await screen.findByText('Assignment #11')).toBeInTheDocument();
    expect(screen.getByText(`${new Date(closedAt).toLocaleString()} by IT operator`)).toBeInTheDocument();
    expect(screen.getByText('Damaged')).toBeInTheDocument();
    expect(screen.getByText('Screen cracked')).toBeInTheDocument();
  });
});

describe('Transfer ongoing custody', () => {
  beforeEach(() => {
    route.current = '/transfer/create';
    permissions.current = ['asset_view', 'asset_custody_manage', 'transfer_request'];
    AxiosInstance.post.mockReset().mockResolvedValue({ data: {} });
    AxiosInstance.get.mockReset().mockImplementation((path) => Promise.resolve({ data:
      path === '/assignment/' ? [] : path === '/transfer/' ? [
        { id: 21, transfer_code: 'TRF-00021', asset_details: held,
          previous_owner_details: employee, new_owner_details: { user_name: 'Bela' },
          status: 'Pending', source_assignment: 11 },
        { id: 22, transfer_code: 'TRF-00022', asset_details: held,
          previous_owner_details: employee, new_owner_details: { user_name: 'Bela' },
          status: 'Approved', source_assignment: 11 },
        { id: 23, transfer_code: 'TRF-00023', asset_details: held,
          previous_owner_details: employee, new_owner_details: { user_name: 'Bela' },
          status: 'Rejected', source_assignment: 11 },
      ] : [],
    }));
  });

  it('retains Pending, Approved and Rejected history and existing document access', async () => {
    render(<Transfers />);
    expect(await screen.findByText('TRF-00021')).toBeInTheDocument();
    expect(screen.getByText('TRF-00022')).toBeInTheDocument();
    expect(screen.getByText('TRF-00023')).toBeInTheDocument();
    expect(screen.getAllByTitle('Download transfer document')).toHaveLength(3);
    expect(screen.getAllByTitle('Approve')).toHaveLength(1);
    expect(screen.getAllByTitle('Reject')).toHaveLength(1);
  });

  it('offers only confirmed ongoing custody as a new Transfer source', async () => {
    const temporary = { id: 5, asset_id: 'AST-005', status: 'Assigned', custody_type: 'Temporary' };
    const unclassified = { id: 6, asset_id: 'AST-006', status: 'Assigned', custody_type: 'Unclassified' };
    AxiosInstance.get.mockImplementation((path) => Promise.resolve({ data:
      path === '/asset/' ? [available, held, temporary, unclassified]
        : path === '/user/directory/' ? [employee, { id: 8, user_name: 'Bela' }] : [],
    }));
    render(<TransferCreate />);
    await userEvent.click(await screen.findByRole('combobox', { name: 'Asset' }));
    expect(screen.getByRole('option', { name: 'AST-004' })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'AST-003' })).not.toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'AST-005' })).not.toBeInTheDocument();
    expect(screen.queryByRole('option', { name: 'AST-006' })).not.toBeInTheDocument();
  });

  it('identifies a transferred Assignment without calling it a physical Take Back', async () => {
    AxiosInstance.get.mockImplementation((path) => Promise.resolve({ data:
      path === '/assignment/' ? [{
        id: 11, asset_details: held, user_details: employee, status: 'Closed',
        issued_at: '2026-09-29T10:00:00Z', issue_condition: 'Good',
        closure_reason: 'Transfer', superseded_by_transfer: 22,
        closed_at: '2026-10-07T10:00:00Z', closed_by_details: { user_name: 'IT operator' },
      }] : [],
    }));
    render(<Transfers />);
    expect(await screen.findByText('Assignment #11')).toBeInTheDocument();
    expect(screen.getByText(/Transferred via TRF-00022/)).toBeInTheDocument();
  });
});
