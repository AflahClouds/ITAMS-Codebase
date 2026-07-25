import { useState, useEffect } from "react"
import { useNavigate } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import dayjs from "dayjs"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import SelectForm from "../../components/forms/SelectForm";
import TextForm from "../../components/forms/TextForm";
import DateForm from "../../components/forms/DateForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const SERVICEABLE_STATUSES = ['Available', 'Assigned'];

const ServiceCreate = () => {

  const [assets, setAssets] = useState([])
  const [vendors, setVendors] = useState([])
  const [message, setMessage] = useState([])
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/asset/').then((res) => setAssets(
      res.data.filter((a) => SERVICEABLE_STATUSES.includes(a.status))))
    AxiosInstance.get('/vendor/').then((res) => setVendors(res.data))
  }

  useEffect(() => {
    GetData()
  }, [])

  const validationSchema = yup.object({
    asset: yup.string().required("Please select an asset"),
    vendor: yup.string().required("Please select a vendor"),
  })

  const toDateString = (value) => {
    if (!value) return null;
    const parsedDate = dayjs.isDayjs(value) ? value : dayjs(value);
    return parsedDate.isValid() ? parsedDate.format("YYYY-MM-DD") : null;
  };

  const formik = useFormik({
    initialValues: {
      asset: '',
      vendor: '',
      expected_return_date: null,
      reason: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        expected_return_date: toDateString(values.expected_return_date),
      };
      try {
        await AxiosInstance.post('/service/', payload);
        setMessage(<MyMessage
          messageText={"Asset sent for service. Custodian cleared, status set to Under Repair."}
          messageColor={"green"} />)
        setTimeout(() => { navigate('/service') }, 1500)
      } catch (error) {
        const backendError = error.response?.data || error.message;
        setMessage(<MyMessage
          messageText={typeof backendError === "string" ? backendError : JSON.stringify(backendError)}
          messageColor={"red"} />)
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
            Send Asset for Service
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <SelectForm
              label={"Asset (Available or Assigned only)"}
              options={assets}
              labelKey="asset_id"
              name="asset"
              value={formik.values.asset}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.asset && Boolean(formik.errors.asset)}
              helperText={formik.touched.asset && formik.errors.asset}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Vendor"}
              options={vendors}
              labelKey="name"
              name="vendor"
              value={formik.values.vendor}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.vendor && Boolean(formik.errors.vendor)}
              helperText={formik.touched.vendor && formik.errors.vendor}
            />
          </Box>

          <Box className={"FormArea"}>
            <DateForm
              label="Expected Return Date"
              name="expected_return_date"
              value={formik.values.expected_return_date}
              onChange={(newValue) => formik.setFieldValue("expected_return_date", newValue)}
              onBlur={() => formik.setFieldTouched("expected_return_date", true)}
              error={formik.touched.expected_return_date && Boolean(formik.errors.expected_return_date)}
              helperText={formik.touched.expected_return_date && formik.errors.expected_return_date}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Reason"}
              name="reason"
              value={formik.values.reason}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.reason && Boolean(formik.errors.reason)}
              helperText={formik.touched.reason && formik.errors.reason}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Send for Service
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default ServiceCreate
