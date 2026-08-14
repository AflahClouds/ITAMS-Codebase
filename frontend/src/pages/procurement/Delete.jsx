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
        messageText={"Procurement archived. It is no longer in the working list but remains readable."}
        messageColor={"green"}
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
            Archive this procurement record?
          </Typography>
        </Box>

        <Box className={"TextBox"}>
          <Typography>
            You will be archiving the procurement (Invoice: <strong>{myData.invoice_number}</strong>) from{" "}
            <strong>{myData.vendor_details?.name}</strong>, purchased via{" "}
            {myData.mode_of_purchase_details?.purchase_mode}, covering the assets:{" "}
            <strong>{myData.assets?.map((asset) => asset.asset_id).join(", ")}</strong>
          </Typography>
          <Typography sx={{ marginTop: "15px" }}>
            Purchase records are archived rather than deleted: the invoice, dates,
            vendor, and link history are the evidence that these assets were bought, so
            they stay readable. The assets remain linked to it.
          </Typography>
        </Box>

        <Box sx={{marginTop: "30px"}}>
          <Button
            type="submit"
            variant="contained" fullWidth>
            Archive
          </Button>
        </Box>

        </form>
    </div>
  )
}

export default ProcurementDelete
