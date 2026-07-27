import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import {
  Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  IconButton, MenuItem, Select, TextField, Typography,
} from '@mui/material';
import AssignmentReturnIcon from '@mui/icons-material/AssignmentReturn';
import LaptopChromebookIcon from '@mui/icons-material/LaptopChromebook';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../AuthContext';

const CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required"];

const Checkouts = () => {
  const [rows, setRows] = useState([]);
  const [checkinTarget, setCheckinTarget] = useState(null);
  const [condition, setCondition] = useState('Good');
  const [remarks, setRemarks] = useState('');
  const [message, setMessage] = useState(null);
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get('/checkout/').then((res) => setRows(res.data));
  };

  useEffect(() => { load(); }, []);

  const doCheckin = async () => {
    try {
      await AxiosInstance.post(`/checkout/${checkinTarget.id}/checkin/`, { condition, remarks });
      setMessage(<MyMessage messageText="Asset checked in. Usage session ended." messageColor="green" />);
      setCheckinTarget(null);
      setRemarks('');
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Check-in failed.'} messageColor="red" />);
      setCheckinTarget(null);
    }
  };

  const columns = useMemo(() => [
    { accessorFn: (r) => r.asset_details?.asset_id, id: 'asset', header: 'Asset' },
    { accessorFn: (r) => r.user_details?.user_name, id: 'user', header: 'User' },
    {
      accessorKey: 'checkout_date', header: 'Checkout Date',
      Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString(),
    },
    { accessorKey: 'expected_return_date', header: 'Expected Return' },
    {
      accessorKey: 'return_date', header: 'Returned On',
      Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleDateString() : '-',
    },
    { accessorKey: 'purpose', header: 'Purpose' },
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
        <LaptopChromebookIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Asset Checkouts
        </Typography>
        {can('asset_custody_manage') && (
          <Button href="/checkout/create" variant="contained" size="small"
            sx={{ marginLeft: 'auto' }}>
            New Checkout
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
              <IconButton color="primary" title="Check in"
                onClick={() => { setCheckinTarget(row.original); setCondition('Good'); }}>
                <AssignmentReturnIcon />
              </IconButton>
            )}
          </Box>
        )}
      />

      <Dialog open={Boolean(checkinTarget)} onClose={() => setCheckinTarget(null)} fullWidth>
        <DialogTitle>
          Check in {checkinTarget?.asset_details?.asset_id}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ marginBottom: '12px' }}>
            Returning from {checkinTarget?.user_details?.user_name}. Record the return condition.
          </Typography>
          <Select fullWidth size="small" value={condition}
            onChange={(e) => setCondition(e.target.value)} sx={{ marginBottom: '12px' }}>
            {CONDITIONS.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
          </Select>
          <TextField fullWidth size="small" label="Remarks" multiline rows={2}
            value={remarks} onChange={(e) => setRemarks(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCheckinTarget(null)}>Cancel</Button>
          <Button variant="contained" onClick={doCheckin}>Check In</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Checkouts;
