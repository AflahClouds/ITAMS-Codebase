import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/transfer/assign' }),
}));
vi.mock('material-react-table', () => ({
  MaterialReactTable: ({ data, columns }) => <table><tbody>{data.map((row) =>
    <tr key={row.id}>{columns.map((column) => <td key={column.id || column.accessorKey}>
      {column.accessorFn ? column.accessorFn(row) : row[column.accessorKey]}
    </td>)}</tr>)}</tbody></table>,
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
