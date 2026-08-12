import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import AxiosInstance from "../../api/client"
import { Box, Typography, Button } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import MyMessage from "../../components/forms/Message";

const ProcurementDelete = () => {
  const MyParameter = useParams()
  const MyId = MyParameter.id
  const navigate = useNavigate()

  const [message, setMessage] = useState([])

  const [myData, setMyData] = useState({
    assets: [],
    vendor_details: null,
    invoice_number: "",
    mode_of_purchase_details: null,
  })

  const GetData = () => {
    AxiosInstance.get(`/procurement/${MyId}/`).then((res) => {
      setMyData(res.data)
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const DeleteRecord = (event) => {
    event.preventDefault()
    AxiosInstance.delete(`/procurement/${MyId}/`).then(() => {
      setMessage(<MyMessage
        messageText={"You successfully deleted the data!"}
        messageColor={"red"}
      />)
      setTimeout(() => {
        navigate('/procurement')
      }, 2000)
    })
  }

  return (
    <div>
        <form onSubmit={DeleteRecord}>

        {message}
        <Box className={"TopBar"}>
          <AddBoxIcon />
          <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
            Are you sure you want to delete this procurement record?
          </Typography>
        </Box>

        <Box className={"TextBox"}>
          <Typography>
            You will be deleting the procurement (Invoice: <strong>{myData.invoice_number}</strong>) from{" "}
            <strong>{myData.vendor_details?.name}</strong>, purchased via{" "}
            {myData.mode_of_purchase_details?.purchase_mode}, covering the assets:{" "}
            <strong>{myData.assets?.map((asset) => asset.asset_id).join(", ")}</strong>
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

export default ProcurementDelete
