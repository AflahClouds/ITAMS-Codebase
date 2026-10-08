import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import { Box, Button, Chip, Grid, IconButton, MenuItem, Paper, Select, TextField, Typography } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required"];
const DOCUMENT_TYPES = ["Purchase Invoice", "Warranty Card", "AMC Document", "PO Document",
                        "Asset Agreement", "Transfer Document", "Other"];

const Row = ({ label, value }) => (
  <Box sx={{ display: 'flex', padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
    <Typography variant="body2" sx={{ width: '45%', color: 'text.secondary' }}>{label}</Typography>
    <Typography variant="body2" sx={{ fontWeight: 500 }}>{value ?? '-'}</Typography>
  </Box>
);

const AssetDetail = () => {
  const { id } = useParams();
  const [asset, setAsset] = useState(null);
  const [history, setHistory] = useState({
    assignments: [], checkouts: [], transfers: [], condition_logs: [], services: [], amc_contracts: [],
  });
  const [condition, setCondition] = useState('Good');
  const [notes, setNotes] = useState('');
  const [docType, setDocType] = useState('Purchase Invoice');
  const [amcStart, setAmcStart] = useState('');
  const [amcEnd, setAmcEnd] = useState('');
  const [amcEndReason, setAmcEndReason] = useState('');
  const [amcVendor, setAmcVendor] = useState('');
  const [vendors, setVendors] = useState([]);
  const [message, setMessage] = useState(null);
  const imageInput = useRef(null);
  const documentInput = useRef(null);
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get(`/asset/${id}/`).then((res) => setAsset(res.data));
    AxiosInstance.get(`/asset/${id}/history/`).then((res) => setHistory(res.data));
    // Only the renewal form needs the Vendor list, and only asset_edit holders see
    // it — readers without that permission would just be issued a 403 per page view.
    if (can('asset_edit')) {
      AxiosInstance.get('/vendor/').then((res) => setVendors(res.data)).catch(() => setVendors([]));
    }
  };

  useEffect(() => { load(); }, [id]);

  const uploadImages = async (event) => {
    const files = Array.from(event.target.files || []);
    for (const file of files) {
      const form = new FormData();
      form.append('asset', id);
      form.append('file', file);
      try {
        await AxiosInstance.post('/asset_image/', form,
          { headers: { 'Content-Type': 'multipart/form-data' } });
      } catch (err) {
        setMessage(<MyMessage
          messageText={err.response?.data?.detail || `Failed to upload ${file.name}.`}
          messageColor="red" />);
        event.target.value = '';
        return;
      }
    }
    if (files.length) {
      setMessage(<MyMessage messageText={`${files.length} image(s) uploaded.`} messageColor="green" />);
      load();
    }
    event.target.value = '';
  };

  const uploadDocument = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('asset', id);
    form.append('document_type', docType);
    form.append('file', file);
    try {
      const res = await AxiosInstance.post('/asset_document/', form,
        { headers: { 'Content-Type': 'multipart/form-data' } });
      setMessage(<MyMessage
        messageText={`${docType} uploaded (version ${res.data.version}).`} messageColor="green" />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Upload failed.'} messageColor="red" />);
    }
    event.target.value = '';
  };

  const deleteFile = async (endpoint, fileId) => {
    try {
      await AxiosInstance.delete(`/${endpoint}/${fileId}/`);
      setMessage(<MyMessage messageText="File removed." messageColor="green" />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Delete failed.'} messageColor="red" />);
    }
  };

  const recordInspection = async (event) => {
    event.preventDefault();
    try {
      await AxiosInstance.post(`/asset/${id}/add_condition/`, { condition, notes });
      setMessage(<MyMessage messageText="Condition inspection recorded." messageColor="green" />);
      setNotes('');
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to record inspection.'}
        messageColor="red" />);
    }
  };

  const renewAmc = async (event) => {
    event.preventDefault();
    try {
      await AxiosInstance.post(`/asset/${id}/renew_amc/`,
        { amc_start: amcStart, amc_end: amcEnd, vendor: amcVendor });
      setMessage(<MyMessage messageText="AMC renewed. IT Manager notified." messageColor="green" />);
      setAmcStart(''); setAmcEnd(''); setAmcVendor('');
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to renew AMC.'} messageColor="red" />);
    }
  };

  const endAmcSupport = async (event) => {
    event.preventDefault();
    try {
      await AxiosInstance.post(`/asset/${id}/end_amc_support/`, { reason: amcEndReason });
      setMessage(<MyMessage messageText="AMC support ended. IT Manager notified." messageColor="green" />);
      setAmcEndReason('');
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to end AMC support.'} messageColor="red" />);
    }
  };

  if (!asset) return <Typography sx={{ padding: '20px' }}>Loading...</Typography>;

  return (
    <div>
      <Box className={'TopBar'}>
        <InfoIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Asset Detail — {asset.asset_id}
        </Typography>
        <Chip label={asset.status} size="small" sx={{ marginLeft: 'auto' }}
          color={asset.status === 'Available' ? 'success' : asset.status === 'Assigned' ? 'info' : 'warning'} />
      </Box>

      {message}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              General
            </Typography>
            <Row label="Asset ID" value={asset.asset_id} />
            <Row label="Name" value={asset.name || '-'} />
            <Row label="Tag Number" value={asset.tag_number} />
            <Row label="Serial Number" value={asset.serial_number} />
            <Row label="Category" value={asset.category_details?.category_name} />
            <Row label="Brand" value={asset.brand_details?.brand_name} />
            <Row label="Model" value={asset.model_details?.model_name} />
            <Row label="Condition" value={asset.condition} />
            <Row label="Notes" value={asset.notes || '-'} />
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Custody & Warranty
            </Typography>
            <Row label="Custodian" value={asset.custodian_details?.user_name} />
            <Row label="Custody Type" value={asset.custody_type} />
            <Row label="Department" value={asset.department_details?.name} />
            <Row label="Location" value={asset.location_details?.name} />
            <Row label="Warranty Start" value={asset.warranty_start} />
            <Row label="Warranty End" value={asset.warranty_end} />
            <Row label="Warranty Days Left" value={asset.warranty_days_left} />
            <Row label="Purchase Cost" value={asset.purchase_cost} />
            <Row label="Depreciation Rate" value={asset.depreciation_rate} />
            <Row label="Asset Life (years)" value={asset.asset_life} />
            <Row label="Procurement Invoice" value={asset.procurement_details?.invoice_number} />
            {asset.barcode_url && (
              <Box sx={{ marginTop: '12px', textAlign: 'center' }}>
                <img src={asset.barcode_url} alt={`Barcode ${asset.tag_number}`}
                  style={{ maxWidth: '260px', width: '100%' }} />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              AMC (Annual Maintenance Contract)
            </Typography>
            {/* Keyed on whether a contract exists at all, not on has_amc: an Ended
                contract reports has_amc false, and its status, end reason, and history
                still have to be readable — and renewable — after it ends. */}
            {asset.amc_status ? (
              <>
                <Row label="AMC Start" value={asset.amc_start} />
                <Row label="AMC End" value={asset.amc_end} />
                <Row label="AMC Days Left" value={asset.amc_days_left} />
                <Row label="AMC Status"
                  value={<Chip label={asset.amc_status} size="small"
                    color={asset.amc_status === 'Active' ? 'success' : 'default'} />} />
                {asset.amc_status === 'Ended' && (
                  <Row label="End Reason" value={asset.amc_end_reason || '-'} />
                )}

                {can('asset_edit') && (
                  <Box sx={{ marginTop: '12px' }}>
                    <form onSubmit={renewAmc}>
                      <Typography variant="caption" color="text.secondary">Renew AMC</Typography>
                      <Box sx={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', marginTop: '4px' }}>
                        <TextField size="small" type="date" label="New Start"
                          InputLabelProps={{ shrink: true }}
                          value={amcStart} onChange={(e) => setAmcStart(e.target.value)} />
                        <TextField size="small" type="date" label="New End"
                          InputLabelProps={{ shrink: true }}
                          value={amcEnd} onChange={(e) => setAmcEnd(e.target.value)} />
                        <Select size="small" displayEmpty sx={{ minWidth: '160px' }}
                          value={amcVendor} onChange={(e) => setAmcVendor(e.target.value)}>
                          <MenuItem value=""><em>Select vendor</em></MenuItem>
                          {vendors.map((v) => (
                            <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
                          ))}
                        </Select>
                        <Button type="submit" size="small" variant="contained">Renew</Button>
                      </Box>
                    </form>

                    {(asset.amc_status === 'Active' || asset.amc_status === 'Incomplete') && (
                      <form onSubmit={endAmcSupport} style={{ marginTop: '12px' }}>
                        <Typography variant="caption" color="text.secondary">
                          {asset.amc_status === 'Incomplete' ? 'Cancel Planned AMC' : 'End AMC Support'}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', marginTop: '4px' }}>
                          <TextField size="small" label="Reason" sx={{ flexGrow: 1 }}
                            value={amcEndReason} onChange={(e) => setAmcEndReason(e.target.value)} />
                          <Button type="submit" size="small" variant="outlined" color="error">
                            End Support
                          </Button>
                        </Box>
                      </form>
                    )}
                  </Box>
                )}

                {history.amc_contracts.length > 1 && (
                  <Box sx={{ marginTop: '12px' }}>
                    <Typography variant="caption" color="text.secondary">AMC History</Typography>
                    {history.amc_contracts.map((c) => (
                      <Box key={c.id} sx={{ padding: '4px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Typography variant="body2">
                          {c.start_date} → {c.end_date} — <Chip label={c.status} size="small" />
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">
                This asset has no AMC. Set one via Edit Asset.
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ padding: '16px' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
                Images ({asset.images?.length || 0})
              </Typography>
              {can('asset_edit') && (
                <>
                  <input ref={imageInput} type="file" accept=".jpg,.jpeg,.png,.webp"
                    multiple hidden onChange={uploadImages} />
                  <Button size="small" variant="outlined" startIcon={<UploadFileIcon />}
                    onClick={() => imageInput.current?.click()}>
                    Upload
                  </Button>
                </>
              )}
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {(asset.images || []).length === 0 && (
                <Typography variant="body2" color="text.secondary">No images uploaded.</Typography>)}
              {(asset.images || []).map((img) => (
                <Box key={img.id} sx={{ position: 'relative', width: '110px' }}>
                  <a href={img.file} target="_blank" rel="noreferrer">
                    <img src={img.file} alt={img.file_name}
                      style={{ width: '110px', height: '80px', objectFit: 'cover',
                               borderRadius: '4px', border: '1px solid #ddd' }} />
                  </a>
                  {can('asset_delete') && (
                    <IconButton size="small" color="error"
                      sx={{ position: 'absolute', top: 0, right: 0, background: 'white' }}
                      onClick={() => deleteFile('asset_image', img.id)}>
                      <DeleteIcon fontSize="inherit" />
                    </IconButton>
                  )}
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ padding: '16px' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
                Documents ({asset.documents?.length || 0})
              </Typography>
              {can('asset_edit') && (
                <>
                  <Select size="small" value={docType} onChange={(e) => setDocType(e.target.value)}>
                    {DOCUMENT_TYPES.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                  </Select>
                  <input ref={documentInput} type="file"
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.webp"
                    hidden onChange={uploadDocument} />
                  <Button size="small" variant="outlined" startIcon={<UploadFileIcon />}
                    onClick={() => documentInput.current?.click()}>
                    Upload
                  </Button>
                </>
              )}
            </Box>
            {(asset.documents || []).length === 0 && (
              <Typography variant="body2" color="text.secondary">No documents uploaded.</Typography>)}
            {(asset.documents || []).map((doc) => (
              <Box key={doc.id} sx={{ display: 'flex', alignItems: 'center',
                                      padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2">
                    {doc.document_type} <Chip label={`v${doc.version}`} size="small" sx={{ marginLeft: '4px' }} />
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {doc.file_name} — {new Date(doc.upload_date).toLocaleDateString()}
                    {doc.uploaded_by_details && ` by ${doc.uploaded_by_details.user_name}`}
                  </Typography>
                </Box>
                <IconButton size="small" component="a" href={doc.file} target="_blank" rel="noreferrer">
                  <DownloadIcon fontSize="small" />
                </IconButton>
                {can('asset_delete') && (
                  <IconButton size="small" color="error"
                    onClick={() => deleteFile('asset_document', doc.id)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                )}
              </Box>
            ))}
          </Paper>
        </Grid>

        {can('asset_edit') && (
          <Grid size={{ xs: 12 }}>
            <Paper sx={{ padding: '16px' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
                Record Condition Inspection
              </Typography>
              <form onSubmit={recordInspection}>
                <Box sx={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <Select size="small" value={condition} onChange={(e) => setCondition(e.target.value)}>
                    {CONDITIONS.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
                  </Select>
                  <TextField size="small" label="Notes" sx={{ flexGrow: 1 }}
                    value={notes} onChange={(e) => setNotes(e.target.value)} />
                  <Button type="submit" variant="contained">Record</Button>
                </Box>
              </form>
            </Paper>
          </Grid>
        )}

        <Grid size={{ xs: 12, md: 3 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Ongoing Assignments
            </Typography>
            {(history.assignments || []).length === 0 && (
              <Typography variant="body2" color="text.secondary">No ongoing assignments.</Typography>)}
            {(history.assignments || []).map((assignment) => (
              <Box key={assignment.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {`Assignment #${assignment.id} · ${assignment.user_details?.user_name}`} — <Chip label={assignment.status} size="small" />
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {assignment.provenance === 'Administrative reconstruction'
                    ? `Recorded ${new Date(assignment.issued_at).toLocaleString()}`
                    : `Issued ${new Date(assignment.issued_at).toLocaleString()}`}
                  {assignment.issued_by_details && ` by ${assignment.issued_by_details.user_name}`}
                  {` · ${assignment.issue_condition || 'Issue condition not recorded'}`}
                </Typography>
                {assignment.date_basis && (
                  <Typography variant="caption" display="block">
                    {assignment.date_basis}
                  </Typography>
                )}
                {assignment.status === 'Open' && can('asset_custody_manage') && (
                  <Button size="small" href="/transfer">Take Back</Button>
                )}
                {assignment.status === 'Open' && can('transfer_request') && (
                  <Button size="small" href="/transfer/create">Request Transfer</Button>
                )}
                {assignment.closure_reason === 'Take Back' && (
                  <Typography variant="caption" display="block">
                    {`Take Back ${new Date(assignment.closed_at).toLocaleString()} by ${assignment.closed_by_details?.user_name || 'IT'} · Available · Actual condition: ${assignment.return_condition}`}
                    {assignment.return_remarks && ` · ${assignment.return_remarks}`}
                  </Typography>
                )}
                {assignment.closure_reason === 'Transfer' && assignment.superseded_by_transfer && (
                  <Typography variant="caption" display="block">
                    {`Transferred via TRF-${String(assignment.superseded_by_transfer).padStart(5, '0')} ${new Date(assignment.closed_at).toLocaleString()} by ${assignment.closed_by_details?.user_name || 'IT'}`}
                  </Typography>
                )}
                {assignment.source_transfer && (
                  <Typography variant="caption" display="block">
                    {`Received via TRF-${String(assignment.source_transfer).padStart(5, '0')}`}
                  </Typography>
                )}
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Checkout History
            </Typography>
            {history.checkouts.length === 0 && (
              <Typography variant="body2" color="text.secondary">No checkouts.</Typography>)}
            {history.checkouts.map((c) => (
              <Box key={c.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {`${c.classification || 'Unclassified'} Checkout #${c.id}`}
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary">
                  {`${c.user_details?.user_name || 'Unknown holder'} · ${c.provenance === 'Administrative reconstruction' ? 'Recorded' : 'Issued'} ${new Date(c.checkout_date).toLocaleString()}`}
                  {c.approved_by_details && ` by ${c.approved_by_details.user_name}`}
                  {` · Purpose: ${c.purpose || 'Not recorded'}`}
                  {c.expected_return_date && ` · Expected return: ${c.expected_return_date}`}
                </Typography>
                {c.date_basis && (
                  <Typography variant="caption" display="block">{c.date_basis}</Typography>
                )}
                <Chip label={c.status} size="small" />
                {c.closure_reason === 'Superseded' && c.superseded_by_transfer && (
                  <Typography variant="caption" display="block">
                    {`Superseded via TRF-${String(c.superseded_by_transfer).padStart(5, '0')} administratively; no physical Check-in`}
                  </Typography>
                )}
                {c.status === 'Open' && c.classification === 'Temporary' &&
                  can('asset_custody_manage') && (
                  <Button size="small" href="/checkout">Check In</Button>
                )}
                {c.return_date && !c.closed_as_interrupted &&
                  (!c.closure_reason || c.closure_reason === 'Returned') && (
                  <Typography variant="caption" display="block">
                    {`Check-in ${new Date(c.return_date).toLocaleString()} · Actual condition: ${c.return_condition}`}
                    {c.return_remarks && ` · ${c.return_remarks}`}
                  </Typography>
                )}
                {c.closed_as_interrupted && (
                  <Typography variant="caption" display="block">Custody interrupted without Check-in.</Typography>
                )}
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Transfer History
            </Typography>
            {history.transfers.length === 0 && (
              <Typography variant="body2" color="text.secondary">No transfers.</Typography>)}
            {history.transfers.map((t) => (
              <Box key={t.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {(t.previous_owner_details?.user_name || '— none recorded')} → {t.new_owner_details?.user_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {t.transfer_code} — {t.status}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Condition Log
            </Typography>
            {history.condition_logs.length === 0 && (
              <Typography variant="body2" color="text.secondary">No inspections.</Typography>)}
            {history.condition_logs.map((l) => (
              <Box key={l.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {l.condition} — {l.inspector_details?.user_name || 'Unknown'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(l.inspection_date).toLocaleString()} {l.notes && `— ${l.notes}`}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Service History
            </Typography>
            {history.services.length === 0 && (
              <Typography variant="body2" color="text.secondary">No service records.</Typography>)}
            {history.services.map((s) => (
              <Box key={s.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {s.vendor_details?.name} — <Chip label={s.status} size="small" />
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(s.sent_date).toLocaleDateString()}
                  {s.returned_date && ` → ${new Date(s.returned_date).toLocaleDateString()}`}
                  {s.reason && ` — ${s.reason}`}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};

export default AssetDetail;
