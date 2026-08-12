import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import {
  Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  IconButton, TextField, Typography,
} from '@mui/material';
import AssignmentReturnIcon from '@mui/icons-material/AssignmentReturn';
import BuildIcon from '@mui/icons-material/Build';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const Services = () => {
  const [rows, setRows] = useState([]);
  const [closeTarget, setCloseTarget] = useState(null);
  const [cost, setCost] = useState('');
  const [remarks, setRemarks] = useState('');
  const [message, setMessage] = useState(null);
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get('/service/').then((res) => setRows(res.data));
  };

  useEffect(() => { load(); }, []);

  const doClose = async () => {
    try {
      await AxiosInstance.post(`/service/${closeTarget.id}/close/`, { cost, remarks });
      setMessage(<MyMessage messageText="Service record closed. Asset is Available again." messageColor="green" />);
      setCloseTarget(null);
      setCost('');
      setRemarks('');
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to close service record.'} messageColor="red" />);
      setCloseTarget(null);
    }
  };

  const columns = useMemo(() => [
    { accessorFn: (r) => r.asset_details?.asset_id, id: 'asset', header: 'Asset' },
    { accessorFn: (r) => r.vendor_details?.name, id: 'vendor', header: 'Vendor' },
    {
      accessorKey: 'sent_date', header: 'Sent Date',
      Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString(),
    },
    { accessorKey: 'expected_return_date', header: 'Expected Return' },
    {
      accessorKey: 'returned_date', header: 'Returned On',
      Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleDateString() : '-',
    },
    { accessorKey: 'reason', header: 'Reason' },
    {
      accessorKey: 'cost', header: 'Cost',
      Cell: ({ cell }) => cell.getValue() ?? '-',
    },
    {
      accessorKey: 'status', header: 'Status',
      Cell: ({ cell }) => (
        <Chip label={cell.getValue()} size="small"
          color={cell.getValue() === 'Open' ? 'warning' : 'success'} />
      ),
    },
  ], []);

  return (
    <div>
      <Box className={'TopBar'}>
        <BuildIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Service Records
        </Typography>
        {can('asset_custody_manage') && (
          <Button href="/service/create" variant="contained" size="small"
            sx={{ marginLeft: 'auto' }}>
            Send for Service
          </Button>
        )}
      </Box>

      {message}

      <MaterialReactTable
        columns={columns}
        data={rows}
        enableRowActions
        renderRowActions={({ row }) => (
          <Box>
            {row.original.status === 'Open' && can('asset_custody_manage') && (
              <IconButton color="primary" title="Close (asset returned)"
                onClick={() => { setCloseTarget(row.original); setCost(''); setRemarks(''); }}>
                <AssignmentReturnIcon />
              </IconButton>
            )}
          </Box>
        )}
      />

      <Dialog open={Boolean(closeTarget)} onClose={() => setCloseTarget(null)} fullWidth>
        <DialogTitle>
          Close service for {closeTarget?.asset_details?.asset_id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ marginBottom: '12px' }}>
            Returning from {closeTarget?.vendor_details?.name}. The asset becomes Available —
            check it back out separately if needed.
          </Typography>
          <TextField fullWidth size="small" label="Cost" type="number" required
            sx={{ marginBottom: '12px' }} helperText="Enter 0 if there was no charge."
            value={cost} onChange={(e) => setCost(e.target.value)} />
          <TextField fullWidth size="small" label="Remarks" multiline rows={2}
            value={remarks} onChange={(e) => setRemarks(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCloseTarget(null)}>Cancel</Button>
          <Button variant="contained" onClick={doClose} disabled={cost === ''}>
            Close Service
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Services;
