import { useEffect, useState } from 'react';
import { Box, Grid, Paper, Typography, Chip } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import { PieChart } from '@mui/x-charts/PieChart';
import { BarChart } from '@mui/x-charts/BarChart';
import { LineChart } from '@mui/x-charts/LineChart';
import AxiosInstance from '../api/client';

const KpiCard = ({ label, value, color }) => (
  <Paper sx={{ padding: '16px', textAlign: 'center', borderTop: `4px solid ${color}` }}>
    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{value}</Typography>
    <Typography variant="body2" color="text.secondary">{label}</Typography>
  </Paper>
);

const ChartCard = ({ title, children }) => (
  <Paper sx={{ padding: '16px', height: '100%' }}>
    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', marginBottom: '8px' }}>
      {title}
    </Typography>
    {children}
  </Paper>
);

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [charts, setCharts] = useState({});

  useEffect(() => {
    AxiosInstance.get('/dashboard/').then((res) => setData(res.data));
    const names = ['category-distribution', 'status-distribution', 'department-usage',
                   'purchase-trend', 'transfer-trend', 'warranty-timeline', 'amc-timeline'];
    names.forEach((name) => {
      AxiosInstance.get(`/charts/${name}/`).then((res) => {
        setCharts((prev) => ({ ...prev, [name]: res.data }));
      });
    });
  }, []);

  if (!data) return <Typography sx={{ padding: '20px' }}>Loading dashboard...</Typography>;

  const k = data.kpis;
  const pieData = (chart) => (chart?.labels || []).map((label, i) => ({
    id: i, label, value: chart.data[i],
  }));

  return (
    <div>
      <Box className={'TopBar'}>
        <DashboardIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Dashboard
        </Typography>
      </Box>

      <Grid container spacing={2} sx={{ marginBottom: '16px' }}>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Total Assets" value={k.total_assets} color="#1976d2" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Available" value={k.available} color="#2e7d32" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Assigned" value={k.assigned} color="#0288d1" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Under Repair" value={k.repair} color="#ed6c02" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Warranty Expiring (30d)" value={k.expiring} color="#d32f2f" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Open Checkouts" value={k.open_checkouts} color="#7b1fa2" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Pending Transfers" value={k.pending_transfers} color="#c2185b" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Currently In Service" value={k.open_services} color="#5d4037" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="AMC Expiring (30d)" value={k.amc_expiring} color="#f57c00" /></Grid>
        <Grid size={{ xs: 6, sm: 3 }}><KpiCard label="Total Value" value={k.total_value.toLocaleString()} color="#00796b" /></Grid>
      </Grid>

      <Grid container spacing={2} sx={{ marginBottom: '16px' }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Assets by Category">
            <PieChart series={[{ data: pieData(charts['category-distribution']) }]} height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Assets by Status">
            <PieChart series={[{ data: pieData(charts['status-distribution']) }]} height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Warranty Timeline">
            <BarChart
              xAxis={[{ scaleType: 'band', data: charts['warranty-timeline']?.labels || [] }]}
              series={[{ data: charts['warranty-timeline']?.data || [] }]}
              height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Assets by Department">
            <BarChart
              xAxis={[{ scaleType: 'band', data: charts['department-usage']?.labels || [] }]}
              series={[{ data: charts['department-usage']?.data || [] }]}
              height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Purchase Trend (12 months)">
            <LineChart
              xAxis={[{ scaleType: 'point', data: charts['purchase-trend']?.labels || [] }]}
              series={[{ data: charts['purchase-trend']?.data || [], area: true }]}
              height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Transfer Trend (12 months)">
            <LineChart
              xAxis={[{ scaleType: 'point', data: charts['transfer-trend']?.labels || [] }]}
              series={[{ data: charts['transfer-trend']?.data || [] }]}
              height={220} />
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="AMC Timeline">
            <BarChart
              xAxis={[{ scaleType: 'band', data: charts['amc-timeline']?.labels || [] }]}
              series={[{ data: charts['amc-timeline']?.data || [] }]}
              height={220} />
          </ChartCard>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Recent Transfers">
            {data.recent_transfers.length === 0 && (
              <Typography variant="body2" color="text.secondary">No transfers yet.</Typography>)}
            {data.recent_transfers.map((t) => (
              <Box key={t.id} sx={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <Typography variant="body2">
                  {t.asset_details?.asset_id} → {t.new_owner_details?.user_name}
                </Typography>
                <Chip label={t.status} size="small"
                  color={t.status === 'Approved' ? 'success' : t.status === 'Pending' ? 'warning' : 'default'} />
              </Box>
            ))}
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Open Checkouts">
            {data.open_checkouts.length === 0 && (
              <Typography variant="body2" color="text.secondary">No open checkouts.</Typography>)}
            {data.open_checkouts.map((c) => (
              <Box key={c.id} sx={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <Typography variant="body2">
                  {c.asset_details?.asset_id} → {c.user_details?.user_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  due {c.expected_return_date || 'N/A'}
                </Typography>
              </Box>
            ))}
          </ChartCard>
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <ChartCard title="Warranty Expiring Soon">
            {data.expiring_assets.length === 0 && (
              <Typography variant="body2" color="text.secondary">Nothing expiring in 30 days.</Typography>)}
            {data.expiring_assets.map((a) => (
              <Box key={a.id} sx={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <Typography variant="body2">{a.asset_id}</Typography>
                <Typography variant="caption" color="error">{a.warranty_end}</Typography>
              </Box>
            ))}
          </ChartCard>
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;
