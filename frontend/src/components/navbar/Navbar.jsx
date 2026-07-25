import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Badge from '@mui/material/Badge';
import MenuMui from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Menu from './Menu';
import ShortMenu from './ShortMenu';
import logo from '../../assets/CLOUDS-LOGO_3.jpg'

import { IconButton } from '@mui/material';
import MenuOpenIcon from '@mui/icons-material/MenuOpen';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

import { Link, useNavigate } from 'react-router';
import { useAuth } from '../../AuthContext';
import AxiosInstance from '../../api/client';

const drawerWidth = 240;
const shortDrawerWidth = 50;

export default function Navbar({ content }) {

    const [isBigMenu, setIsBigMenu] = useState(false)
    const [unread, setUnread] = useState(0)
    const [anchorEl, setAnchorEl] = useState(null)
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const changeMenu = () => {
        setIsBigMenu(!isBigMenu)
    }

    useEffect(() => {
        if (!user) return;
        const poll = () => {
            AxiosInstance.get('/notification/unread_count/')
                .then((res) => setUnread(res.data.count))
                .catch(() => {});
        };
        poll();
        const timer = setInterval(poll, 30000);
        return () => clearInterval(timer);
    }, [user]);

    const handleLogout = async () => {
        setAnchorEl(null);
        await logout();
        navigate('/login');
    };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton sx={{ color:'white' }}
            onClick={changeMenu}>

            {isBigMenu ? <MenuOpenIcon /> : <MenuIcon />}

          </IconButton>
          <img src={logo} alt="Logo" style={{ width: '40px', marginRight: '10px' }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
            IT Asset Management
          </Typography>

          <Box sx={{ flexGrow: 1 }} />

          <IconButton sx={{ color: 'white' }} component={Link} to="/notifications">
            <Badge badgeContent={unread} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton sx={{ color: 'white' }} onClick={(e) => setAnchorEl(e.currentTarget)}>
            <AccountCircleIcon />
          </IconButton>
          <Typography variant="body2" sx={{ marginLeft: '4px' }}>
            {user?.user_name}
          </Typography>

          <MenuMui anchorEl={anchorEl} open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}>
            <MenuItem disabled>{user?.role || 'No role'}</MenuItem>
            <MenuItem component={Link} to="/change-password"
              onClick={() => setAnchorEl(null)}>
              Change Password
            </MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </MenuMui>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: isBigMenu ? drawerWidth : shortDrawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: isBigMenu ? drawerWidth : shortDrawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
            {isBigMenu ? <Menu /> : <ShortMenu />}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
            {content}
      </Box>
    </Box>
  );
}
