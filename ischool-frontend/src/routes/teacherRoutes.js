// src/routes/teacherRoutes.js
import { Routes, Route } from "react-router-dom";
import Apply from "../../Pages/teacher/Apply";
import TeacherDashboard from "../Pages/teacher/Dashboard";
import ProtectedRoute from "./ProtectedRoute"; // Optional role check

const TeacherRoutes = () => {
  return (
    <Routes>
      <Route path="/teacher/apply" element={<Apply />} />
      <Route
        path="/teacher/dashboard"
        element={
          <ProtectedRoute role="teacher">
            <TeacherDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

export default TeacherRoutes;
