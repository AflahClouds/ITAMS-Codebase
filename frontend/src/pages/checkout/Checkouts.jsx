import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import {
  Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  MenuItem, Select, TextField, Typography,
} from '@mui/material';
import AssignmentReturnIcon from '@mui/icons-material/AssignmentReturn';
import LaptopChromebookIcon from '@mui/icons-material/LaptopChromebook';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required"];
const physicallyCheckedIn = (row) => row.status === 'Returned' &&
  !row.closed_as_interrupted && (!row.closure_reason || row.closure_reason === 'Returned');

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
      setMessage(<MyMessage messageText="Temporary Checkout checked in." messageColor="green" />);
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
    { accessorFn: (r) => r.classification || 'Unclassified', id: 'type', header: 'Custody Type' },
    { accessorFn: (r) => r.approved_by_details?.user_name || '-', id: 'issuer', header: 'Issued By' },
    {
      accessorKey: 'checkout_date', header: 'Checkout Date',
      Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString(),
    },
    { accessorKey: 'expected_return_date', header: 'Expected Return' },
    { accessorFn: (r) => physicallyCheckedIn(r) && r.return_date
      ? new Date(r.return_date).toLocaleDateString() : '-',
    id: 'checked_in', header: 'Physical Check-in' },
    { accessorKey: 'purpose', header: 'Purpose' },
    { accessorFn: (r) => physicallyCheckedIn(r) ? r.return_condition : '-',
      id: 'return_condition', header: 'Actual Return Condition' },
    {
      accessorFn: (r) => r.closed_as_interrupted ? 'Interrupted' :
        (r.closure_reason || r.status), id: 'outcome', header: 'Outcome',
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
            New Temporary Checkout
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
            {row.original.status === 'Open' && row.original.classification === 'Temporary' &&
              can('asset_custody_manage') && (
              <Button size="small" startIcon={<AssignmentReturnIcon />}
                aria-label={`Check In ${row.original.asset_details?.asset_id}`}
                onClick={() => { setCheckinTarget(row.original); setCondition('Good'); }}>
                Check In
              </Button>
            )}
          </Box>
        )}
      />

      <Dialog open={Boolean(checkinTarget)} onClose={() => setCheckinTarget(null)} fullWidth>
        <DialogTitle>
          Check In temporary Checkout {checkinTarget?.asset_details?.asset_id}
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
