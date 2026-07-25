import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import AxiosInstance from "../../api/client"
import { Box, Typography, Button } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import MyMessage from "../../components/forms/Message";

const VendorDelete = () => {
  const MyParameter = useParams()
  const MyId = MyParameter.id
  const navigate = useNavigate()

  const [message, setMessage] = useState([])

  const [myData, setMyData] = useState({
    name: "",
  })

  const GetData = () => {
    AxiosInstance.get(`/vendor/${MyId}/`).then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const DeleteRecord = (event) => {
    event.preventDefault()
    AxiosInstance.delete(`/vendor/${MyId}/`).then(() => {
      setMessage(<MyMessage
        messageText={"You successfully deleted the data!"}
        messageColor={"red"}
      />)
      setTimeout(() => {
        navigate('/vendor')
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
            Are you sure you want to delete this vendor?
          </Typography>
        </Box>

        <Box className={"TextBox"}>
          <Typography>
            You will be deleting the vendor: <strong>{myData.name}</strong>
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

export default VendorDelete
