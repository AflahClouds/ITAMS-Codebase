import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router';
import { Box, Button, Chip, Grid, IconButton, MenuItem, Paper, Select, TextField, Typography } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../AuthContext';

const CONDITIONS = ["New", "Good", "Average", "Damaged", "Repair Required", "Scrapped"];
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
  const [history, setHistory] = useState({ checkouts: [], transfers: [], condition_logs: [] });
  const [condition, setCondition] = useState('Good');
  const [notes, setNotes] = useState('');
  const [docType, setDocType] = useState('Purchase Invoice');
  const [message, setMessage] = useState(null);
  const imageInput = useRef(null);
  const documentInput = useRef(null);
  const { can } = useAuth();

  const load = () => {
    AxiosInstance.get(`/asset/${id}/`).then((res) => setAsset(res.data));
    AxiosInstance.get(`/asset/${id}/history/`).then((res) => setHistory(res.data));
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
              Assignment & Warranty
            </Typography>
            <Row label="Custodian" value={asset.custodian_details?.user_name} />
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

        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Checkout History
            </Typography>
            {history.checkouts.length === 0 && (
              <Typography variant="body2" color="text.secondary">No checkouts.</Typography>)}
            {history.checkouts.map((c) => (
              <Box key={c.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {c.user_details?.user_name} — <Chip label={c.status} size="small" />
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(c.checkout_date).toLocaleDateString()}
                  {c.return_date && ` → ${new Date(c.return_date).toLocaleDateString()}`}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ padding: '16px' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
              Transfer History
            </Typography>
            {history.transfers.length === 0 && (
              <Typography variant="body2" color="text.secondary">No transfers.</Typography>)}
            {history.transfers.map((t) => (
              <Box key={t.id} sx={{ padding: '6px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Typography variant="body2">
                  {(t.previous_owner_details?.user_name || 'IT Store')} → {t.new_owner_details?.user_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {t.transfer_code} — {t.status}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
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
      </Grid>
    </div>
  );
};

export default AssetDetail;
