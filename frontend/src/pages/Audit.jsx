import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import { Alert, Box, Typography } from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import AxiosInstance from '../api/client';

const Audit = () => {
  const [rows, setRows] = useState([]);
  // The audit view caps its result set. B8 FR-022 forbids showing a truncated audit
  // trail as though it were complete, so the backend reports the cap alongside the
  // rows and this page has to surface it.
  const [limitInfo, setLimitInfo] = useState({ total: 0, omitted: 0, limit: 0 });

  useEffect(() => {
    AxiosInstance.get('/audit/').then((res) => {
      const { results = [], total = 0, omitted = 0, limit = 0 } = res.data ?? {};
      setRows(results);
      setLimitInfo({ total, omitted, limit });
    });
  }, []);

  const columns = useMemo(() => [
    {
      accessorKey: 'date', header: 'Date',
      Cell: ({ cell }) => new Date(cell.getValue()).toLocaleString(),
    },
    { accessorKey: 'username', header: 'User' },
    { accessorKey: 'action', header: 'Action' },
    { accessorKey: 'module', header: 'Module' },
    { accessorKey: 'old_value', header: 'Old Value' },
    { accessorKey: 'new_value', header: 'New Value' },
    { accessorKey: 'ip_address', header: 'IP Address' },
  ], []);

  return (
    <div>
      <Box className={'TopBar'}>
        <HistoryIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Audit Trail
        </Typography>
      </Box>

      {limitInfo.omitted > 0 && (
        <Alert severity="warning" sx={{ marginBottom: '10px' }}>
          Showing the {limitInfo.limit.toLocaleString()} most recent of{' '}
          {limitInfo.total.toLocaleString()} matching events.{' '}
          <strong>{limitInfo.omitted.toLocaleString()} older events are not shown.</strong>{' '}
          Narrow the module or username filter to see them.
        </Alert>
      )}

      <MaterialReactTable columns={columns} data={rows} />
    </div>
  );
};

export default Audit;
