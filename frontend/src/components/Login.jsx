import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Box, Button, Paper, TextField, Typography, Alert } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useAuth } from '../AuthContext';
import logo from '../assets/CLOUDS-LOGO_3.jpg';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box sx={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', backgroundColor: 'rgb(1,1,75)',
    }}>
      <Paper sx={{ padding: '40px', width: '360px', textAlign: 'center' }}>
        <img src={logo} alt="Logo" style={{ width: '70px', marginBottom: '10px' }} />
        <Typography variant="h6" sx={{ fontWeight: 'bold', marginBottom: '4px' }}>
          IT Asset Management
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ marginBottom: '20px' }}>
          Sign in to continue
        </Typography>

        {error && <Alert severity="error" sx={{ marginBottom: '15px' }}>{error}</Alert>}

        <form onSubmit={handleSubmit}>
          <TextField
            label="Username" fullWidth sx={{ marginBottom: '15px' }}
            value={username} onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <TextField
            label="Password" type="password" fullWidth sx={{ marginBottom: '20px' }}
            value={password} onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit" variant="contained" fullWidth disabled={busy}
            startIcon={<LockOutlinedIcon />}
          >
            {busy ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
      </Paper>
    </Box>
  );
};

export default Login;
