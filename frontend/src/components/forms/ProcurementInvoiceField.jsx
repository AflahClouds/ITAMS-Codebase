import { Box, Button, Typography } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

const ACCEPTED_DOCUMENTS = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.webp';

const ProcurementInvoiceField = ({ file, onChange, currentInvoice = null, error = '' }) => {
  const buttonLabel = currentInvoice ? 'Choose replacement' : 'Choose invoice';

  return (
    <Box>
      <Typography variant="subtitle2">Purchase Invoice (optional)</Typography>
      {currentInvoice && (
        <Typography variant="body2" sx={{ marginTop: '4px' }}>
          Current: {currentInvoice.file_name} — version {currentInvoice.version}
        </Typography>
      )}
      <Button component="label" size="small" variant="outlined"
        startIcon={<UploadFileIcon />} sx={{ marginTop: '8px' }}>
        {buttonLabel}
        <input
          hidden
          type="file"
          aria-label="Choose purchase invoice"
          accept={ACCEPTED_DOCUMENTS}
          onChange={(event) => onChange(event.target.files?.[0] || null)}
        />
      </Button>
      {file && (
        <Typography variant="body2" sx={{ marginTop: '6px' }}>
          Selected: {file.name}
        </Typography>
      )}
      <Typography variant="caption" display="block" color={error ? 'error' : 'text.secondary'}>
        {error || (currentInvoice
          ? 'Leave empty to keep the current invoice. Maximum 25 MB.'
          : 'Accepted documents only. Maximum 25 MB.')}
      </Typography>
    </Box>
  );
};

export default ProcurementInvoiceField;
