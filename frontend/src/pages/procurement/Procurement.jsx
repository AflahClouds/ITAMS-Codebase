import { useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import CalendarViewMonth from '@mui/icons-material/CalendarViewMonth';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import DownloadIcon from '@mui/icons-material/Download';
import AxiosInstance from '../../api/client'
import { downloadProtectedFile } from '../../api/downloadProtectedFile';
import { useAuth } from '../../auth/useAuth';

const Procurement = () => {

  const [myData, setMyData] = useState([])
  // B6 ALR-008: a control offering an action the reader may not take is a broken
  // promise — the backend refuses it, and the operator learns that only by clicking.
  // Hiding it is presentation, not authorization; the backend check remains the
  // decision (finding OBS-AS-014).
  const { can } = useAuth()

  const GetData = () => {
    AxiosInstance.get('/procurement/').then((res) => {
      setMyData(res.data)
    })
  }

  const downloadInvoice = async (invoice) => {
    try {
      await downloadProtectedFile(invoice.download_url, invoice.file_name);
    } catch {
      window.alert('The purchase invoice could not be downloaded.');
    }
  }

  useEffect(() => {
    GetData()
  }, [])

  const columns = useMemo(
    () => [
      {
        accessorFn: (row) => (row.assets || []).map((asset) => asset.asset_id).join(', '),
        id: 'assets',
        header: 'Assets',
      },
      {
        accessorKey: 'mode_of_purchase_details.purchase_mode',
        header: 'Purchase Mode',
      },
      {
        accessorKey: 'vendor_details.name',
        header: 'Vendor Name',
      },
      {
        accessorKey: 'purchase_date',
        header: 'Purchase Date',
      },
      {
        accessorKey: 'invoice_number',
        header: 'Invoice Number',
      },
      {
        accessorKey: 'po_number',
        header: 'PO Number',
      },
    ],
    []
  )

  return (
    <div>

      <Box className={"TopBar"}>
        <CalendarViewMonth />
        <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
          Procurement Table !
        </Typography>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={myData}
        enableRowActions={can('asset_edit') || can('asset_delete') ||
                          myData.some((procurement) => procurement.current_invoice)}
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            {row.original.current_invoice && (
              <IconButton color="primary" aria-label="Download purchase invoice"
                          onClick={() => downloadInvoice(row.original.current_invoice)}>
                <DownloadIcon/>
              </IconButton>
            )}

            {can('asset_edit') && (
              <IconButton color="primary" aria-label="Edit procurement"
                          component={Link} to={`/procurement/edit/${row.original.id}`}>
                <EditIcon/>
              </IconButton>
            )}

            {can('asset_delete') && (
              <IconButton color="error" aria-label="Archive procurement"
                          component={Link} to={`/procurement/delete/${row.original.id}`}>
                <DeleteIcon/>
              </IconButton>
            )}
            {can('asset_delete') && row.original.assets?.length === 1 && (
              <IconButton color="error" aria-label="Permanently delete procurement"
                          component={Link} to={`/procurement/permanent-delete/${row.original.id}`}>
                <DeleteForeverIcon />
              </IconButton>
            )}
          </Box>
        )}
      />

    </div>
  )
}

export default Procurement
