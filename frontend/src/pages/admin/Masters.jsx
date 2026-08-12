import { useEffect, useState } from 'react';
import {
  Box, Button, IconButton, Paper, Tab, Table, TableBody, TableCell,
  TableHead, TableRow, Tabs, TextField, Typography,
} from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';

const MASTERS = [
  { key: 'department', label: 'Departments', endpoint: '/department/', nameField: 'name', extraField: 'description', extraLabel: 'Description' },
  { key: 'location', label: 'Locations', endpoint: '/location/', nameField: 'name', extraField: 'address', extraLabel: 'Address' },
  { key: 'category', label: 'Categories', endpoint: '/category/', nameField: 'category_name' },
  { key: 'brand', label: 'Brands', endpoint: '/brand/', nameField: 'brand_name' },
  { key: 'model', label: 'Models', endpoint: '/model/', nameField: 'model_name' },
  { key: 'purchase_mode', label: 'Purchase Modes', endpoint: '/purchase_mode/', nameField: 'purchase_mode' },
];

const Masters = () => {
  const [tab, setTab] = useState(0);
  const [rows, setRows] = useState([]);
  const [name, setName] = useState('');
  const [extra, setExtra] = useState('');
  const [message, setMessage] = useState(null);

  const master = MASTERS[tab];

  const load = () => {
    AxiosInstance.get(master.endpoint).then((res) => setRows(res.data));
  };

  // Switching tabs swaps to a different master: drop the previous rows and inputs,
  // then load. Done in one state update so the reset is a single render, not four.
  const selectTab = (next) => {
    setTab(next);
    setRows([]);
    setName('');
    setExtra('');
  };

  useEffect(() => { load(); }, [tab]);

  const add = async (event) => {
    event.preventDefault();
    if (!name.trim()) return;
    const payload = { [master.nameField]: name.trim() };
    if (master.extraField) payload[master.extraField] = extra.trim();
    try {
      await AxiosInstance.post(master.endpoint, payload);
      setName(''); setExtra('');
      setMessage(<MyMessage messageText={`${master.label.slice(0, -1)} added.`} messageColor="green" />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={JSON.stringify(err.response?.data) || 'Failed to add.'} messageColor="red" />);
    }
  };

  const remove = async (row) => {
    try {
      await AxiosInstance.delete(`${master.endpoint}${row.id}/`);
      setMessage(<MyMessage messageText="Item removed." messageColor="green" />);
      load();
    } catch {
      setMessage(<MyMessage
        messageText="Cannot delete: item is in use." messageColor="red" />);
    }
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <TuneIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Master Data
        </Typography>
      </Box>

      {message}

      <Paper sx={{ marginBottom: '16px' }}>
        <Tabs value={tab} onChange={(e, v) => selectTab(v)} variant="scrollable">
          {MASTERS.map((m) => <Tab key={m.key} label={m.label} />)}
        </Tabs>
      </Paper>

      <Paper sx={{ padding: '16px', marginBottom: '16px' }}>
        <form onSubmit={add}>
          <Box sx={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <TextField size="small" label={`New ${master.label.slice(0, -1).toLowerCase()} name`}
              value={name} onChange={(e) => setName(e.target.value)} />
            {master.extraField && (
              <TextField size="small" label={master.extraLabel} sx={{ flexGrow: 1 }}
                value={extra} onChange={(e) => setExtra(e.target.value)} />
            )}
            <Button type="submit" variant="contained">Add</Button>
          </Box>
        </form>
      </Paper>

      <Paper>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
              {master.extraField && <TableCell sx={{ fontWeight: 'bold' }}>{master.extraLabel}</TableCell>}
              <TableCell align="right" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row[master.nameField]}</TableCell>
                {master.extraField && <TableCell>{row[master.extraField] || '-'}</TableCell>}
                <TableCell align="right">
                  <IconButton size="small" color="error" onClick={() => remove(row)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </div>
  );
};

export default Masters;
