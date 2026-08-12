import { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { useFormik } from "formik"
import * as yup from "yup"
import dayjs from "dayjs"
import AxiosInstance from "../../api/client"
import { Box, Typography } from "@mui/material"
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import MultiSelectForm from "../../components/forms/MultiSelectForm";
import DateForm from "../../components/forms/DateForm";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';

const ProcurementEdit = () => {

  const MyParameter = useParams()
  const MyId = MyParameter.id

  const [assets, setAssets] = useState([])
  const [purchase_modes, setPurchaseMode] = useState([])
  const [vendors, setVendors] = useState([])
  const [message, setMessage] = useState([])
  const [myData, setMyData] = useState({
    asset_ids: [],
    mode_of_purchase: '',
    vendor: '',
    purchase_date: null,
    invoice_date: null,
    invoice_number: '',
    po_number: '',
  })
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/purchase_mode/').then((res) => {
      setPurchaseMode(res.data)
    })

    AxiosInstance.get('/vendor/').then((res) => {
      setVendors(res.data)
    })

    AxiosInstance.get(`/procurement/${MyId}/`).then((res) => {
      const linkedAssetIds = (res.data.assets || []).map((asset) => asset.id)
      setMyData({ ...res.data, asset_ids: linkedAssetIds })

      AxiosInstance.get('/asset/').then((assetRes) => {
        setAssets(assetRes.data.filter(
          (asset) => !asset.has_procurement || linkedAssetIds.includes(asset.id)
        ))
      })
    })
  }

  useEffect(() => {
    GetData()
  }, [])

  const validationSchema = yup.object({
    asset_ids: yup
      .array().min(1, "Please select at least one asset").required("Please select at least one asset"),
    mode_of_purchase: yup
      .string().required("Please select a purchase mode"),
    vendor: yup
      .string().required("Please select a vendor"),
  })

  const toDateString = (value) => {
    if (!value) return null;

    const parsedDate = dayjs.isDayjs(value) ? value : dayjs(value);
    return parsedDate.isValid() ? parsedDate.format("YYYY-MM-DD") : null;
  };

  const toNumberOrNull = (value) => {
    if (value === "" || value === null || value === undefined) return null;
    const numberValue = Number(value);
    return Number.isNaN(numberValue) ? null : numberValue;
  };

  const formik = useFormik({
    initialValues: {
      asset_ids: myData.asset_ids,
      mode_of_purchase: myData.mode_of_purchase,
      vendor: myData.vendor,
      purchase_date: myData.purchase_date,
      invoice_date: myData.invoice_date,
      invoice_number: myData.invoice_number,
      po_number: myData.po_number,
    },
    enableReinitialize: true,
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      const payload = {
        ...values,
        mode_of_purchase: toNumberOrNull(values.mode_of_purchase),
        vendor: toNumberOrNull(values.vendor),
        purchase_date: toDateString(values.purchase_date),
        invoice_date: toDateString(values.invoice_date),
        invoice_number: values.invoice_number || "",
        po_number: values.po_number || "",
      };

      try {
        await AxiosInstance.put(`/procurement/${MyId}/`, payload);

        setMessage(
          <MyMessage
            messageText="You successfully updated the data!"
            messageColor="green"
          />
        );

        setTimeout(() => {
          navigate("/procurement");
        }, 2000);

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
    },
  });

  return (
    <div>
      <form onSubmit={formik.handleSubmit}>
        <Box className={"TopBar"}>
          <AddBoxIcon />
          <Typography sx={{marginLeft: "10px", fontWeight: "bold"}} variant="subtitle2">
            Edit Procurement !
          </Typography>
        </Box>

        {message}

        <Box className={"FormBox"}>
          <Box className={"FormArea"}>
            <MultiSelectForm
              label={"Assets"}
              options={assets}
              labelKey="asset_id"
              name="asset_ids"
              value={formik.values.asset_ids}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.asset_ids && Boolean(formik.errors.asset_ids)}
              helperText={formik.touched.asset_ids && formik.errors.asset_ids}
            />
          </Box>

          <Box className={"FormArea"}>
            <SelectForm
              label={"Purchase Mode"}
              options={purchase_modes}
              labelKey="purchase_mode"
              name="mode_of_purchase"
              value={formik.values.mode_of_purchase}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.mode_of_purchase && Boolean(formik.errors.mode_of_purchase)}
              helperText={formik.touched.mode_of_purchase && formik.errors.mode_of_purchase}
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
            <TextForm
              label={"Invoice Number"}
              name="invoice_number"
              value={formik.values.invoice_number}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.invoice_number && Boolean(formik.errors.invoice_number)}
              helperText={formik.touched.invoice_number && formik.errors.invoice_number}
            />
          </Box>

          <Box className={"FormArea"}>
            <TextForm
              label={"PO Number"}
              name="po_number"
              value={formik.values.po_number}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.po_number && Boolean(formik.errors.po_number)}
              helperText={formik.touched.po_number && formik.errors.po_number}
            />
          </Box>

          <Box className={"FormArea"}>
            <DateForm
              label="Purchase Date"
              name="purchase_date"
              value={formik.values.purchase_date}
              onChange={(newValue) => formik.setFieldValue("purchase_date", newValue)}
              onBlur={() => formik.setFieldTouched("purchase_date", true)}
              error={formik.touched.purchase_date && Boolean(formik.errors.purchase_date)}
              helperText={formik.touched.purchase_date && formik.errors.purchase_date}
            />
          </Box>

          <Box className={"FormArea"}>
            <DateForm
              label="Invoice Date"
              name="invoice_date"
              value={formik.values.invoice_date}
              onChange={(newValue) => formik.setFieldValue("invoice_date", newValue)}
              onBlur={() => formik.setFieldTouched("invoice_date", true)}
              error={formik.touched.invoice_date && Boolean(formik.errors.invoice_date)}
              helperText={formik.touched.invoice_date && formik.errors.invoice_date}
            />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Update Procurement
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default ProcurementEdit
