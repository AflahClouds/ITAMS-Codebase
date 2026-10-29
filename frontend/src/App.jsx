import { Routes, Route } from 'react-router'
import './App.css'
import Navbar from './components/navbar/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import ChangePassword from './pages/ChangePassword'
import Dashboard from './pages/Dashboard'
import Notifications from './pages/Notifications'
import Audit from './pages/Audit'
import Reports from './pages/Reports'
import Settings from './pages/Settings'

// Asset pages
import Assets from './pages/asset/Assets'
import AssetDetail from './pages/asset/Detail'
import AssetCreate from './pages/asset/Create'
import AssetEdit from './pages/asset/Edit'
import AssetDelete from './pages/asset/Delete'

// Checkout / transfer pages
import Checkouts from './pages/checkout/Checkouts'
import CheckoutCreate from './pages/checkout/Create'
import Transfers from './pages/transfer/Transfers'
import TransferCreate from './pages/transfer/Create'

// Procurement pages
import Procurement from './pages/procurement/Procurement'
import ProcurementCreate from './pages/procurement/Create'
import ProcurementEdit from './pages/procurement/Edit'
import ProcurementDelete from './pages/procurement/Delete'

// Vendor pages
import Vendors from './pages/vendor/Vendors'
import VendorCreate from './pages/vendor/Create'
import VendorEdit from './pages/vendor/Edit'
import VendorDelete from './pages/vendor/Delete'

// Service Record pages
import Services from './pages/service/Services'
import ServiceCreate from './pages/service/Create'

// User pages
import User from './pages/user/User'
import UserCreate from './pages/user/Create'
import UserEdit from './pages/user/Edit'
import UserDelete from './pages/user/Delete'

// Admin pages
import Roles from './pages/admin/Roles'
import Masters from './pages/admin/Masters'


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
                <Route path="/checkout/create" element={<ProtectedRoute permission="asset_custody_manage"><CheckoutCreate /></ProtectedRoute>} />

                {/* Transfer Routes */}
                <Route path="/transfer" element={<ProtectedRoute permission="asset_view"><Transfers /></ProtectedRoute>} />
                <Route path="/transfer/assign" element={<ProtectedRoute permission="asset_custody_manage"><TransferCreate /></ProtectedRoute>} />
                <Route path="/transfer/create" element={<ProtectedRoute permission="transfer_request"><TransferCreate /></ProtectedRoute>} />

                {/* Procurement Routes */}
                <Route path="/procurement" element={<ProtectedRoute permission="asset_view"><Procurement /></ProtectedRoute>} />
                <Route path="/procurement/create" element={<ProtectedRoute permission="asset_create"><ProcurementCreate /></ProtectedRoute>} />
                <Route path="/procurement/edit/:id" element={<ProtectedRoute permission="asset_edit"><ProcurementEdit /></ProtectedRoute>} />
                <Route path="/procurement/delete/:id" element={<ProtectedRoute permission="asset_delete"><ProcurementDelete /></ProtectedRoute>} />
                <Route path="/procurement/permanent-delete/:id" element={<ProtectedRoute permission="asset_delete"><ProcurementDelete mode="permanent" /></ProtectedRoute>} />

                {/* Service Record Routes */}
                <Route path="/service" element={<ProtectedRoute permission="asset_view"><Services /></ProtectedRoute>} />
                <Route path="/service/create" element={<ProtectedRoute permission="asset_custody_manage"><ServiceCreate /></ProtectedRoute>} />

                {/* Vendor Routes */}
                <Route path="/vendor" element={<ProtectedRoute permission="asset_view"><Vendors /></ProtectedRoute>} />
                <Route path="/vendor/create" element={<ProtectedRoute permission="settings_access"><VendorCreate /></ProtectedRoute>} />
                <Route path="/vendor/edit/:id" element={<ProtectedRoute permission="settings_access"><VendorEdit /></ProtectedRoute>} />
                <Route path="/vendor/delete/:id" element={<ProtectedRoute permission="settings_access"><VendorDelete /></ProtectedRoute>} />

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
