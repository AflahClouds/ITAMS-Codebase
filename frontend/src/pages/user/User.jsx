import { useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, Chip, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import GroupIcon from '@mui/icons-material/Group';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from '../../api/client'
import { useAuth } from '../../auth/useAuth';

const User = () => {

  const [myData, setMyData] = useState([])
  const { can, user } = useAuth();

  const GetData = () => {
    AxiosInstance.get('/user/').then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const columns = useMemo(
    () => [
      {
        accessorKey: 'user_name',
        header: 'User Name',
      },
      {
        accessorKey: 'emp_id',
        header: 'Emp ID',
      },
      {
        accessorKey: 'email_id',
        header: 'Email ID',
      },
      {
        accessorFn: (row) => row.department_details?.name || '-',
        id: 'department',
        header: 'Department',
      },
      {
        accessorKey: 'designation',
        header: 'Designation',
      },
      {
        accessorFn: (row) => row.role_details?.name || '-',
        id: 'role',
        header: 'Role',
      },
      {
        accessorFn: (row) => row.login_username || '-',
        id: 'login',
        header: 'Login',
      },
      {
        accessorKey: 'status',
        header: 'Status',
        Cell: ({ cell }) => (
          <Chip label={cell.getValue()} size="small"
            color={cell.getValue() === 'Active' ? 'success' : 'default'} />
        ),
      },
    ]
  )

  return (
    <div>

      <Box className={"TopBar"}>
        <GroupIcon />
        <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
          User Table !
        </Typography>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={myData}
        enableRowActions
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            {can('user_management') && (
              <IconButton color="primary" component={Link} to={`/user/edit/${row.original.id}`}>
                <EditIcon/>
              </IconButton>
            )}

            {user?.is_admin && (
              <IconButton color="error" component={Link} to={`/user/delete/${row.original.id}`}>
                <DeleteIcon/>
              </IconButton>
            )}
          </Box>
        )}
      />

    </div>
  )
}

export default User
