import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const PrivateRoute = ({ children }) => {
  const { token } = useContext(AuthContext);

  // If token exists, render children; otherwise redirect to login
  return token ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
