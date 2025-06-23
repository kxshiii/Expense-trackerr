// src/App.js
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, CssBaseline, Box, Typography } from '@mui/material';
import Login from './Pages/Login';
import SignUp from './Pages/SignUp';

function App() {
  return (
    <Router>
      <CssBaseline /> {/* Normalizes browser styles */}
      <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9', py: 5 }}>
        <Container maxWidth="sm">
          <Typography variant="h4" align="center" gutterBottom>
            Expense Trackerr
          </Typography>

          <Routes>
            <Route path="/signup" element={<SignUp />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;
