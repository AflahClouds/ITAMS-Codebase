import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { beforeEach, expect, it, vi } from 'vitest';
import Masters from './Masters';
import AxiosInstance from '../../api/client';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), post: vi.fn(), delete: vi.fn() } }));

beforeEach(() => {
  vi.clearAllMocks();
  AxiosInstance.get.mockImplementation((url) => Promise.resolve({ data:
    url === '/brand/' ? [{ id: 7, brand_name: 'Dell' }] :
      url === '/model/' ? [{ id: 8, model_name: 'Latitude', brand: 7 }] : [] }));
  AxiosInstance.post.mockResolvedValue({ data: {} });
});

it('selects, submits and displays the Model Brand', async () => {
  render(<Masters />);
  fireEvent.click(screen.getByRole('tab', { name: 'Models' }));
  const brand = await screen.findByLabelText('Brand');
  fireEvent.change(brand, { target: { value: '7' } });
  fireEvent.change(screen.getByLabelText('New model name'), { target: { value: 'Precision' } });
  fireEvent.click(screen.getByRole('button', { name: 'Add' }));
  await waitFor(() => expect(AxiosInstance.post).toHaveBeenCalledWith('/model/', { model_name: 'Precision', brand: 7 }));
  expect(await screen.findByRole('cell', { name: 'Dell' })).toBeInTheDocument();
});
