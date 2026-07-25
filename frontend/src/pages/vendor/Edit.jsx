import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const VendorEdit = () => {

  const MyParameter = useParams()
  const MyId = MyParameter.id

  const [message, setMessage] = useState([])
  const [myData, setMyData] = useState({
    name: "", contact_person: "", phone: "", email: "",
  })
  const navigate = useNavigate()

  useEffect(() => {
    AxiosInstance.get(`/vendor/${MyId}/`).then((res) => setMyData(res.data))
  }, [])

  const validationSchema = yup.object({
    name: yup
      .string().required("Please enter the vendor name"),
  })

  const formik = useFormik({
    initialValues: {
      name: myData.name,
      contact_person: myData.contact_person || '',
      phone: myData.phone || '',
      email: myData.email || '',
    },
    enableReinitialize: true,
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await AxiosInstance.put(`/vendor/${MyId}/`, values);
        setMessage(<MyMessage
          messageText={"You successfully updated the data!"}
          messageColor={"green"}
        />)
        setTimeout(() => {
          navigate('/vendor')
        }, 1500)
      } catch (error) {
        const backendError = error.response?.data || error.message;
        setMessage(<MyMessage
          messageText={typeof backendError === "string" ? backendError : JSON.stringify(backendError)}
          messageColor={"red"}
        />)
      } finally {
        setSubmitting(false);
      }
    }
  });

  return (
    <div>
      <form onSubmit={formik.handleSubmit}>
        <Box className={"TopBar"}>
          <AddBoxIcon />
          <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
            Edit Vendor !
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <TextForm
              label={"Vendor Name"}
              name="name"
              value={formik.values.name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Contact Person"}
              name="contact_person"
              value={formik.values.contact_person}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.contact_person && Boolean(formik.errors.contact_person)}
              helperText={formik.touched.contact_person && formik.errors.contact_person}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Phone"}
              name="phone"
              value={formik.values.phone}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.phone && Boolean(formik.errors.phone)}
              helperText={formik.touched.phone && formik.errors.phone}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Email"}
              name="email"
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Update Vendor
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default VendorEdit
