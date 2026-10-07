import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import { Box, Button, Chip, IconButton, TextField, Typography } from '@mui/material';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const CONDITIONS = ['New', 'Good', 'Average', 'Damaged', 'Repair Required'];
const worsened = (before, after) => before !== 'New' || after !== 'Good'
  ? CONDITIONS.indexOf(after) > CONDITIONS.indexOf(before) : false;

const Transfers = () => {
  const [rows, setRows] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [message, setMessage] = useState(null);
  const [returning, setReturning] = useState(null);
  const [returnCondition, setReturnCondition] = useState('');
  const [returnRemarks, setReturnRemarks] = useState('');
  const [returnError, setReturnError] = useState('');
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get('/transfer/').then((res) => setRows(res.data));
    AxiosInstance.get('/assignment/').then((res) => setAssignments(res.data));
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

  const openReturn = (assignment) => {
    setReturning(assignment);
    setReturnCondition('');
    setReturnRemarks('');
    setReturnError('');
  };

  const recordReturn = async (event) => {
    event.preventDefault();
    if (!returnCondition) {
      setReturnError('Select the actual return condition.');
      return;
    }
    if (worsened(returning.issue_condition, returnCondition) && !returnRemarks.trim()) {
      setReturnError('Record what happened in the return remarks.');
      return;
    }
    try {
      const response = await AxiosInstance.post(`/assignment/${returning.id}/take-back/`, {
        condition: returnCondition, remarks: returnRemarks.trim(),
      });
      setMessage(<MyMessage messageText={`Take Back recorded: ${response.data.asset_details?.status || 'Available'} · ${response.data.return_condition}.`} messageColor="green" />);
      setReturning(null);
      setReturnError('');
      load();
    } catch (err) {
      setReturnError(err.response?.data?.detail || 'Take Back failed.');
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

  const assignmentColumns = useMemo(() => [
    { accessorFn: (r) => r.asset_details?.asset_id, id: 'asset', header: 'Asset' },
    { accessorFn: (r) => r.user_details?.user_name, id: 'holder', header: 'Employee' },
    { accessorKey: 'issue_condition', header: 'Issue Condition' },
    { accessorKey: 'issued_at', header: 'Issued At' },
    { accessorKey: 'status', header: 'Status' },
    { accessorKey: 'return_condition', header: 'Actual Return Condition' },
  ], []);

  return (
    <div>
      <Box className={'TopBar'}>
        <SwapHorizIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Assignments &amp; Transfers
        </Typography>
        {can('asset_custody_manage') && (
          <Button href="/transfer/assign" variant="contained" size="small"
            sx={{ marginLeft: 'auto' }}>
            Assign Asset
          </Button>
        )}
        {can('transfer_request') && (
          <Button href="/transfer/create" variant="contained" size="small"
            sx={{ marginLeft: '8px' }}>
            Request Transfer
          </Button>
        )}
      </Box>

      {message}

      <Typography variant="subtitle2" sx={{ marginTop: '16px', marginBottom: '8px' }}>
        Ongoing Assignments
      </Typography>
      <MaterialReactTable columns={assignmentColumns} data={assignments}
        enableRowActions={can('asset_custody_manage')}
        renderRowActions={({ row }) => row.original.status === 'Open' &&
          can('asset_custody_manage') && (
          <Button size="small" aria-label={`Take Back ${row.original.asset_details?.asset_id}`}
            onClick={() => openReturn(row.original)}>Take Back</Button>
        )} />
      {returning && can('asset_custody_manage') && (
        <Box component="form" onSubmit={recordReturn} sx={{ padding: '16px' }}>
          <Typography variant="subtitle2">
            {`Take Back ${returning.asset_details?.asset_id} · Assignment #${returning.id} · ${returning.user_details?.user_name}`}
          </Typography>
          <Typography variant="body2">{`Issue condition: ${returning.issue_condition}`}</Typography>
          <label htmlFor="return-condition">Actual return condition</label>
          <select id="return-condition" aria-label="Actual return condition"
            value={returnCondition} onChange={(event) => {
              setReturnCondition(event.target.value); setReturnError('');
            }}>
            <option value="">Select condition</option>
            {CONDITIONS.map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
          <TextField label="Return remarks" value={returnRemarks}
            onChange={(event) => { setReturnRemarks(event.target.value); setReturnError(''); }}
            fullWidth multiline sx={{ marginTop: '8px' }} />
          {returnError && <Typography role="alert" color="error">{returnError}</Typography>}
          <Box sx={{ marginTop: '8px' }}>
            <Button type="submit" variant="contained">Record Take Back</Button>
            <Button onClick={() => setReturning(null)}>Cancel</Button>
          </Box>
        </Box>
      )}

      <Typography variant="subtitle2" sx={{ marginTop: '16px', marginBottom: '8px' }}>
        Transfer Requests
      </Typography>

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
