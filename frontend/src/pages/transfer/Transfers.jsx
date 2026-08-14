import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import { Box, Button, Chip, IconButton, Typography } from '@mui/material';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const Transfers = () => {
  const [rows, setRows] = useState([]);
  const [message, setMessage] = useState(null);
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get('/transfer/').then((res) => setRows(res.data));
  };

  useEffect(() => { load(); }, []);

  const downloadDocument = async (transfer) => {
    const res = await AxiosInstance.get(
      `/transfer/${transfer.id}/document/`, { responseType: 'blob' });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transfer_${transfer.transfer_code}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const act = async (id, action) => {
    try {
      await AxiosInstance.post(`/transfer/${id}/${action}/`);
      setMessage(<MyMessage
        messageText={action === 'approve'
          ? 'Transfer approved. Custodian updated.'
          : 'Transfer request rejected.'}
        messageColor={action === 'approve' ? 'green' : 'red'} />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Action failed.'} messageColor="red" />);
    }
  };

  const columns = useMemo(() => [
    { accessorKey: 'transfer_code', header: 'Transfer ID' },
    { accessorFn: (r) => r.asset_details?.asset_id, id: 'asset', header: 'Asset' },
    {
      accessorFn: (r) => r.previous_owner_details?.user_name || '— none recorded',
      id: 'from', header: 'From',
    },
    { accessorFn: (r) => r.new_owner_details?.user_name, id: 'to', header: 'To' },
    {
      accessorFn: (r) => r.new_department_details?.name || '-',
      id: 'dept', header: 'New Department',
    },
    {
      accessorKey: 'transfer_date', header: 'Date',
      Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString(),
    },
    {
      accessorFn: (r) => r.requested_by_details?.user_name || '-',
      id: 'requested', header: 'Requested By',
    },
    {
      accessorKey: 'status', header: 'Status',
      Cell: ({ cell }) => (
        <Chip label={cell.getValue()} size="small"
          color={cell.getValue() === 'Approved' ? 'success'
            : cell.getValue() === 'Pending' ? 'warning' : 'error'} />
      ),
    },
  ], []);

  return (
    <div>
      <Box className={'TopBar'}>
        <SwapHorizIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Asset Transfers
        </Typography>
        {can('transfer_request') && (
          <Button href="/transfer/create" variant="contained" size="small"
            sx={{ marginLeft: 'auto' }}>
            Request Transfer
          </Button>
        )}
      </Box>

      {message}

      <MaterialReactTable
        columns={columns}
        data={rows}
        enableRowActions
        renderRowActions={({ row }) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap' }}>
            {row.original.status === 'Pending' && can('asset_custody_manage') && (
              <>
                <IconButton color="success" title="Approve"
                  onClick={() => act(row.original.id, 'approve')}>
                  <CheckCircleIcon />
                </IconButton>
                <IconButton color="error" title="Reject"
                  onClick={() => act(row.original.id, 'reject')}>
                  <CancelIcon />
                </IconButton>
              </>
            )}
            <IconButton color="default" title="Download transfer document"
              onClick={() => downloadDocument(row.original)}>
              <PictureAsPdfIcon />
            </IconButton>
          </Box>
        )}
      />
    </div>
  );
};

export default Transfers;
