import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import DateForm from "../../components/forms/DateForm";
import DescriptionForm from "../../components/forms/DescriptionForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const STATUS_OPTIONS = ["Available", "Assigned", "Under Repair", "In Storage", "Disposed", "Scrapped"]
  .map((s) => ({ id: s, label: s }));
const CONDITION_OPTIONS = ["New", "Good", "Average", "Damaged", "Repair Required", "Scrapped"]
  .map((s) => ({ id: s, label: s }));

const AssetEdit = () => {

  const MyParameter = useParams()
  const MyId = MyParameter.id

  const [categories, setCategory] = useState([])
  const [brands, setBrand] = useState([])
  const [models, setModel] = useState([])
  const [locations, setLocations] = useState([])
  const [departments, setDepartments] = useState([])
  const [users, setUsers] = useState([])
  const [message, setMessage] = useState([])
  const [myData, setMyData] = useState({
    asset_id: "", name: "", tag_number: "", serial_number: "",
    category: "", brand: "", model: "", status: "Available", condition: "New",
    location: "", department: "", custodian: "",
    warranty_start: null, warranty_end: null,
    purchase_cost: "", depreciation_rate: "", asset_life: "", notes: "",
  })

  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/category/').then((res) => setCategory(res.data))
    AxiosInstance.get('/brand/').then((res) => setBrand(res.data))
    AxiosInstance.get('/model/').then((res) => setModel(res.data))
    AxiosInstance.get('/location/').then((res) => setLocations(res.data))
    AxiosInstance.get('/department/').then((res) => setDepartments(res.data))
    AxiosInstance.get('/user/directory/').then((res) => setUsers(res.data))
    AxiosInstance.get(`/asset/${MyId}/`).then((res) => setMyData(res.data))
  }

  useEffect(() => {
    GetData()
  }, [])

  const validationSchema = yup.object({
    asset_id: yup
      .string().required("Please enter the asset id"),
    tag_number: yup
      .number().typeError("Tag number must be a number")
      .required("Please enter the tag number"),
    serial_number: yup
      .string().required("Please enter the device serial number"),
    category: yup
      .string().required("Please select a category"),
    brand: yup
      .string().required("Please select a brand"),
    model: yup
      .string().required("Please select a model"),
    status: yup
      .string().required("Please select a status"),
    condition: yup
      .string().required("Please select a condition"),
    purchase_cost: yup
      .number().typeError("Purchase cost must be a number").nullable(),
    depreciation_rate: yup
      .number().typeError("Depreciation rate must be a number").nullable(),
    asset_life: yup
      .number().typeError("Asset life must be a number").nullable(),
  })

  const toNumberOrNull = (value) => (value === "" || value === null || value === undefined) ? null : Number(value);
  const toIdOrNull = (value) => (value === "" || value === null || value === undefined) ? null : value;
  const toDateOrNull = (value) => {
    if (!value) return null;
    const d = new Date(value);
    return isNaN(d) ? null : d.toISOString().slice(0, 10);
  };

  const formik = useFormik({
    initialValues: {
      asset_id: myData.asset_id,
      name: myData.name || '',
      tag_number: myData.tag_number,
      serial_number: myData.serial_number,
      category: myData.category,
      brand: myData.brand,
      model: myData.model,
      status: myData.status || 'Available',
      condition: myData.condition || 'New',
      location: myData.location ?? '',
      department: myData.department ?? '',
      custodian: myData.custodian ?? '',
      warranty_start: myData.warranty_start,
      warranty_end: myData.warranty_end,
      purchase_cost: myData.purchase_cost ?? '',
      depreciation_rate: myData.depreciation_rate ?? '',
      asset_life: myData.asset_life ?? '',
      notes: myData.notes || '',
    },
    enableReinitialize: true,
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        purchase_cost: toNumberOrNull(values.purchase_cost),
        depreciation_rate: toNumberOrNull(values.depreciation_rate),
        asset_life: toNumberOrNull(values.asset_life),
        location: toIdOrNull(values.location),
        department: toIdOrNull(values.department),
        custodian: toIdOrNull(values.custodian),
        warranty_start: toDateOrNull(values.warranty_start),
        warranty_end: toDateOrNull(values.warranty_end),
      };
      try {
        await AxiosInstance.put(`/asset/${MyId}/`, payload);
        setMessage(<MyMessage
          messageText={"You successfully updated the data!"}
          messageColor={"green"}
        />)
        setTimeout(() => {
          navigate('/asset')
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
            Edit Asset !
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <TextForm
              label={"Asset ID"}
              name="asset_id"
              value={formik.values.asset_id}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.asset_id && Boolean(formik.errors.asset_id)}
              helperText={formik.touched.asset_id && formik.errors.asset_id}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Asset Name"}
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
              label={"Tag Number"}
              name="tag_number"
              value={formik.values.tag_number}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.tag_number && Boolean(formik.errors.tag_number)}
              helperText={formik.touched.tag_number && formik.errors.tag_number}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Serial Number"}
              name="serial_number"
              value={formik.values.serial_number}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.serial_number && Boolean(formik.errors.serial_number)}
              helperText={formik.touched.serial_number && formik.errors.serial_number}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Category"}
              options={categories}
              labelKey="category_name"
              name="category"
              value={formik.values.category}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.category && Boolean(formik.errors.category)}
              helperText={formik.touched.category && formik.errors.category}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Brand"}
              options={brands}
              labelKey="brand_name"
              name="brand"
              value={formik.values.brand}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.brand && Boolean(formik.errors.brand)}
              helperText={formik.touched.brand && formik.errors.brand}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Model"}
              options={models}
              labelKey="model_name"
              name="model"
              value={formik.values.model}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.model && Boolean(formik.errors.model)}
              helperText={formik.touched.model && formik.errors.model}
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

          <Box className={"FormArea"}>
            <SelectForm
              label={"Location"}
              options={locations}
              labelKey="name"
              name="location"
              value={formik.values.location}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.location && Boolean(formik.errors.location)}
              helperText={formik.touched.location && formik.errors.location}
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
            <SelectForm
              label={"Custodian"}
              options={users}
              labelKey="user_name"
              name="custodian"
              value={formik.values.custodian}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.custodian && Boolean(formik.errors.custodian)}
              helperText={formik.touched.custodian && formik.errors.custodian}
            />
          </Box>

          <Box className={"FormArea"}>
            <DateForm
              label="Warranty Start"
              name="warranty_start"
              value={formik.values.warranty_start}
              onChange={(newValue) => formik.setFieldValue("warranty_start", newValue)}
              onBlur={() => formik.setFieldTouched("warranty_start", true)}
              error={formik.touched.warranty_start && Boolean(formik.errors.warranty_start)}
              helperText={formik.touched.warranty_start && formik.errors.warranty_start}
            />
          </Box>

          <Box className={"FormArea"}>
            <DateForm
              label="Warranty End"
              name="warranty_end"
              value={formik.values.warranty_end}
              onChange={(newValue) => formik.setFieldValue("warranty_end", newValue)}
              onBlur={() => formik.setFieldTouched("warranty_end", true)}
              error={formik.touched.warranty_end && Boolean(formik.errors.warranty_end)}
              helperText={formik.touched.warranty_end && formik.errors.warranty_end}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Purchase Cost"}
              name="purchase_cost"
              value={formik.values.purchase_cost}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.purchase_cost && Boolean(formik.errors.purchase_cost)}
              helperText={formik.touched.purchase_cost && formik.errors.purchase_cost}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Depreciation Rate"}
              name="depreciation_rate"
              value={formik.values.depreciation_rate}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.depreciation_rate && Boolean(formik.errors.depreciation_rate)}
              helperText={formik.touched.depreciation_rate && formik.errors.depreciation_rate}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"Asset Life"}
              name="asset_life"
              value={formik.values.asset_life}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.asset_life && Boolean(formik.errors.asset_life)}
              helperText={formik.touched.asset_life && formik.errors.asset_life}
            />
          </Box>

          <Box className={"FormArea"} sx={{ width: '100%' }}>
            <DescriptionForm
              label={"Notes"}
              rows={3}
              name="notes"
              value={formik.values.notes}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Update Asset
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default AssetEdit
