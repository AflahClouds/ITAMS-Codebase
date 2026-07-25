import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const STATUS_OPTIONS = ["Active", "Disabled"].map((s) => ({ id: s, label: s }));

const UserEdit = () => {

  const MyParameter = useParams()
  const MyId = MyParameter.id

  const [departments, setDepartments] = useState([])
  const [roles, setRoles] = useState([])
  const [message, setMessage] = useState([])
  const [myData, setMyData] = useState({
    user_name: "", emp_id: "", email_id: "", mob_no: "",
    department: "", designation: "", role: "", status: "Active",
    login_username: null,
  })
  const navigate = useNavigate()

  useEffect(() => {
    AxiosInstance.get('/department/').then((res) => setDepartments(res.data))
    AxiosInstance.get('/role/').then((res) => setRoles(res.data))
    AxiosInstance.get(`/user/${MyId}/`).then((res) => setMyData(res.data))
  }, [])

  const validationSchema = yup.object({
    user_name: yup
      .string().required("Please enter the user name"),
    emp_id: yup
      .string().required("Please enter the employee id"),
    email_id: yup
      .string().email("Please enter a valid email").required("Please enter the email id"),
  })

  const formik = useFormik({
    initialValues: {
      user_name: myData.user_name,
      emp_id: myData.emp_id,
      email_id: myData.email_id,
      mob_no: myData.mob_no,
      department: myData.department ?? '',
      designation: myData.designation || '',
      role: myData.role ?? '',
      status: myData.status || 'Active',
      username: '',
      password: '',
    },
    enableReinitialize: true,
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        department: values.department || null,
        role: values.role || null,
      };
      try {
        await AxiosInstance.put(`/user/${MyId}/`, payload);

        setMessage(
          <MyMessage
            messageText="You successfully updated the data!"
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
            Edit User ! {myData.login_username && `(login: ${myData.login_username})`}
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
              label={myData.login_username ? "Change Login Username" : "Create Login Username"}
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
              label={"Reset Password (leave blank to keep)"}
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
            Update User
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default UserEdit
