// src/components/AuthForm.js
import { TextField, Button, Box, Typography } from '@mui/material';

const AuthForm = ({ isLogin, formData, handleChange, handleSubmit }) => {
  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        width: 320,
        mx: 'auto',
        mt: 10,
        p: 4,
        borderRadius: 2,
        boxShadow: 3,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
      }}
    >
      <Typography variant="h5" textAlign="center">
        {isLogin ? 'Login' : 'Sign Up'}
      </Typography>

      <TextField
        label="Email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      <TextField
        label="Password"
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        required
      />

      {!isLogin && (
        <TextField
          label="Username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          required
        />
      )}

      <Button variant="contained" type="submit">
        {isLogin ? 'Login' : 'Create Account'}
      </Button>
    </Box>
  );
};

export default AuthForm;
