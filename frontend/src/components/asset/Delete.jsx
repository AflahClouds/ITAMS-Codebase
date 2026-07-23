import {React, useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import AxiosInstance from "../Axios"
import {Box, Typography, Button} from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import MyMessage from "../forms/Message";

const AssetDelete = () => {
  const MyParameter = useParams()
  const MyId = MyParameter.id
  const navigate = useNavigate()

  const [category, setCategory] = useState([])
  const [brands, setBrand] = useState([])
  const [models, setModel] = useState([])
  const [message, setMessage] = useState([])

  const [myData, setMyData] = useState({
        asset_id: "",
        tag_number: "",
        serial_number: "",
        category: "",
        brand: "",
        model: "",
      })

  console.log("myData:", myData)

  const GetData = () => {
    AxiosInstance.get(`/asset/${MyId}/`).then((res) => {
      setMyData(res.data)
    })

    AxiosInstance.get(`/category/`).then((res) => {
      setCategory(res.data)
    })

    AxiosInstance.get(`/brand/`).then((res) => {
      setBrand(res.data)
    })

    AxiosInstance.get(`/model/`).then((res) => {
      setModel(res.data)
    })
    
  }

  useEffect(() => {
    GetData()
  }, [])

  const DeleteRecord = (event) => {
    event.preventDefault()
    AxiosInstance.delete(`/asset/${MyId}/`).then(() => {
      setMessage(<MyMessage
        messageText={"You successfully deleted the data!"}
        messageColor={"red"}
      />)
      setTimeout(() => {
        navigate('/asset')
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
            Are you sure you want to delete this asset?
          </Typography>
        </Box>

        <Box className={"TextBox"}>
          <Typography>
            You will be deleting the asset: <strong>{myData.asset_id}</strong> from {" "}
            {category.find(c => c.id === myData.category)?.category_name} - {" "}
            {brands.find(b => b.id === myData.brand)?.brand_name} - {" "}
            {models.find(m => m.id === myData.model)?.model_name}
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

export default AssetDelete
    