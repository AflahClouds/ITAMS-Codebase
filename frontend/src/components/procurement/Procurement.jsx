import { React, useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import CalendarViewMonth from '@mui/icons-material/CalendarViewMonth';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../Axios'

const Procurement = () => {

  const [myData, setMyData] = useState([])

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
        accessorKey: 'vendor_name',
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
        enableRowActions
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            <IconButton color="primary" component={Link} to={`/procurement/edit/${row.original.id}`}>
              <EditIcon/>
            </IconButton>

            <IconButton color="error" component={Link} to={`/procurement/delete/${row.original.id}`}>
              <DeleteIcon/>
            </IconButton>
          </Box>
        )}
      />

    </div>
  )
}

export default Procurement
