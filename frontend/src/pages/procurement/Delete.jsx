import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router';
import { Box, Typography, Button } from '@mui/material';
import AddBoxIcon from '@mui/icons-material/AddBox';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';
import { useAuth } from '../../auth/useAuth';

const rejectionText = (error, fallback) => {
  const rejection = error.response?.data;
  return Array.isArray(rejection) ? rejection.join(' ') : rejection?.detail || fallback;
};

const ProcurementDelete = ({ mode = 'archive' }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { can } = useAuth();
  const permanent = mode === 'permanent';
  const [procurement, setProcurement] = useState(null);
  const [error, setError] = useState('');
  const [archived, setArchived] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    AxiosInstance.get(`/procurement/${id}/`).then((response) => {
      if (active) {
        setProcurement(response.data);
        setError('');
        setArchived(false);
      }
    }).catch((failure) => {
      if (active) setError(rejectionText(failure, 'Could not load Procurement. Reload and try again.'));
    });
    return () => { active = false; };
  }, [id]);

  const current = procurement && String(procurement.id) === id ? procurement : null;
  const allowed = can('asset_delete');
  const singleton = current?.assets?.length === 1;
  const canConfirm = current && allowed && !archived && (!permanent || singleton);

  const confirm = async (event) => {
    event.preventDefault();
    if (!canConfirm || busy) return;
    setBusy(true);
    setError('');
    try {
      if (permanent) {
        await AxiosInstance.post(`/procurement/${id}/permanent-delete/`, {});
        navigate(`/asset/detail/${current.assets[0].id}`);
      } else {
        await AxiosInstance.delete(`/procurement/${id}/`);
        setArchived(true);
        setTimeout(() => navigate('/procurement'), 2000);
      }
    } catch (failure) {
      setError(rejectionText(failure, permanent
        ? 'Permanent deletion failed. Reload and try again.'
        : 'Archive failed. Reload and try again.'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <form onSubmit={confirm}>
        <Box className="TopBar">
          <AddBoxIcon />
          <Typography component="h1" variant="subtitle2" sx={{ marginLeft: '10px', fontWeight: 'bold' }}>
            {permanent ? 'Permanently delete Procurement?' : 'Archive this procurement record?'}
          </Typography>
        </Box>
        {error && <MyMessage messageText={error} messageColor="red" />}
        {archived && <MyMessage
          messageText="Procurement archived. It is no longer in the working list but remains readable."
          messageColor="green" />}
        {!current && !error && <Typography>Loading Procurement...</Typography>}
        {current && <Box className="TextBox">
          <Typography>
            Invoice: <strong>{current.invoice_number}</strong> from{' '}
            <strong>{current.vendor_details?.name}</strong>, purchased via{' '}
            {current.mode_of_purchase_details?.purchase_mode}, covering the assets:{' '}
            <strong>{current.assets?.map((asset) => asset.asset_id).join(', ')}</strong>
          </Typography>
          {permanent ? <>
            <Typography sx={{ marginTop: '15px' }}>
              This purchase, invoice versions and Procurement history will be permanently deleted.
            </Typography>
            {singleton && <Typography>
              The Asset {current.assets[0].asset_id} is retained, unlinked and In Storage. Asset deletion is a separate action.
            </Typography>}
            {!singleton && <Typography color="error" sx={{ marginTop: 2 }}>
              Permanent deletion requires exactly one remaining Asset. Remove other eligible Assets with a reason first.
            </Typography>}
          </> : <Typography sx={{ marginTop: '15px' }}>
            Archive keeps the purchase, invoice versions and history readable. The Assets remain linked.
          </Typography>}
          {!allowed && <Typography color="error">You do not have permission to perform this action.</Typography>}
        </Box>}
        <Box sx={{ marginTop: '30px', display: 'flex', gap: 2 }}>
          {(!permanent || canConfirm) && <Button type="submit" variant="contained"
            color={permanent ? 'error' : 'primary'} disabled={busy || !canConfirm}>
            {permanent ? 'Confirm permanent deletion' : 'Archive'}
          </Button>}
          <Button type="button" disabled={busy} onClick={() => navigate('/procurement')}>Cancel</Button>
        </Box>
      </form>
    </div>
  );
};

export default ProcurementDelete;
