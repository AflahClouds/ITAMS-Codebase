import { useState, useEffect } from "react"
import { useNavigate } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import SelectForm from "../../components/forms/SelectForm";
import DescriptionForm from "../../components/forms/DescriptionForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const CONDITION_OPTIONS = ["New", "Good", "Average", "Damaged", "Repair Required"]
  .map((s) => ({ id: s, label: s }));

const TransferCreate = () => {

  const [assets, setAssets] = useState([])
  const [users, setUsers] = useState([])
  const [departments, setDepartments] = useState([])
  const [message, setMessage] = useState([])
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/asset/').then((res) => setAssets(
      res.data.filter((a) => ['Available', 'Assigned'].includes(a.status))))
    AxiosInstance.get('/user/directory/').then((res) => setUsers(res.data))
    AxiosInstance.get('/department/').then((res) => setDepartments(res.data))
  }

  useEffect(() => {
    GetData()
  }, [])

  const validationSchema = yup.object({
    asset: yup.string().required("Please select an asset"),
    new_owner: yup.string().required("Please select the new owner"),
  })

  const formik = useFormik({
    initialValues: {
      asset: '',
      new_owner: '',
      new_department: '',
      condition: '',
      remarks: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        new_department: values.new_department || null,
      };
      try {
        await AxiosInstance.post('/transfer/', payload);
        setMessage(<MyMessage
          messageText={"Transfer request submitted for approval!"}
          messageColor={"green"} />)
        setTimeout(() => { navigate('/transfer') }, 1500)
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
            Request Asset Transfer
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <SelectForm
              label={"Asset"}
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
              label={"New Owner"}
              options={users}
              labelKey="user_name"
              name="new_owner"
              value={formik.values.new_owner}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.new_owner && Boolean(formik.errors.new_owner)}
              helperText={formik.touched.new_owner && formik.errors.new_owner}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"New Department (optional)"}
              options={departments}
              labelKey="name"
              name="new_department"
              value={formik.values.new_department}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.new_department && Boolean(formik.errors.new_department)}
              helperText={formik.touched.new_department && formik.errors.new_department}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Condition"}
              options={CONDITION_OPTIONS}
              labelKey="label"
              name="condition"
              value={formik.values.condition}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.condition && Boolean(formik.errors.condition)}
              helperText={formik.touched.condition && formik.errors.condition}
            />
          </Box>

          <Box className={"FormArea"} sx={{ width: '100%' }}>
            <DescriptionForm
              label={"Remarks"}
              rows={3}
              name="remarks"
              value={formik.values.remarks}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Submit Transfer Request
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default TransferCreate
