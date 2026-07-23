import dayjs from "dayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";

export default function DateForm({
  label,
  value,
  name,
  onChange,
  onBlur,
  error,
  helperText,
}) {

  const pickerValue = value ? dayjs(value) : null;

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DatePicker
        label={label}
        value={pickerValue}
        onChange={onChange}
        format="YYYY-MM-DD"
        slotProps={{
          textField: {
            name,
            fullWidth: true,
            onBlur,
            error: Boolean(error),
            helperText,
          },
        }}
      />
    </LocalizationProvider>
  );
}
