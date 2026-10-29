import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import { beforeEach, expect, it, vi } from 'vitest';

const purchaseState = vi.hoisted(() => ({ released: false }));
vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../../auth/useAuth', () => ({
  useAuth: () => ({ user: { is_admin: true }, can: () => true }),
}));
// Keep the real App routing, permission guards, release form and Asset detail;
// exclude only navigation chrome and its unrelated polling.
vi.mock('../../components/navbar/Navbar', () => ({
  default: ({ content }) => <main>{content}</main>,
}));

import AxiosInstance from '../../api/client';
import App from '../../App';

beforeEach(() => {
  purchaseState.released = false;
  AxiosInstance.get.mockReset().mockImplementation((url) => {
    if (url === '/procurement/7/') return Promise.resolve({ data: {
      id: 7, invoice_number: 'INV-7', assets: [{ id: 1, asset_id: 'ONLY' }],
    } });
    if (url === '/asset/1/') return Promise.resolve({ data: {
      id: 1, asset_id: 'ONLY', tag_number: 'ONLY-T', serial_number: 'ONLY-S',
      status: purchaseState.released ? 'In Storage' : 'Available', condition: 'New',
      procurement: purchaseState.released ? null : 7,
      procurement_details: purchaseState.released ? null : { invoice_number: 'INV-7' },
      procurement_invoice: null, custodian: null, department: null, images: [], documents: [],
    } });
    if (url === '/asset/1/history/') return Promise.resolve({ data: {
      assignments: [], checkouts: [], transfers: [], condition_logs: [], services: [], amc_contracts: [],
    } });
    return Promise.resolve({ data: [] });
  });
  AxiosInstance.post.mockReset().mockImplementation((url) => {
    if (url !== '/procurement/7/permanent-delete/') throw new Error(`Unexpected action ${url}`);
    purchaseState.released = true;
    return Promise.resolve({ status: 204 });
  });
});

it('releases Procurement and opens the retained Asset through the actual App detail route with fresh state', async () => {
  render(<MemoryRouter initialEntries={['/procurement/delete/7']}><App /></MemoryRouter>);
  await userEvent.click(await screen.findByRole('button', { name: 'Permanently delete Procurement' }));
  expect(AxiosInstance.get).not.toHaveBeenCalledWith('/asset/1/');
  await userEvent.click(screen.getByRole('button', { name: 'Confirm permanent deletion' }));
  expect(await screen.findByText('In Storage')).toBeInTheDocument();
  await waitFor(() => expect(AxiosInstance.get).toHaveBeenCalledWith('/asset/1/'));
  expect(screen.getByText('ONLY')).toBeInTheDocument();
  expect(screen.queryByText('INV-7')).not.toBeInTheDocument();
  expect(screen.getByText('Procurement Invoice Number').parentElement).toHaveTextContent('-');
  expect(screen.getByText('No purchase invoice attached.')).toBeInTheDocument();
});
