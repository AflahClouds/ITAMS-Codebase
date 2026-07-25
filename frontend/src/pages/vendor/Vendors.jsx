import { useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import StorefrontIcon from '@mui/icons-material/Storefront';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../../api/client'
import { useAuth } from '../../AuthContext';

const Vendors = () => {

  const [myData, setMyData] = useState([])
  const { can } = useAuth();

  const GetData = () => {
    AxiosInstance.get('/vendor/').then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const columns = useMemo(
    () => [
      {
        accessorKey: 'name',
        header: 'Vendor Name',
      },
      {
        accessorKey: 'contact_person',
        header: 'Contact Person',
      },
      {
        accessorKey: 'phone',
        header: 'Phone',
      },
      {
        accessorKey: 'email',
        header: 'Email',
      },
    ]
  )

  return (
    <div>

      <Box className={"TopBar"}>
        <StorefrontIcon />
        <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
          Vendors
        </Typography>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={myData}
        enableRowActions
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            {can('settings_access') && (
              <IconButton color="primary" component={Link} to={`/vendor/edit/${row.original.id}`}>
                <EditIcon/>
              </IconButton>
            )}

            {can('settings_access') && (
              <IconButton color="error" component={Link} to={`/vendor/delete/${row.original.id}`}>
                <DeleteIcon/>
              </IconButton>
            )}
          </Box>
        )}
      />

    </div>
  )
}

export default Vendors
