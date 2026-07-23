import TextField from '@mui/material/TextField';

export default function DescriptionForm({label, rows, value, name, onChange, onBlur}) {
  return (

    <TextField
        id="outlined-multiline-static"
        label={label}
        multiline
        rows={rows}
        value={value}
        name={name}
        onChange={onChange}
        onBlur={onBlur}
    />

  );
}
