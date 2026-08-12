import { useState } from 'react';
import { Box, Button, TextField, Typography } from '@mui/material';
import KeyIcon from '@mui/icons-material/Key';
import AxiosInstance from '../api/client';
import MyMessage from '../components/forms/Message';
import { useAuth } from '../auth/useAuth';

const ChangePassword = () => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [message, setMessage] = useState(null);
  const { setToken } = useAuth();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (newPassword !== confirm) {
      setMessage(<MyMessage messageText="New passwords do not match." messageColor="red" />);
      return;
    }
    try {
      const res = await AxiosInstance.post('/auth/change-password/', {
        old_password: oldPassword, new_password: newPassword,
      });
      setToken(res.data.token);
      setMessage(<MyMessage messageText="Password changed successfully!" messageColor="green" />);
      setOldPassword(''); setNewPassword(''); setConfirm('');
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to change password.'}
        messageColor="red" />);
    }
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <KeyIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Change Password
        </Typography>
      </Box>

      {message}

      <form onSubmit={handleSubmit}>
        <Box className={'FormBox'} sx={{ padding: '20px' }}>
          <Box className={'FormArea'}>
            <TextField label="Current Password" type="password" fullWidth
              value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} />
          </Box>
          <Box className={'FormArea'}>
            <TextField label="New Password" type="password" fullWidth
              value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </Box>
          <Box className={'FormArea'}>
            <TextField label="Confirm New Password" type="password" fullWidth
              value={confirm} onChange={(e) => setConfirm(e.target.value)} />
          </Box>
          <Button type="submit" sx={{ margin: '20px' }} variant="contained" fullWidth>
            Change Password
          </Button>
        </Box>
      </form>
    </div>
  );
};

export default ChangePassword;
