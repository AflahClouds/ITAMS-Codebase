import Box from '@mui/material/Box';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import FormHelperText from '@mui/material/FormHelperText';
import Chip from '@mui/material/Chip';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  slotProps: {
    paper: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  },
};

export default function MultiSelectForm({label, options, labelKey, value, name, onChange, onBlur, error, helperText}) {

  return (
    <div>
      <FormControl sx={{ width:'100%' }} error={error}>
        <InputLabel id={`${name}-multiple-chip-label`}>{label}</InputLabel>
        <Select
          labelId={`${name}-multiple-chip-label`}
          id={`${name}-multiple-chip`}
          multiple
          value={value}
          name={name}
          onChange={onChange}
          onBlur={onBlur}
          error={error}
          input={<OutlinedInput id={`${name}-select-multiple-chip`} label={label} />}
          renderValue={(selected) => (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {selected.map((selectedValue) => (
                <Chip
                  key={selectedValue}
                  label={options.find((option) => option.id === selectedValue)?.[labelKey]}
                />
              ))}
            </Box>
          )}
          MenuProps={MenuProps}
        >
          {options.map((option) => (
            <MenuItem
              key={option.id}
              value={option.id}
            >
              {option[labelKey]}
            </MenuItem>
          ))}
        </Select>
        <FormHelperText>{helperText}</FormHelperText>
      </FormControl>
    </div>
  );
}
