import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, CssBaseline, Box, Typography } from '@mui/material';

import Home from './Pages/Home';
import Login from './Pages/Login';
import SignUp from './Pages/SignUp';
import Dashboard from './Pages/Dashboard';

import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <CssBaseline />
        <Box sx={{ minHeight: '100vh', bgcolor: '#f9f9f9', py: 5 }}>
          <Container maxWidth="sm">
            <Typography variant="h4" align="center" gutterBottom>
              Expense Trackerr
            </Typography>

            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/login" element={<Login />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
            </Routes>
          </Container>
        </Box>
      </Router>
    </AuthProvider>
  );
}

export default App;
