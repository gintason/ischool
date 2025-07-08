import React from 'react';
import { Navigate } from 'react-router-dom';

const OleStudentPrivateRoute = ({ children }) => {
  const token = localStorage.getItem("ole_token");
  let user = null;

  try {
    const storedUser = localStorage.getItem("ole_user");
    if (storedUser && storedUser !== "undefined") {
      user = JSON.parse(storedUser);
    }
  } catch (error) {
    console.error("Failed to parse ole_user from localStorage:", error);
    user = null;
  }

  const isOleStudent = token && user?.role === "ole_student";

  return isOleStudent ? children : <Navigate to="/ole_student/dashboard" replace />;
};

export default OleStudentPrivateRoute;
