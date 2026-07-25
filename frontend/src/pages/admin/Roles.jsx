import { useEffect, useState } from 'react';
import {
  Box, Button, Checkbox, Paper, Table, TableBody, TableCell, TableHead,
  TableRow, TextField, Typography,
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import AxiosInstance from '../../api/client';
import MyMessage from '../../components/forms/Message';

const Roles = () => {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [matrix, setMatrix] = useState({});
  const [newRole, setNewRole] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [message, setMessage] = useState(null);

  const load = () => {
    AxiosInstance.get('/role/').then((res) => {
      setRoles(res.data);
      const m = {};
      res.data.forEach((role) => {
        m[role.id] = new Set(role.permissions.map((p) => p.code));
      });
      setMatrix(m);
    });
    AxiosInstance.get('/permission/').then((res) => setPermissions(res.data));
  };

  useEffect(() => { load(); }, []);

  const toggle = (roleId, code) => {
    setMatrix((prev) => {
      const next = { ...prev };
      const set = new Set(next[roleId]);
      if (set.has(code)) set.delete(code); else set.add(code);
      next[roleId] = set;
      return next;
    });
  };

  const saveRole = async (role) => {
    try {
      await AxiosInstance.patch(`/role/${role.id}/`, {
        permission_codes: Array.from(matrix[role.id] || []),
      });
      setMessage(<MyMessage messageText={`Permissions updated for '${role.name}'.`} messageColor="green" />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || 'Failed to update role.'} messageColor="red" />);
    }
  };

  const createRole = async (event) => {
    event.preventDefault();
    if (!newRole.trim()) return;
    try {
      await AxiosInstance.post('/role/', { name: newRole.trim(), description: newDesc.trim() });
      setNewRole(''); setNewDesc('');
      setMessage(<MyMessage messageText="Role created." messageColor="green" />);
      load();
    } catch (err) {
      setMessage(<MyMessage
        messageText={JSON.stringify(err.response?.data) || 'Failed to create role.'} messageColor="red" />);
    }
  };

  return (
    <div>
      <Box className={'TopBar'}>
        <AdminPanelSettingsIcon />
        <Typography sx={{ marginLeft: '10px', fontWeight: 'bold' }} variant="subtitle2">
          Roles & Permissions
        </Typography>
      </Box>

      {message}

      <Paper sx={{ padding: '16px', marginBottom: '16px' }}>
        <form onSubmit={createRole}>
          <Box sx={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <TextField size="small" label="New role name"
              value={newRole} onChange={(e) => setNewRole(e.target.value)} />
            <TextField size="small" label="Description" sx={{ flexGrow: 1 }}
              value={newDesc} onChange={(e) => setNewDesc(e.target.value)} />
            <Button type="submit" variant="contained">Add Role</Button>
          </Box>
        </form>
      </Paper>

      <Paper sx={{ overflowX: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Permission</TableCell>
              {roles.map((role) => (
                <TableCell key={role.id} align="center" sx={{ fontWeight: 'bold' }}>
                  {role.name}
                  <Typography variant="caption" display="block" color="text.secondary">
                    {role.user_count} user(s)
                  </Typography>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {permissions.map((perm) => (
              <TableRow key={perm.id}>
                <TableCell>{perm.name} <Typography variant="caption" color="text.secondary">({perm.code})</Typography></TableCell>
                {roles.map((role) => (
                  <TableCell key={role.id} align="center">
                    <Checkbox size="small"
                      checked={role.name === 'Admin' || Boolean(matrix[role.id]?.has(perm.code))}
                      disabled={role.name === 'Admin'}
                      onChange={() => toggle(role.id, perm.code)} />
                  </TableCell>
                ))}
              </TableRow>
            ))}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Save</TableCell>
              {roles.map((role) => (
                <TableCell key={role.id} align="center">
                  {role.name !== 'Admin' && (
                    <Button size="small" variant="outlined" onClick={() => saveRole(role)}>
                      Save
                    </Button>
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableBody>
        </Table>
      </Paper>
    </div>
  );
};

export default Roles;
