import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import { beforeEach, expect, it, vi } from 'vitest';

const purchaseState = vi.hoisted(() => ({ released: false, multiple: false, deletionAllowed: true }));
vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() } }));
vi.mock('../../auth/useAuth', () => ({
  useAuth: () => ({ user: { is_admin: true }, can: (code) => code !== 'asset_delete' || purchaseState.deletionAllowed }),
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
  purchaseState.multiple = false;
  purchaseState.deletionAllowed = true;
  const procurement = () => ({
    id: 7, invoice_number: 'INV-7', vendor: 2, mode_of_purchase: 3,
    purchase_date: '2026-01-01', invoice_date: '2026-01-02', po_number: '',
    mode_of_purchase_details: { purchase_mode: 'Purchase' },
    vendor_details: { name: 'Example Vendor' },
    assets: purchaseState.multiple ? [{ id: 1, asset_id: 'ONLY' }, { id: 2, asset_id: 'SECOND' }]
      : [{ id: 1, asset_id: 'ONLY' }],
  });
  AxiosInstance.get.mockReset().mockImplementation((url) => {
    if (url === '/procurement/') return Promise.resolve({ data: [procurement()] });
    if (url === '/procurement/7/') return Promise.resolve({ data: procurement() });
    if (url === '/purchase_mode/') return Promise.resolve({ data: [{ id: 3, purchase_mode: 'Purchase' }] });
    if (url === '/vendor/') return Promise.resolve({ data: [{ id: 2, name: 'Example Vendor' }] });
    if (url === '/asset/') return Promise.resolve({ data: [{ id: 1, asset_id: 'ONLY', has_procurement: true }] });
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
  AxiosInstance.delete.mockReset().mockResolvedValue({ status: 204 });
});

it('releases Procurement and opens the retained Asset through the actual App detail route with fresh state', async () => {
  render(<MemoryRouter initialEntries={['/procurement']}><App /></MemoryRouter>);
  await userEvent.click(await screen.findByRole('link', { name: 'Permanently delete procurement' }));
  expect(await screen.findByRole('heading', { name: 'Permanently delete Procurement?' })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Archive' })).not.toBeInTheDocument();
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
  expect(AxiosInstance.get).not.toHaveBeenCalledWith('/asset/1/');
  await userEvent.click(screen.getByRole('button', { name: 'Confirm permanent deletion' }));
  expect(await screen.findByText('In Storage')).toBeInTheDocument();
  await waitFor(() => expect(AxiosInstance.get).toHaveBeenCalledWith('/asset/1/'));
  expect(screen.getByText('ONLY')).toBeInTheDocument();
  expect(screen.queryByText('INV-7')).not.toBeInTheDocument();
  expect(screen.getByText('Procurement Invoice Number').parentElement).toHaveTextContent('-');
  expect(screen.getByText('No purchase invoice attached.')).toBeInTheDocument();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
});

it('opens only the archive confirmation from the table and archives only on confirmation', async () => {
  render(<MemoryRouter initialEntries={['/procurement']}><App /></MemoryRouter>);
  await userEvent.click(await screen.findByRole('link', { name: 'Archive procurement' }));
  expect(await screen.findByText('Archive this procurement record?')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Permanently delete Procurement' })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Confirm permanent deletion' })).not.toBeInTheDocument();
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
  await userEvent.click(screen.getByRole('button', { name: 'Archive' }));
  expect(await screen.findByText(/Procurement archived/)).toBeInTheDocument();
  expect(AxiosInstance.delete).toHaveBeenCalledWith('/procurement/7/');
  expect(AxiosInstance.post).not.toHaveBeenCalled();
});

it('opens only permanent confirmation from the singleton edit action and cancels without mutation', async () => {
  render(<MemoryRouter initialEntries={['/procurement/edit/7']}><App /></MemoryRouter>);
  await userEvent.click(await screen.findByRole('link', { name: 'Permanently delete Procurement' }));
  expect(await screen.findByRole('heading', { name: 'Permanently delete Procurement?' })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Archive' })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
  await screen.findByRole('link', { name: 'Archive procurement' });
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
});

it('cancels the archive confirmation without either mutation', async () => {
  render(<MemoryRouter initialEntries={['/procurement/delete/7']}><App /></MemoryRouter>);
  await screen.findByText('INV-7');
  await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
  await screen.findByRole('link', { name: 'Archive procurement' });
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
});

it('blocks a directly entered permanent URL for a multi-Asset purchase without offering archive', async () => {
  purchaseState.multiple = true;
  render(<MemoryRouter initialEntries={['/procurement/permanent-delete/7']}><App /></MemoryRouter>);
  expect(await screen.findByText(/Permanent deletion requires exactly one remaining Asset/)).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Confirm permanent deletion' })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Archive' })).not.toBeInTheDocument();
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
});

it('protects the direct permanent URL with the existing deletion permission', async () => {
  purchaseState.deletionAllowed = false;
  render(<MemoryRouter initialEntries={['/procurement/permanent-delete/7']}><App /></MemoryRouter>);
  expect(await screen.findByText('403 — Access denied')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Confirm permanent deletion' })).not.toBeInTheDocument();
  expect(AxiosInstance.post).not.toHaveBeenCalled();
  expect(AxiosInstance.delete).not.toHaveBeenCalled();
});
