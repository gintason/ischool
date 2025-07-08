import React from "react";
import { Navigate, Outlet } from "react-router-dom";

const TeacherPrivateRoute = () => {
  const token = localStorage.getItem("teacherToken");

  return token ? <Outlet /> : <Navigate to="/teacher/login" replace />;
};

export default TeacherPrivateRoute;
