import * as React from 'react';
import ListSubheader from '@mui/material/ListSubheader';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';

import DashboardIcon from '@mui/icons-material/Dashboard';
import DevicesIcon from '@mui/icons-material/Devices';
import LaptopChromebookIcon from '@mui/icons-material/LaptopChromebook';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import GroupIcon from '@mui/icons-material/Group';
import ListAltIcon from '@mui/icons-material/ListAlt';
import AddIcon from '@mui/icons-material/Add';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import TuneIcon from '@mui/icons-material/Tune';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';

import { Link, useLocation } from 'react-router';
import { useAuth } from '../../AuthContext';


function Section({ icon, label, to, path, open, onToggle, children }) {
  return (
    <>
      <ListItemButton onClick={onToggle} component={Link} to={to} selected={path === to}>
        <ListItemIcon>{icon}</ListItemIcon>
        <ListItemText primary={label} />
        {children ? (open ? <ExpandLess /> : <ExpandMore />) : null}
      </ListItemButton>
      {children && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>{children}</List>
        </Collapse>
      )}
    </>
  );
}

function SubItem({ icon, label, to, path }) {
  return (
    <ListItemButton sx={{ pl: 4 }} component={Link} to={to} selected={path === to}>
      <ListItemIcon>{icon}</ListItemIcon>
      <ListItemText primary={label} />
    </ListItemButton>
  );
}

export default function Menu() {
  const [assetsOpen, setAssetsOpen] = React.useState(true);
  const [procurementOpen, setProcurementOpen] = React.useState(false);
  const [userOpen, setUserOpen] = React.useState(false);
  const [adminOpen, setAdminOpen] = React.useState(false);

  const location = useLocation()
  const path = location.pathname
  const { can, user } = useAuth();

  return (
    <List
      sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
      component="nav"
      aria-labelledby="nested-list-subheader"
      subheader={
        <ListSubheader component="div" id="nested-list-subheader">
          IT Assets
        </ListSubheader>
      }
    >

      <ListItemButton component={Link} to="/" selected={path === "/"}>
        <ListItemIcon><DashboardIcon /></ListItemIcon>
        <ListItemText primary="Dashboard" />
      </ListItemButton>

      {can('asset_view') && (
        <Section icon={<DevicesIcon />} label="Assets" to="/asset" path={path}
          open={assetsOpen} onToggle={() => setAssetsOpen(!assetsOpen)}>
          <SubItem icon={<ListAltIcon />} label="All Assets" to="/asset" path={path} />
          {can('asset_create') && (
            <SubItem icon={<AddIcon />} label="Add Asset" to="/asset/create" path={path} />
          )}
        </Section>
      )}

      {can('asset_view') && (
        <ListItemButton component={Link} to="/checkout" selected={path.startsWith("/checkout")}>
          <ListItemIcon><LaptopChromebookIcon /></ListItemIcon>
          <ListItemText primary="Checkouts" />
        </ListItemButton>
      )}

      {can('asset_view') && (
        <ListItemButton component={Link} to="/transfer" selected={path.startsWith("/transfer")}>
          <ListItemIcon><SwapHorizIcon /></ListItemIcon>
          <ListItemText primary="Transfers" />
        </ListItemButton>
      )}

      {can('asset_view') && (
        <Section icon={<ReceiptLongIcon />} label="Procurement" to="/procurement" path={path}
          open={procurementOpen} onToggle={() => setProcurementOpen(!procurementOpen)}>
          <SubItem icon={<ListAltIcon />} label="All" to="/procurement" path={path} />
          {can('asset_create') && (
            <SubItem icon={<AddIcon />} label="Create" to="/procurement/create" path={path} />
          )}
        </Section>
      )}

      {can('user_management') && (
        <Section icon={<GroupIcon />} label="Users" to="/user" path={path}
          open={userOpen} onToggle={() => setUserOpen(!userOpen)}>
          <SubItem icon={<ListAltIcon />} label="All" to="/user" path={path} />
          <SubItem icon={<AddIcon />} label="Create" to="/user/create" path={path} />
        </Section>
      )}

      {can('report_access') && (
        <ListItemButton component={Link} to="/reports" selected={path === "/reports"}>
          <ListItemIcon><AssessmentIcon /></ListItemIcon>
          <ListItemText primary="Reports" />
        </ListItemButton>
      )}

      {user?.is_admin && (
        <Section icon={<AdminPanelSettingsIcon />} label="Admin" to="/admin/roles" path={path}
          open={adminOpen} onToggle={() => setAdminOpen(!adminOpen)}>
          <SubItem icon={<AdminPanelSettingsIcon />} label="Roles" to="/admin/roles" path={path} />
          <SubItem icon={<HistoryIcon />} label="Audit Trail" to="/audit" path={path} />
          <SubItem icon={<SettingsIcon />} label="Settings" to="/settings" path={path} />
        </Section>
      )}

      {can('settings_access') && !user?.is_admin && (
        <ListItemButton component={Link} to="/admin/masters" selected={path === "/admin/masters"}>
          <ListItemIcon><TuneIcon /></ListItemIcon>
          <ListItemText primary="Masters" />
        </ListItemButton>
      )}

      {user?.is_admin && (
        <ListItemButton component={Link} to="/admin/masters" selected={path === "/admin/masters"}>
          <ListItemIcon><TuneIcon /></ListItemIcon>
          <ListItemText primary="Masters" />
        </ListItemButton>
      )}

    </List>
  );
}
