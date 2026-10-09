import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn(), put: vi.fn() } }));
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({ id: '1' }),
}));

import AxiosInstance from '../../api/client';
import AssetCreate from './Create';
import AssetEdit from './Edit';

const existingAsset = {
  id: 1, asset_id: 'AST-001', name: 'Laptop', tag_number: 101,
  serial_number: 'SER-001', category: 1, brand: 2, model: 3,
  status: 'Assigned', condition: 'Good', location: null, department: 4,
  warranty_start: null, warranty_end: null, has_amc: false,
  amc_start: null, amc_end: null, purchase_cost: null,
  depreciation_rate: null, asset_life: null, notes: '',
};

const choose = async (label, value) => {
  await userEvent.click(screen.getByRole('combobox', { name: label }));
  await userEvent.click(screen.getByRole('option', { name: value }));
};

describe('Asset department is derived from custody', () => {
  beforeEach(() => {
    AxiosInstance.get.mockReset().mockImplementation((path) => {
      const data = {
        '/asset/1/': existingAsset,
        '/category/': [{ id: 1, category_name: 'Computers' }],
        '/brand/': [{ id: 2, brand_name: 'Example' }],
        '/model/': [{ id: 3, model_name: 'Laptop' }],
        '/department/': [{ id: 4, name: 'Holder department' }],
      }[path] ?? [];
      return Promise.resolve({ data });
    });
    AxiosInstance.post.mockReset().mockResolvedValue({ data: { id: 2 } });
    AxiosInstance.put.mockReset().mockResolvedValue({ data: existingAsset });
  });

  it('creates an unheld Asset without an editable or submitted Department', async () => {
    render(<AssetCreate />);
    expect(await screen.findByRole('combobox', { name: 'Category' })).toBeInTheDocument();
    expect(screen.queryByRole('combobox', { name: 'Department' })).not.toBeInTheDocument();
    await userEvent.type(screen.getByRole('textbox', { name: 'Asset ID' }), 'AST-002');
    await userEvent.type(screen.getByRole('textbox', { name: 'Tag Number' }), '102');
    await userEvent.type(screen.getByRole('textbox', { name: 'Serial Number' }), 'SER-002');
    await choose('Category', 'Computers');
    await choose('Brand', 'Example');
    await choose('Model', 'Laptop');
    await userEvent.click(screen.getByRole('button', { name: 'Add Asset' }));
    await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalled());
    expect(AxiosInstance.post.mock.calls[0][0]).toBe('/asset/');
    expect(AxiosInstance.post.mock.calls[0][1]).not.toHaveProperty('department');
  }, 45000);

  it('edits unrelated Asset details without submitting its derived Department', async () => {
    render(<AssetEdit />);
    await waitFor(() => expect(screen.getByRole('textbox', { name: 'Asset ID' }))
      .toHaveValue('AST-001'));
    expect(screen.queryByRole('combobox', { name: 'Department' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Update Asset' }));
    await waitFor(() => expect(AxiosInstance.put).toHaveBeenCalled());
    expect(AxiosInstance.put.mock.calls[0][0]).toBe('/asset/1/');
    expect(AxiosInstance.put.mock.calls[0][1]).not.toHaveProperty('department');
  }, 15000);
});
