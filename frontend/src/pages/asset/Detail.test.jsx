import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn() } }));
vi.mock('../../api/downloadProtectedFile', () => ({
  downloadProtectedFile: vi.fn(),
}));
vi.mock('react-router', () => ({ useParams: () => ({ id: '11' }) }));
vi.mock('../../auth/useAuth', () => ({
  useAuth: () => ({ can: (code) => code === 'asset_view' }),
}));

import AxiosInstance from '../../api/client';
import { downloadProtectedFile } from '../../api/downloadProtectedFile';
import AssetDetail from './Detail';

const ASSET = {
  id: 11,
  asset_id: 'AST-11',
  tag_number: 'TAG-11',
  serial_number: 'SER-11',
  status: 'Available',
  condition: 'New',
  images: [],
  documents: [],
  procurement_details: { invoice_number: 'INV-11' },
  procurement_invoice: {
    id: 4,
    file_name: 'shared.pdf',
    version: 3,
    download_url: '/asset/11/procurement-invoice/',
  },
};

describe('Asset mapped procurement invoice', () => {
  beforeEach(() => {
    AxiosInstance.get.mockImplementation((url) => Promise.resolve({
      data: url.endsWith('/history/')
        ? { checkouts: [], transfers: [], condition_logs: [], services: [], amc_contracts: [] }
        : ASSET,
    }));
  });

  it('renders and downloads the Procurement-owned invoice without Asset upload controls', async () => {
    render(<AssetDetail />);

    expect(await screen.findByText(/shared\.pdf \(v3\)/)).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText('Download mapped purchase invoice'));
    expect(downloadProtectedFile).toHaveBeenCalledWith(
      '/asset/11/procurement-invoice/', 'shared.pdf');
    expect(screen.queryByText(/replace purchase invoice/i)).not.toBeInTheDocument();
  });

  it('shows a clear empty state when the linked Procurement has no document', async () => {
    AxiosInstance.get.mockImplementation((url) => Promise.resolve({
      data: url.endsWith('/history/')
        ? { checkouts: [], transfers: [], condition_logs: [], services: [], amc_contracts: [] }
        : { ...ASSET, procurement_invoice: null },
    }));
    render(<AssetDetail />);

    expect(await screen.findByText('No purchase invoice attached.')).toBeInTheDocument();
  });
});
