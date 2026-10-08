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
  const [classifyTarget, setClassifyTarget] = useState(null);
  const [reconcileTarget, setReconcileTarget] = useState(null);
  const [approvedTransfers, setApprovedTransfers] = useState([]);
  const [selectedTransfer, setSelectedTransfer] = useState('');
  const [currentCustodyType, setCurrentCustodyType] = useState('');
  const [reconciliationRemarks, setReconciliationRemarks] = useState('');
  const [classification, setClassification] = useState('');
  const [classificationRemarks, setClassificationRemarks] = useState('');
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

  const doClassify = async () => {
    try {
      await AxiosInstance.post(`/checkout/${classifyTarget.id}/classify/`, {
        custody_type: classification, remarks: classificationRemarks,
      });
      setMessage(<MyMessage messageText="Legacy Checkout classified." messageColor="green" />);
      setClassifyTarget(null);
      setClassification('');
      setClassificationRemarks('');
      load();
    } catch (err) {
      setMessage(<MyMessage messageText={err.response?.data?.detail ||
        'Classification failed.'} messageColor="red" />);
    }
  };

  const openReconciliation = async (row) => {
    setReconcileTarget(row);
    setSelectedTransfer('');
    setCurrentCustodyType('');
    setReconciliationRemarks('');
    try {
      const response = await AxiosInstance.get('/transfer/');
      setApprovedTransfers(response.data.filter((transfer) =>
        transfer.status === 'Approved' && transfer.asset === row.asset_details?.id));
    } catch {
      setApprovedTransfers([]);
      setMessage(<MyMessage messageText="Could not load approved Transfer evidence."
        messageColor="red" />);
    }
  };

  const doReconcile = async () => {
    try {
      await AxiosInstance.post(`/checkout/${reconcileTarget.id}/reconcile/`, {
        approved_transfer: Number(selectedTransfer), custody_type: currentCustodyType,
        remarks: reconciliationRemarks,
      });
      setMessage(<MyMessage messageText="Historical handoff reconciled administratively."
        messageColor="green" />);
      setReconcileTarget(null);
      load();
    } catch (err) {
      setMessage(<MyMessage messageText={err.response?.data?.detail ||
        'Reconciliation failed.'} messageColor="red" />);
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
            {row.original.status === 'Open' && row.original.classification === 'Unclassified' &&
              row.original.current_custody_type === 'Unclassified' &&
              can('asset_custody_manage') && (
              <Button size="small"
                aria-label={`Classify ${row.original.asset_details?.asset_id}`}
                onClick={() => { setClassifyTarget(row.original); setClassification('');
                  setClassificationRemarks(''); }}>
                Classify
              </Button>
            )}
            {row.original.status === 'Open' && row.original.classification === 'Unclassified' &&
              row.original.current_custody_type === 'Conflicting' && (
              <>
                <Typography variant="body2">Conflicting custody records — investigate</Typography>
                {can('asset_custody_manage') && (
                  <Button size="small"
                    aria-label={`Reconcile ${row.original.asset_details?.asset_id}`}
                    onClick={() => openReconciliation(row.original)}>
                    Reconcile
                  </Button>
                )}
              </>
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

      <Dialog open={Boolean(reconcileTarget)} onClose={() => setReconcileTarget(null)} fullWidth>
        <DialogTitle>Reconcile historical handoff {reconcileTarget?.asset_details?.asset_id}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ marginBottom: '12px' }}>
            Verify the complete Approved Transfer chain and current holder before recording
            administrative reconciliation. This records no physical Check-in.
          </Typography>
          <Box sx={{ marginBottom: '12px' }}>
            <label htmlFor="reconcile-transfer">Approved Transfer</label>
            <select id="reconcile-transfer" aria-label="Approved Transfer"
              value={selectedTransfer} onChange={(event) => setSelectedTransfer(event.target.value)}>
              <option value="">Choose final approved Transfer</option>
              {approvedTransfers.map((transfer) => (
                <option key={transfer.id} value={transfer.id}>
                  {`${transfer.transfer_code} ${transfer.previous_owner_details?.user_name || 'Unknown'} → ${transfer.new_owner_details?.user_name || 'Unknown'}`}
                </option>
              ))}
            </select>
          </Box>
          <Box sx={{ marginBottom: '12px' }}>
            <label htmlFor="reconcile-type">Current custody type</label>
            <select id="reconcile-type" aria-label="Current custody type"
              value={currentCustodyType}
              onChange={(event) => setCurrentCustodyType(event.target.value)}>
              <option value="">Choose custody type</option>
              <option value="Temporary">Temporary</option>
              <option value="Ongoing">Ongoing</option>
            </select>
          </Box>
          <TextField fullWidth size="small" label="Reconciliation remarks" multiline rows={2}
            value={reconciliationRemarks}
            onChange={(event) => setReconciliationRemarks(event.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReconcileTarget(null)}>Cancel</Button>
          <Button variant="contained" disabled={!selectedTransfer || !currentCustodyType}
            onClick={doReconcile}>Record Reconciliation</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(classifyTarget)} onClose={() => setClassifyTarget(null)} fullWidth>
        <DialogTitle>Classify legacy Checkout {classifyTarget?.asset_details?.asset_id}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ marginBottom: '12px' }}>
            This administrative classification records actual custody; no physical Check-in occurs.
          </Typography>
          <select aria-label="Custody type" value={classification}
            onChange={(event) => setClassification(event.target.value)}>
            <option value="">Choose custody type</option>
            <option value="Temporary">Temporary</option>
            <option value="Ongoing">Ongoing</option>
          </select>
          <TextField fullWidth size="small" label="Classification remarks" multiline rows={2}
            value={classificationRemarks}
            onChange={(event) => setClassificationRemarks(event.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClassifyTarget(null)}>Cancel</Button>
          <Button variant="contained" disabled={!classification} onClick={doClassify}>
            Record Classification
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Checkouts;
