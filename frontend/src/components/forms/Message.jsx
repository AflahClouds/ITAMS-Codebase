import { Box, Typography } from '@mui/material';

export default function MyMessage({messageText, messageColor}) {
  return (

    <Box
        sx={{
            width: '100%',
            height: '30px',
            color: 'white',
            marginBottom: '20px',
            padding: '20px',
            display: 'flex',
            backgroundColor: messageColor,
            alignItems: 'center',
        }}
    >
        <Typography>
            {messageText}
        </Typography>
    </Box>
  
    );
}
