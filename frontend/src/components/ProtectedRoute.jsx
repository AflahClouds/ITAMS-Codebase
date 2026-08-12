import { Navigate } from 'react-router';
import { Box, Typography } from '@mui/material';
import { useAuth } from '../auth/useAuth';

const ProtectedRoute = ({ permission, adminOnly = false, children }) => {
  const { user, can } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if ((adminOnly && !user.is_admin) || (permission && !can(permission))) {
    return (
      <Box sx={{ padding: '40px', textAlign: 'center' }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>403 — Access denied</Typography>
        <Typography color="text.secondary">
          You do not have permission to view this page.
        </Typography>
      </Box>
    );
  }
  return children;
};

export default ProtectedRoute;
