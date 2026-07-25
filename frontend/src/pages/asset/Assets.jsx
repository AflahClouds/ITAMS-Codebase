import { useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, Chip, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import CalendarViewMonth from '@mui/icons-material/CalendarViewMonth';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../../api/client'
import { useAuth } from '../../AuthContext';

const STATUS_COLORS = {
  'Available': 'success', 'Assigned': 'info', 'Under Repair': 'warning',
  'In Storage': 'default', 'Sold': 'error', 'Scrapped': 'error', 'Lost': 'error',
};

const Assets = () => {

  const [myData, setMyData] = useState([])
  const { can } = useAuth();

  const GetData = () => {
    AxiosInstance.get('/asset/').then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const columns = useMemo(
    () => [
      {
        accessorKey: 'asset_id',
        header: 'Asset ID',
      },
      {
        accessorKey: 'category_details.category_name',
        header: 'Category',
      },
      {
        accessorKey: 'brand_details.brand_name',
        header: 'Brand',
      },
      {
        accessorKey: 'model_details.model_name',
        header: 'Model',
      },
      {
        accessorKey: 'serial_number',
        header: 'Serial Number',
      },
      {
        accessorKey: 'status',
        header: 'Status',
        Cell: ({ cell }) => (
          <Chip label={cell.getValue()} size="small"
            color={STATUS_COLORS[cell.getValue()] || 'default'} />
        ),
      },
      {
        accessorKey: 'condition',
        header: 'Condition',
      },
      {
        accessorFn: (row) => row.custodian_details?.user_name || '-',
        id: 'custodian',
        header: 'Custodian',
      },
      {
        accessorFn: (row) => row.location_details?.name || '-',
        id: 'location',
        header: 'Location',
      },
    ]
  )

  return (
    <div>

      <Box className={"TopBar"}>
        <CalendarViewMonth />
        <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
          Asset Register
        </Typography>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={myData}
        enableRowActions
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap' }}>
            <IconButton color="default" component={Link} to={`/asset/detail/${row.original.id}`}>
              <VisibilityIcon/>
            </IconButton>

            {can('asset_edit') && (
              <IconButton color="primary" component={Link} to={`/asset/edit/${row.original.id}`}>
                <EditIcon/>
              </IconButton>
            )}

            {can('asset_delete') && (
              <IconButton color="error" component={Link} to={`/asset/delete/${row.original.id}`}>
                <DeleteIcon/>
              </IconButton>
            )}
          </Box>
        )}
      />

    </div>
  )
}

export default Assets
