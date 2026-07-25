import { useEffect, useState } from 'react';
import { Box, Button, Chip, Paper, Typography } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { Link } from 'react-router';
import AxiosInstance from '../api/client';

const Notifications = () => {
  const [rows, setRows] = useState([]);

  const load = () => {
    AxiosInstance.get('/notification/').then((res) => setRows(res.data));
  };

  useEffect(() => { load(); }, []);

  const markRead = async (id) => {
    await AxiosInstance.post(`/notification/${id}/mark_read/`);
    load();
  };

  const markAll = async () => {
    await AxiosInstance.post('/notification/mark_all_read/');
    load();
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <NotificationsIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Notifications
        </Typography>
        <Button size="small" variant="outlined" onClick={markAll}
          sx={{ marginLeft: 'auto', color: 'white', borderColor: 'white' }}>
          Mark all read
        </Button>
      </Box>

      {rows.length === 0 && (
        <Typography color="text.secondary" sx={{ padding: '20px' }}>
          No notifications yet.
        </Typography>
      )}

      {rows.map((n) => (
        <Paper key={n.id} sx={{
          padding: '12px 16px', marginBottom: '8px', display: 'flex',
          alignItems: 'center', gap: '12px',
          backgroundColor: n.status === 'Unread' ? '#e3f2fd' : 'white',
        }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="body2">
              {n.link ? <Link to={n.link}>{n.message}</Link> : n.message}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date(n.created).toLocaleString()}
            </Typography>
          </Box>
          <Chip label={n.status} size="small"
            color={n.status === 'Unread' ? 'info' : 'default'} />
          {n.status === 'Unread' && (
            <Button size="small" onClick={() => markRead(n.id)}>Mark read</Button>
          )}
        </Paper>
      ))}
    </div>
  );
};

export default Notifications;
