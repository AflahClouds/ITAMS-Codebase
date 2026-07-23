import { useEffect, useMemo, useState } from 'react';
import { MaterialReactTable } from 'material-react-table';
import { Box, Typography } from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import AxiosInstance from './Axios';

const Audit = () => {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    AxiosInstance.get('/audit/').then((res) => setRows(res.data));
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

      <MaterialReactTable columns={columns} data={rows} />
    </div>
  );
};

export default Audit;
