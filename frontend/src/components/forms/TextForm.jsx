import { useId } from 'react';
import TextField from '@mui/material/TextField';

export default function TextForm({label, value, name, onChange, onBlur, error, helperText}) {

  // Every instance carried the same id copied from the MUI docs ("standard-basic"), so
  // a form with several text fields emitted that id a dozen times over. Duplicate ids
  // break the label/control association a screen reader depends on, and leave a
  // label-based query unable to address one field rather than another.
  //
  // `useId` guarantees uniqueness even when two instances share a name; the name is
  // kept in the id so the markup stays readable, matching SelectForm.
  const uid = useId();
  const fieldId = `${name || 'text'}-${uid}`;

  return (

    <TextField
        id={fieldId}
        sx={{width:'100%'}}
        label={label}
        variant="outlined"
        value={value}
        name={name}
        onChange={onChange}
        onBlur={onBlur}
        error={error}
        helperText={helperText}
        />

    );
}
