import { React, useEffect, useMemo, useState } from "react"
import { MaterialReactTable } from "material-react-table";
import { Box, IconButton, Typography } from "@mui/material";
import { Link } from "react-router";
import CalendarViewMonth from '@mui/icons-material/CalendarViewMonth';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AxiosInstance from './Axios'

const Home = () => {

  const [myData, setMyData] = useState([])

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
        accessorKey: 'tag_number',
        header: 'Tag Number',
      },
      {
        accessorKey: 'serial_number',
        header: 'Serial Number',
      },
    ]
  )

  return (
    <div>

      <Box className={"TopBar"}>
        <CalendarViewMonth />
        <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
          Asset Table !
        </Typography>
      </Box>

      <MaterialReactTable
        columns={columns}
        data={myData}
        enableRowActions
        renderRowActions={({row}) => (
          <Box sx={{ display: 'flex', flexWrap: 'nowrap', gap: '8px' }}>
            <IconButton color="primary" component={Link} to={`/asset/edit/${row.original.id}`}>
              <EditIcon/>
            </IconButton>

            <IconButton color="error" component={Link} to={`/asset/delete/${row.original.id}`}>
              <DeleteIcon/>
            </IconButton>
          </Box>
        )}
      />

    </div>
  )
}

export default Home
    