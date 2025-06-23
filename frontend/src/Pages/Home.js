import React from 'react';
import { Box, Typography, Button, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  return (
    <Box textAlign="center" py={5}>
      <Typography variant="h3" gutterBottom>
        Welcome to Expense Trackerr
      </Typography>
      <Typography variant="body1" gutterBottom>
        Keep track of your expenses, set budgets, and gain control of your finances.
      </Typography>

      <Stack direction="row" spacing={2} justifyContent="center" mt={4}>
        <Button variant="contained" color="primary" onClick={() => navigate('/login')}>
          Log In
        </Button>
        <Button variant="outlined" color="primary" onClick={() => navigate('/signup')}>
          Sign Up
        </Button>
      </Stack>
    </Box>
  );
};

export default Home;
