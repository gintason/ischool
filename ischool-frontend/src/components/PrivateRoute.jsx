import React from 'react';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children }) => {
  const isAuthenticated = !!localStorage.getItem('accessToken');

  return isAuthenticated ? children : <Navigate to="/student_login" replace />;

  
};

export default PrivateRoute;
