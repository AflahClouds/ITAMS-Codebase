import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';

import DashboardIcon from '@mui/icons-material/Dashboard';
import DevicesIcon from '@mui/icons-material/Devices';
import LaptopChromebookIcon from '@mui/icons-material/LaptopChromebook';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import BuildIcon from '@mui/icons-material/Build';
import StorefrontIcon from '@mui/icons-material/Storefront';
import GroupIcon from '@mui/icons-material/Group';
import AssessmentIcon from '@mui/icons-material/Assessment';
import TuneIcon from '@mui/icons-material/Tune';

import { Link, useLocation } from 'react-router';
import { useAuth } from '../../AuthContext';


const Item = ({ to, icon, selected }) => (
  <ListItemButton sx={{ display: 'flex', justifyContent: 'center' }}
    component={Link} to={to} selected={selected}>
    <ListItemIcon sx={{ display: 'flex', justifyContent: 'center' }}>
      {icon}
    </ListItemIcon>
  </ListItemButton>
);


export default function ShortMenu() {

  const location = useLocation()
  const path = location.pathname
  const { can, user } = useAuth();

  return (
    <List
      sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
      component="nav"
      aria-labelledby="nested-list-subheader"
    >
      <Item to="/" icon={<DashboardIcon />} selected={path === '/'} />
      {can('asset_view') && (
        <Item to="/asset" icon={<DevicesIcon />} selected={path.startsWith('/asset')} />
      )}
      {can('asset_view') && (
        <Item to="/checkout" icon={<LaptopChromebookIcon />} selected={path.startsWith('/checkout')} />
      )}
      {can('asset_view') && (
        <Item to="/transfer" icon={<SwapHorizIcon />} selected={path.startsWith('/transfer')} />
      )}
      {can('asset_view') && (
        <Item to="/procurement" icon={<ReceiptLongIcon />} selected={path.startsWith('/procurement')} />
      )}
      {can('asset_view') && (
        <Item to="/service" icon={<BuildIcon />} selected={path.startsWith('/service')} />
      )}
      {can('asset_view') && (
        <Item to="/vendor" icon={<StorefrontIcon />} selected={path.startsWith('/vendor')} />
      )}
      {can('user_management') && (
        <Item to="/user" icon={<GroupIcon />} selected={path.startsWith('/user')} />
      )}
      {can('report_access') && (
        <Item to="/reports" icon={<AssessmentIcon />} selected={path === '/reports'} />
      )}
      {(user?.is_admin || can('settings_access')) && (
        <Item to="/admin/masters" icon={<TuneIcon />} selected={path === '/admin/masters'} />
      )}
    </List>
  );
}
