import { useId } from 'react';
import TextField from '@mui/material/TextField';

export default function DescriptionForm({label, rows, value, name, onChange, onBlur}) {

  // Same defect as TextForm and SelectForm: the id was the one from the MUI docs
  // ("outlined-multiline-static"), so it repeated wherever more than one of these
  // appeared, or alongside any other field reusing a documentation id.
  const uid = useId();
  const fieldId = `${name || 'description'}-${uid}`;

  return (

    <TextField
        id={fieldId}
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
