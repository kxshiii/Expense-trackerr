// src/pages/Dashboard.js
import React, { useContext } from 'react';
import { Button, Container, Typography } from '@mui/material';
import { AuthContext } from '../context/AuthContext';

const Dashboard = () => {
  const { logout } = useContext(AuthContext);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Welcome to your Dashboard!
      </Typography>
      <Button variant="contained" color="secondary" onClick={logout}>
        Logout
      </Button>
    </Container>
  );
};

export default Dashboard;
