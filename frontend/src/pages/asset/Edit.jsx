import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import AxiosInstance from "../../api/client"
import { Box, Typography, Checkbox, FormControlLabel } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import DateForm from "../../components/forms/DateForm";
import DescriptionForm from "../../components/forms/DescriptionForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const CONDITION_OPTIONS = ["New", "Good", "Average", "Damaged", "Repair Required"]
  .map((s) => ({ id: s, label: s }));

const TERMINAL_STATUSES = ["Sold", "Scrapped", "Lost"];
const LIFECYCLE_MANAGED_STATUSES = ["Assigned", "Under Repair"];

// Mirrors the backend's AssetSerializer.validate() transition rule: Assigned/Under Repair
// can only be entered/left via Checkout or Service Record, and terminal statuses are one-way.
const allowedStatusOptions = (currentStatus, hasProcurement) => {
  if (TERMINAL_STATUSES.includes(currentStatus)) {
    return [currentStatus];
  }
  if (LIFECYCLE_MANAGED_STATUSES.includes(currentStatus)) {
    return [currentStatus, ...TERMINAL_STATUSES];
  }
  return [...(hasProcurement || currentStatus === "Available" ? ["Available"] : []), "In Storage", ...TERMINAL_STATUSES];
};

const statusLockNote = (currentStatus) => {
  if (TERMINAL_STATUSES.includes(currentStatus)) {
    return `This asset is ${currentStatus} and its status can no longer be changed.`;
  }
  if (currentStatus === "Assigned") {
    return "To free this asset up, use Check-in on the Checkouts page instead of editing status here.";
  }
  if (currentStatus === "Under Repair") {
    return "To free this asset up, close its Service Record instead of editing status here.";
  }
  return null;
};

const AssetEdit = () => {

  const MyParameter = useParams()
  const MyId = MyParameter.id

  const [categories, setCategory] = useState([])
  const [brands, setBrand] = useState([])
  const [models, setModel] = useState([])
  const [locations, setLocations] = useState([])
  const [vendors, setVendors] = useState([])
  const [message, setMessage] = useState([])
  const [myData, setMyData] = useState({
    asset_id: "", name: "", tag_number: "", serial_number: "",
    category: "", brand: "", model: "", status: "Available", condition: "New",
    location: "", department: "",
    warranty_start: null, warranty_end: null,
    has_amc: false, amc_start: null, amc_end: null,
    purchase_cost: "", depreciation_rate: "", asset_life: "", notes: "",
  })

  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/category/').then((res) => setCategory(res.data))
    AxiosInstance.get('/brand/').then((res) => setBrand(res.data))
    AxiosInstance.get('/model/').then((res) => setModel(res.data))
    AxiosInstance.get('/location/').then((res) => setLocations(res.data))
    AxiosInstance.get('/vendor/').then((res) => setVendors(res.data))
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
      warranty_start: myData.warranty_start,
      warranty_end: myData.warranty_end,
      has_amc: myData.has_amc || false,
      amc_start: myData.amc_start,
      amc_end: myData.amc_end,
      amc_vendor: myData.amc_vendor_current || '',
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
        warranty_start: toDateOrNull(values.warranty_start),
        warranty_end: toDateOrNull(values.warranty_end),
        amc_start: values.has_amc ? toDateOrNull(values.amc_start) : null,
        amc_end: values.has_amc ? toDateOrNull(values.amc_end) : null,
        // B7 FR-032: a dated AMC contract references a managed Vendor. Only an
        // Incomplete contract (the flag set, dates not yet known) may omit one.
        amc_vendor: values.has_amc && values.amc_start && values.amc_end
          ? values.amc_vendor || null
          : null,
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
              options={allowedStatusOptions(myData.status, myData.has_procurement).map((s) => ({ id: s, label: s }))}
              labelKey="label"
              name="status"
              value={formik.values.status}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.status && Boolean(formik.errors.status)}
              helperText={(formik.touched.status && formik.errors.status) || statusLockNote(myData.status)}
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
            <Typography variant="body2">
              Department: {myData.department_details?.name || 'None'} (follows current Custodian)
            </Typography>
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

          <Box className={"FormArea"} sx={{ width: '100%' }}>
            <FormControlLabel
              control={
                <Checkbox
                  name="has_amc"
                  checked={formik.values.has_amc}
                  onChange={formik.handleChange}
                />
              }
              label="This asset has an AMC (Annual Maintenance Contract)"
            />
          </Box>

          {formik.values.has_amc && (
            <>
              <Box className={"FormArea"}>
                <DateForm
                  label="AMC Start"
                  name="amc_start"
                  value={formik.values.amc_start}
                  onChange={(newValue) => formik.setFieldValue("amc_start", newValue)}
                  onBlur={() => formik.setFieldTouched("amc_start", true)}
                  error={formik.touched.amc_start && Boolean(formik.errors.amc_start)}
                  helperText={formik.touched.amc_start && formik.errors.amc_start}
                />
              </Box>

              <Box className={"FormArea"}>
                <DateForm
                  label="AMC End"
                  name="amc_end"
                  value={formik.values.amc_end}
                  onChange={(newValue) => formik.setFieldValue("amc_end", newValue)}
                  onBlur={() => formik.setFieldTouched("amc_end", true)}
                  error={formik.touched.amc_end && Boolean(formik.errors.amc_end)}
                  helperText={formik.touched.amc_end && formik.errors.amc_end}
                />
              </Box>

              <Box className={"FormArea"}>
                <SelectForm
                  label={"AMC Vendor"}
                  options={vendors}
                  labelKey="name"
                  name="amc_vendor"
                  value={formik.values.amc_vendor || ''}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.amc_vendor && Boolean(formik.errors.amc_vendor)}
                  helperText={
                    (formik.touched.amc_vendor && formik.errors.amc_vendor)
                    || "Required once the contract has dates — an AMC is held with someone, and vendor-grouped reporting depends on it."
                  }
                />
              </Box>
            </>
          )}

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

