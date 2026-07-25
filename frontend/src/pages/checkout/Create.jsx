import { useState, useEffect } from "react"
import { useNavigate } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import dayjs from "dayjs"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import DateForm from "../../components/forms/DateForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const CONDITION_OPTIONS = ["New", "Good", "Average", "Damaged", "Repair Required", "Scrapped"]
  .map((s) => ({ id: s, label: s }));

const CheckoutCreate = () => {

  const [assets, setAssets] = useState([])
  const [users, setUsers] = useState([])
  const [message, setMessage] = useState([])
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/asset/?status=Available').then((res) => setAssets(res.data))
    AxiosInstance.get('/user/directory/').then((res) => setUsers(res.data))
  }

  useEffect(() => {
    GetData()
  }, [])

  const validationSchema = yup.object({
    asset: yup.string().required("Please select an asset"),
    user: yup.string().required("Please select a user"),
  })

  const toDateString = (value) => {
    if (!value) return null;
    const parsedDate = dayjs.isDayjs(value) ? value : dayjs(value);
    return parsedDate.isValid() ? parsedDate.format("YYYY-MM-DD") : null;
  };

  const formik = useFormik({
    initialValues: {
      asset: '',
      user: '',
      expected_return_date: null,
      purpose: '',
      checkout_condition: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        expected_return_date: toDateString(values.expected_return_date),
      };
      try {
        await AxiosInstance.post('/checkout/', payload);
        setMessage(<MyMessage
          messageText={"Asset checked out. Usage session started!"}
          messageColor={"green"} />)
        setTimeout(() => { navigate('/checkout') }, 1500)
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
            New Checkout — start a usage session
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <SelectForm
              label={"Asset (available only)"}
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
              label={"User"}
              options={users}
              labelKey="user_name"
              name="user"
              value={formik.values.user}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.user && Boolean(formik.errors.user)}
              helperText={formik.touched.user && formik.errors.user}
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
            <SelectForm
              label={"Checkout Condition"}
              options={CONDITION_OPTIONS}
              labelKey="label"
              name="checkout_condition"
              value={formik.values.checkout_condition}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.checkout_condition && Boolean(formik.errors.checkout_condition)}
              helperText={formik.touched.checkout_condition && formik.errors.checkout_condition}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Purpose"}
              name="purpose"
              value={formik.values.purpose}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.purpose && Boolean(formik.errors.purpose)}
              helperText={formik.touched.purpose && formik.errors.purpose}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Checkout Asset
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default CheckoutCreate
