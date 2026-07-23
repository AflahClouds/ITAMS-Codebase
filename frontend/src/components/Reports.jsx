import { useEffect, useState } from 'react';
import {
  Box, Button, Chip, Paper, Table, TableBody, TableCell, TableHead,
  TableRow, Typography,
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DownloadIcon from '@mui/icons-material/Download';
import AxiosInstance from './Axios';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [current, setCurrent] = useState(null);

  useEffect(() => {
    AxiosInstance.get('/reports/').then((res) => setReports(res.data.reports));
  }, []);

  const openReport = (key) => {
    AxiosInstance.get(`/reports/${key}/`).then((res) => setCurrent(res.data));
  };

  const exportCsv = () => {
    if (!current) return;
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const lines = [current.headers.map(esc).join(',')];
    current.rows.forEach((row) => lines.push(row.map(esc).join(',')));
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${current.key}_report.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportServer = async (fmt) => {
    if (!current) return;
    const res = await AxiosInstance.get(
      `/reports/${current.key}/export/${fmt}/`, { responseType: 'blob' });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${current.key}_report.${fmt === 'pdf' ? 'pdf' : 'xlsx'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <AssessmentIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Report Center
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
        {reports.map((r) => (
          <Chip key={r.key} label={r.title} clickable
            color={current?.key === r.key ? 'primary' : 'default'}
            onClick={() => openReport(r.key)} />
        ))}
      </Box>

      {current && (
        <Paper sx={{ padding: '16px', overflowX: 'auto' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
              {current.title} ({current.rows.length} rows)
            </Typography>
            <Box sx={{ display: 'flex', gap: '8px' }}>
              <Button size="small" variant="outlined" startIcon={<DownloadIcon />}
                onClick={() => exportServer('pdf')}>
                PDF
              </Button>
              <Button size="small" variant="outlined" startIcon={<DownloadIcon />}
                onClick={() => exportServer('excel')}>
                Excel
              </Button>
              <Button size="small" variant="outlined" startIcon={<DownloadIcon />}
                onClick={exportCsv}>
                CSV
              </Button>
            </Box>
          </Box>
          <Table size="small">
            <TableHead>
              <TableRow>
                {current.headers.map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 'bold' }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {current.rows.map((row, i) => (
                <TableRow key={i}>
                  {row.map((cell, j) => <TableCell key={j}>{cell}</TableCell>)}
                </TableRow>
              ))}
              {current.rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={current.headers.length}>
                    <Typography color="text.secondary">No data.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Paper>
      )}
    </div>
  );
};

export default Reports;
