import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, it, vi } from 'vitest';

vi.mock('../../api/client', () => ({ default: { get: vi.fn(), delete: vi.fn() } }));
vi.mock('react-router', () => ({
  useNavigate: () => vi.fn(), useParams: () => ({ id: '1' }),
  Link: ({ to, children, ...props }) => <a href={to} {...props}>{children}</a>,
}));
import AxiosInstance from '../../api/client';
import AssetDelete from './Delete';

beforeEach(() => {
  AxiosInstance.get.mockImplementation((path) => Promise.resolve({ data:
    path === '/asset/1/' ? { asset_id: 'LINKED', procurement: 7 } : [],
  }));
  AxiosInstance.delete.mockReset();
});

it('explains linked protection and provides Procurement navigation', async () => {
  render(<AssetDelete />);
  expect(await screen.findByRole('link', { name: 'Open Procurement' }))
    .toHaveAttribute('href', '/procurement/edit/7');
  expect(screen.getByText(/remove.*Procurement.*first/i)).toBeInTheDocument();
});

it('shows a rejected deletion without reporting success', async () => {
  AxiosInstance.delete.mockRejectedValue({ response: { data: {
    detail: 'Remove this Asset from Procurement first.',
  } } });
  render(<AssetDelete />);
  await screen.findByText('LINKED');
  await userEvent.click(screen.getByRole('button', { name: 'Delete' }));
  expect(await screen.findByText('Remove this Asset from Procurement first.')).toBeInTheDocument();
  expect(screen.queryByText(/successfully deleted/i)).not.toBeInTheDocument();
});
