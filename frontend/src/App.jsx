import { Routes, Route } from 'react-router'
import './App.css'
import Navbar from './components/navbar/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './components/Login'
import ChangePassword from './components/ChangePassword'
import Dashboard from './components/Dashboard'
import Notifications from './components/Notifications'
import Audit from './components/Audit'
import Reports from './components/Reports'
import Settings from './components/Settings'

// Asset components
import Assets from './components/asset/Assets'
import AssetDetail from './components/asset/Detail'
import AssetCreate from './components/asset/Create'
import AssetEdit from './components/asset/Edit'
import AssetDelete from './components/asset/Delete'

// Checkout / transfer components
import Checkouts from './components/checkout/Checkouts'
import CheckoutCreate from './components/checkout/Create'
import Transfers from './components/transfer/Transfers'
import TransferCreate from './components/transfer/Create'

// Procurement components
import Procurement from './components/procurement/Procurement'
import ProcurementCreate from './components/procurement/Create'
import ProcurementEdit from './components/procurement/Edit'
import ProcurementDelete from './components/procurement/Delete'

// User components
import User from './components/user/User'
import UserCreate from './components/user/Create'
import UserEdit from './components/user/Edit'
import UserDelete from './components/user/Delete'

// Admin components
import Roles from './components/admin/Roles'
import Masters from './components/admin/Masters'


function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route path="*" element={
        <ProtectedRoute>
          <Navbar
            content={
              <Routes>

                <Route path="/" element={<Dashboard />} />
                <Route path="/change-password" element={<ChangePassword />} />
                <Route path="/notifications" element={<Notifications />} />

                {/* Asset Routes */}
                <Route path="/asset" element={<ProtectedRoute permission="asset_view"><Assets /></ProtectedRoute>} />
                <Route path="/asset/detail/:id" element={<ProtectedRoute permission="asset_view"><AssetDetail /></ProtectedRoute>} />
                <Route path="/asset/create" element={<ProtectedRoute permission="asset_create"><AssetCreate /></ProtectedRoute>} />
                <Route path="/asset/edit/:id" element={<ProtectedRoute permission="asset_edit"><AssetEdit /></ProtectedRoute>} />
                <Route path="/asset/delete/:id" element={<ProtectedRoute permission="asset_delete"><AssetDelete /></ProtectedRoute>} />

                {/* Checkout Routes */}
                <Route path="/checkout" element={<ProtectedRoute permission="asset_view"><Checkouts /></ProtectedRoute>} />
                <Route path="/checkout/create" element={<ProtectedRoute permission="asset_transfer"><CheckoutCreate /></ProtectedRoute>} />

                {/* Transfer Routes */}
                <Route path="/transfer" element={<ProtectedRoute permission="asset_view"><Transfers /></ProtectedRoute>} />
                <Route path="/transfer/create" element={<ProtectedRoute permission="transfer_request"><TransferCreate /></ProtectedRoute>} />

                {/* Procurement Routes */}
                <Route path="/procurement" element={<ProtectedRoute permission="asset_view"><Procurement /></ProtectedRoute>} />
                <Route path="/procurement/create" element={<ProtectedRoute permission="asset_create"><ProcurementCreate /></ProtectedRoute>} />
                <Route path="/procurement/edit/:id" element={<ProtectedRoute permission="asset_edit"><ProcurementEdit /></ProtectedRoute>} />
                <Route path="/procurement/delete/:id" element={<ProtectedRoute permission="asset_delete"><ProcurementDelete /></ProtectedRoute>} />

                {/* User Routes */}
                <Route path="/user" element={<ProtectedRoute permission="user_management"><User /></ProtectedRoute>} />
                <Route path="/user/create" element={<ProtectedRoute permission="user_management"><UserCreate /></ProtectedRoute>} />
                <Route path="/user/edit/:id" element={<ProtectedRoute permission="user_management"><UserEdit /></ProtectedRoute>} />
                <Route path="/user/delete/:id" element={<ProtectedRoute adminOnly><UserDelete /></ProtectedRoute>} />

                {/* Reports / Admin */}
                <Route path="/reports" element={<ProtectedRoute permission="report_access"><Reports /></ProtectedRoute>} />
                <Route path="/audit" element={<ProtectedRoute adminOnly><Audit /></ProtectedRoute>} />
                <Route path="/settings" element={<ProtectedRoute adminOnly><Settings /></ProtectedRoute>} />
                <Route path="/admin/roles" element={<ProtectedRoute adminOnly><Roles /></ProtectedRoute>} />
                <Route path="/admin/masters" element={<ProtectedRoute permission="settings_access"><Masters /></ProtectedRoute>} />

              </Routes>
            }
          />
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default App
