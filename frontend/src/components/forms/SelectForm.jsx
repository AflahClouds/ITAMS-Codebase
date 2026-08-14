import { useId } from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import FormHelperText from '@mui/material/FormHelperText';

export default function SelectForm({label, options, labelKey, value, name, onChange, onBlur, error, helperText}) {

  // Every instance carried the same ids copied from the MUI docs
  // ("demo-simple-select-label"), so a page with two selects emitted duplicate ids and
  // the label pointed at whichever control the browser found first. That breaks the
  // label/control association a screen reader relies on, and it is why a label-based
  // query in a test matches wrappers rather than controls.
  //
  // `useId` guarantees uniqueness even when two instances share a name; the name is
  // kept in the id so the markup stays readable, matching MultiSelectForm.
  const uid = useId();
  const selectId = `${name || 'select'}-${uid}`;
  const labelId = `${selectId}-label`;

  return (
    <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id={labelId}>{label}</InputLabel>
        <Select
          labelId={labelId}
          id={selectId}
          label={label}
          value={value}
          name={name}
          onChange={onChange}
          onBlur={onBlur}
          error={error}
        >
          {options.map((option) => (
            <MenuItem key={option.id} value={option.id}>
              {option[labelKey]}
            </MenuItem>
          ))}
        </Select>
        <FormHelperText error>{helperText}</FormHelperText>
      </FormControl>
    </Box>
  );
}
