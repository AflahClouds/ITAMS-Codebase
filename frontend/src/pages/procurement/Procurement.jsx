import { useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import CalendarViewMonth from '@mui/icons-material/CalendarViewMonth';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../../api/client'
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
    ]
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
        enableRowActions={can('asset_edit') || can('asset_delete')}
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
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
          </Box>
        )}
      />

    </div>
  )
}

export default Procurement
