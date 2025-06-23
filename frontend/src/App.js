import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, CssBaseline, Box, Typography } from '@mui/material';
import Login from './Pages/Login';
import SignUp from './Pages/SignUp';
import Dashboard from './Pages/Dashboard'; // <-- you'll create this page
import { AuthProvider } from './context/AuthContext'; // <-- wrap the app with AuthProvider
import PrivateRoute from './components/PrivateRoute'; // <-- protect private routes

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
