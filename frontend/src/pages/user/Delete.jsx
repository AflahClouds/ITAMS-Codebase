import { React, useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import AxiosInstance from "../../api/client"
import { Box, Typography, Button } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import MyMessage from "../../components/forms/Message";

const UserDelete = () => {
  const MyParameter = useParams()
  const MyId = MyParameter.id
  const navigate = useNavigate()

  const [message, setMessage] = useState([])

  const [myData, setMyData] = useState({
    user_name: "",
    emp_id: "",
    email_id: "",
    mob_no: "",
    department: "",
  })

  const GetData = () => {
    AxiosInstance.get(`/user/${MyId}/`).then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const DeleteRecord = (event) => {
    event.preventDefault()
    AxiosInstance.delete(`/user/${MyId}/`).then(() => {
      setMessage(<MyMessage
        messageText={"You successfully deleted the data!"}
        messageColor={"red"}
      />)
      setTimeout(() => {
        navigate('/user')
      }, 2000)
    }).catch((err) => {
      setMessage(<MyMessage
        messageText={err.response?.data?.detail || "Delete failed."}
        messageColor={"red"}
      />)
    })
  }

  return (
    <div>
        <form onSubmit={DeleteRecord}>

        {message}
        <Box className={"TopBar"}>
          <AddBoxIcon />
          <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
            Are you sure you want to delete this user?
          </Typography>
        </Box>

        <Box className={"TextBox"}>
          <Typography>
            You will be deleting the user: <strong>{myData.user_name}</strong> (Emp ID:{" "}
            <strong>{myData.emp_id}</strong>) from the{" "}
            <strong>{myData.department_details?.name || '-'}</strong> department
          </Typography>
        </Box>

        <Box sx={{marginTop: "30px"}}>
          <Button
            type="submit"
            variant="contained" fullWidth>
            Delete
          </Button>
        </Box>

        </form>
    </div>
  )
}

export default UserDelete
