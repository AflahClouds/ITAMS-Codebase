import { React, useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { useFormik } from "formik";
import * as yup from "yup";
import dayjs from "dayjs";
import AxiosInstance from "../Axios";
import { Box, Typography } from "@mui/material";
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from "../forms/TextForm";
import SelectForm from "../forms/SelectForm";
import MultiSelectForm from "../forms/MultiSelectForm";
import DateForm from "../forms/DateForm";
import MyMessage from "../forms/Message";
import Button from '@mui/material/Button';

const ProcurementCreate = () => {

  const [assets, setAssets] = useState([])
  const [purchase_modes, setPurchaseMode] = useState([])
  const [message, setMessage] = useState([])
  const navigate = useNavigate()

  const GetData = () => {
    AxiosInstance.get('/asset/').then((res) => {
      setAssets(res.data.filter((asset) => !asset.has_procurement))
    })

    AxiosInstance.get('/purchase_mode/').then((res) => {
      setPurchaseMode(res.data)
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
      asset_ids: [],
      mode_of_purchase: '',
      vendor_name: '',
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
        purchase_date: toDateString(values.purchase_date),
        invoice_date: toDateString(values.invoice_date),
        invoice_number: values.invoice_number || "",
        vendor_name: values.vendor_name || "",
        po_number: values.po_number || "",
      };

      try {
        await AxiosInstance.post("/procurement/", payload);

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
            <TextForm
              label={"Vendor Name"}
              name="vendor_name"
              value={formik.values.vendor_name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.vendor_name && Boolean(formik.errors.vendor_name)}
              helperText={formik.touched.vendor_name && formik.errors.vendor_name}
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
            Add Procurement
          </Button>

        </Box>
      </form>
    </div>
  )
}

export default ProcurementCreate
