import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import AxiosInstance from "../../api/client"
import { Box, Typography, Button } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import MyMessage from "../../components/forms/Message";
import { useAuth } from '../../auth/useAuth';

const ProcurementDelete = () => {
  const MyParameter = useParams()
  const MyId = MyParameter.id
  const navigate = useNavigate()
  const { can } = useAuth()
  const [confirmPermanent, setConfirmPermanent] = useState(false)
  const [busy, setBusy] = useState(false)

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

  const DeleteRecord = async (event) => {
    event.preventDefault()
    setBusy(true)
    try {
      await AxiosInstance.delete(`/procurement/${MyId}/`)
      setMessage(<MyMessage
        messageText={"Procurement archived. It is no longer in the working list but remains readable."}
        messageColor={"green"}
      />)
      setTimeout(() => {
        navigate('/procurement')
      }, 2000)
    } catch (error) {
      setMessage(<MyMessage messageText={error.response?.data?.detail || 'Archive failed. Reload and try again.'} messageColor="red" />)
    } finally {
      setBusy(false)
    }
  }

  const permanentlyDelete = async () => {
    setBusy(true)
    try {
      await AxiosInstance.post(`/procurement/${MyId}/permanent-delete/`, {})
      navigate(`/asset/${myData.assets[0].id}`)
    } catch (error) {
      const rejection = error.response?.data
      setMessage(<MyMessage messageText={Array.isArray(rejection)
        ? rejection.join(' ')
        : rejection?.detail || 'Permanent deletion failed. Reload and try again.'} messageColor="red" />)
    } finally {
      setBusy(false)
    }
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
            Archive keeps the purchase, invoice versions and history readable. The Assets remain linked.
          </Typography>
        </Box>

        <Box sx={{marginTop: "30px"}}>
          <Button
            type="submit"
            disabled={busy || !can('asset_delete')}
            variant="contained" fullWidth>
            Archive
          </Button>
        </Box>

        </form>
        {can('asset_delete') && myData.assets?.length === 1 && <Box sx={{ marginTop: 3 }}>
          {confirmPermanent ? <>
            <Typography>
              Invoice {myData.invoice_number}: its purchase, invoice versions and Procurement history will be permanently deleted.
            </Typography>
            <Typography>The Asset {myData.assets[0].asset_id} is retained, unlinked and In Storage. Asset deletion is a separate action.</Typography>
            <Button color="error" disabled={busy} onClick={permanentlyDelete}>Confirm permanent deletion</Button>
            <Button disabled={busy} onClick={() => setConfirmPermanent(false)}>Cancel</Button>
          </> : <Button color="error" disabled={busy} onClick={() => setConfirmPermanent(true)}>
            Permanently delete Procurement
          </Button>}
        </Box>}
    </div>
  )
}

export default ProcurementDelete
