import { useState, useEffect } from "react"
import { useNavigate } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../Axios"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../forms/TextForm";
import SelectForm from "../forms/SelectForm";
import MyMessage from "../forms/Message";
import Button from '@mui/material/Button';

const STATUS_OPTIONS = ["Active", "Disabled"].map((s) => ({ id: s, label: s }));

const UserCreate = () => {

  const [departments, setDepartments] = useState([])
  const [roles, setRoles] = useState([])
  const [message, setMessage] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    AxiosInstance.get('/department/').then((res) => setDepartments(res.data))
    AxiosInstance.get('/role/').then((res) => setRoles(res.data))
  }, [])

  const validationSchema = yup.object({
    user_name: yup
      .string().required("Please enter the user name"),
    emp_id: yup
      .string().required("Please enter the employee id"),
    email_id: yup
      .string().email("Please enter a valid email").required("Please enter the email id"),
    mob_no: yup
      .string().required("Please enter the mobile number"),
    department: yup
      .string().required("Please select a department"),
    role: yup
      .string().required("Please select a role"),
  })

  const formik = useFormik({
    initialValues: {
      user_name: '',
      emp_id: '',
      email_id: '',
      mob_no: '',
      department: '',
      designation: '',
      role: '',
      status: 'Active',
      username: '',
      password: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await AxiosInstance.post('/user/', values);

        setMessage(
          <MyMessage
            messageText="You successfully submitted the data!"
            messageColor="green"
          />
        );

        setTimeout(() => {
          navigate('/user');
        }, 1500);

      } catch (error) {
        const backendError = error.response?.data || error.message;
        setMessage(
          <MyMessage
            messageText={
              typeof backendError === "string"
                ? backendError
                : JSON.stringify(backendError)
            }
            messageColor="red"
          />
        );
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
            Create new User !
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <TextForm
              label={"User Name"}
              name="user_name"
              value={formik.values.user_name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.user_name && Boolean(formik.errors.user_name)}
              helperText={formik.touched.user_name && formik.errors.user_name}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Emp ID"}
              name="emp_id"
              value={formik.values.emp_id}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.emp_id && Boolean(formik.errors.emp_id)}
              helperText={formik.touched.emp_id && formik.errors.emp_id}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Email ID"}
              name="email_id"
              value={formik.values.email_id}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email_id && Boolean(formik.errors.email_id)}
              helperText={formik.touched.email_id && formik.errors.email_id}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Mob No"}
              name="mob_no"
              value={formik.values.mob_no}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.mob_no && Boolean(formik.errors.mob_no)}
              helperText={formik.touched.mob_no && formik.errors.mob_no}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Department"}
              options={departments}
              labelKey="name"
              name="department"
              value={formik.values.department}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.department && Boolean(formik.errors.department)}
              helperText={formik.touched.department && formik.errors.department}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Designation"}
              name="designation"
              value={formik.values.designation}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.designation && Boolean(formik.errors.designation)}
              helperText={formik.touched.designation && formik.errors.designation}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Role"}
              options={roles}
              labelKey="name"
              name="role"
              value={formik.values.role}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.role && Boolean(formik.errors.role)}
              helperText={formik.touched.role && formik.errors.role}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Status"}
              options={STATUS_OPTIONS}
              labelKey="label"
              name="status"
              value={formik.values.status}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.status && Boolean(formik.errors.status)}
              helperText={formik.touched.status && formik.errors.status}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Login Username (optional)"}
              name="username"
              value={formik.values.username}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.username && Boolean(formik.errors.username)}
              helperText={formik.touched.username && formik.errors.username}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Login Password (optional)"}
              name="password"
              value={formik.values.password}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Add User
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default UserCreate
