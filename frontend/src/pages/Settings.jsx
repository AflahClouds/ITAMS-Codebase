import { useEffect, useState } from 'react';
import { Box, Button, Paper, TextField, Typography } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import AxiosInstance from '../api/client';
import MyMessage from '../components/forms/Message';

const FIELDS = [
  { key: 'company_name', label: 'Company Name' },
  { key: 'theme_color', label: 'Theme Color (hex)' },
  { key: 'smtp_server', label: 'SMTP Server' },
  { key: 'smtp_port', label: 'SMTP Port' },
  { key: 'smtp_username', label: 'SMTP Username' },
  { key: 'smtp_sender', label: 'SMTP Sender Address' },
];

const Settings = () => {
  const [values, setValues] = useState({});
  const [message, setMessage] = useState(null);

  useEffect(() => {
    AxiosInstance.get('/setting/').then((res) => {
      const map = {};
      res.data.forEach((s) => { map[s.key] = s.value; });
      setValues(map);
    });
  }, []);

  const save = async (event) => {
    event.preventDefault();
    try {
      for (const field of FIELDS) {
        if (values[field.key] !== undefined) {
          await AxiosInstance.post('/setting/', { key: field.key, value: values[field.key] || '' });
        }
      }
      setMessage(<MyMessage messageText="Settings saved." messageColor="green" />);
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to save settings.'}
        messageColor="red" />);
    }
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <SettingsIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Application Settings
        </Typography>
      </Box>

      {message}

      <Paper sx={{ padding: '20px' }}>
        <form onSubmit={save}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
            {FIELDS.map((field) => (
              <Box key={field.key} className={'FormArea'}>
                <TextField fullWidth size="small" label={field.label}
                  value={values[field.key] || ''}
                  onChange={(e) => setValues({ ...values, [field.key]: e.target.value })} />
              </Box>
            ))}
          </Box>
          <Button type="submit" variant="contained" sx={{ margin: '15px' }}>
            Save Settings
          </Button>
        </form>
      </Paper>
    </div>
  );
};

export default Settings;
