import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useFormik } from "formik";
import * as yup from "yup";
import dayjs from "dayjs";
import AxiosInstance from "../../api/client";
import { Box, Typography } from "@mui/material";
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../../components/forms/TextForm";
import SelectForm from "../../components/forms/SelectForm";
import MultiSelectForm from "../../components/forms/MultiSelectForm";
import DateForm from "../../components/forms/DateForm";
import ArrivalsForm from "../../components/forms/ArrivalsForm";
import ProcurementInvoiceField from "../../components/forms/ProcurementInvoiceField";
import MyMessage from "../../components/forms/Message";
import Button from '@mui/material/Button';
import { buildProcurementFormData } from './formData';

const ProcurementCreate = () => {

  const [assets, setAssets] = useState([])
  const [purchase_modes, setPurchaseMode] = useState([])
  const [vendors, setVendors] = useState([])
  const [locations, setLocations] = useState([])
  const [message, setMessage] = useState([])
  // Keyed by asset id: { arrived_on, location }. B6 FR-009 requires one per linked
  // asset before the purchase can be saved.
  const [arrivals, setArrivals] = useState({})
  const [attested, setAttested] = useState(false)
  const [attestError, setAttestError] = useState(false)
  const [invoiceFile, setInvoiceFile] = useState(null)
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/asset/').then((res) => {
      setAssets(res.data.filter((asset) => !asset.has_procurement))
    })

    AxiosInstance.get('/purchase_mode/').then((res) => {
      setPurchaseMode(res.data)
    })

    AxiosInstance.get('/vendor/').then((res) => {
      setVendors(res.data)
    })

    AxiosInstance.get('/location/').then((res) => {
      setLocations(res.data)
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

  const handleArrivalChange = (assetId, field, value) => {
    setArrivals((current) => ({
      ...current,
      [assetId]: { ...(current[assetId] || {}), [field]: value },
    }))
  }

  const buildArrivals = (selectedIds) => selectedIds
    .map((assetId) => {
      const arrival = arrivals[assetId] || {}
      return {
        asset: assetId,
        arrived_on: toDateString(arrival.arrived_on),
        location: toNumberOrNull(arrival.location),
      }
    })
    .filter((row) => row.arrived_on && row.location)

  const formik = useFormik({
    initialValues: {
      asset_ids: [],
      mode_of_purchase: '',
      vendor: '',
      purchase_date: null,
      invoice_date: null,
      invoice_number: '',
      po_number: '',
    },
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
        attested: attested,
        arrivals: buildArrivals(values.asset_ids),
      };

      if (!attested) {
        setAttestError(true);
        setSubmitting(false);
        return;
      }
      setAttestError(false);

      try {
        await AxiosInstance.post(
          "/procurement/",
          buildProcurementFormData(payload, invoiceFile),
          { headers: { 'Content-Type': 'multipart/form-data' } },
        );

        setMessage(
          <MyMessage
            messageText="You successfully submitted the data!"
            messageColor="green"
          />
        );

        setTimeout(() => {
          navigate("/procurement");
        }, 2000);

      } catch (error) {
        const backendError = error.response?.data || error.message;
        console.error("Backend validation error:", backendError);

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
            Create new Procurement !
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

          <ArrivalsForm
            assets={assets}
            selectedIds={formik.values.asset_ids}
            locations={locations}
            arrivals={arrivals}
            attested={attested}
            onArrivalChange={handleArrivalChange}
            onAttestChange={(checked) => { setAttested(checked); setAttestError(false); }}
            showAttestError={attestError}
          />

          <Box className={"FormArea"}>
            <ProcurementInvoiceField file={invoiceFile} onChange={setInvoiceFile} />
          </Box>

          <Button
            type="submit"
            sx={{margin:"20px"}}
            variant="contained" fullWidth>
            Add Procurement
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default ProcurementCreate
