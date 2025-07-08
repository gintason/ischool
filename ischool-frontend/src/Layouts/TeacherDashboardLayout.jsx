import React from "react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

const TeacherDashboardLayout = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("teacherToken");
    navigate("/teacher/login");
  };

  return (
    <div className="d-flex min-vh-100">
      {/* Sidebar */}
      <aside className="bg-light border-end p-3" style={{ width: "250px" }}>
        <h4>Teacher Panel</h4>
        <ul className="nav flex-column mt-4">
          <li className="nav-item">
            <Link className="nav-link" to="/teacher/dashboard">🏠 Dashboard</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/teacher/apply">📄 Apply</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/teacher/shortlisted">✅ Shortlisted</Link>
          </li>

           <li className="nav-item">
          <Link className="nav-link" to="/teacher/upcoming-classes">📅 Upcoming Classes</Link>
          </li>
         
          <li className="nav-item mt-3">
            <button className="btn btn-outline-danger w-100" onClick={handleLogout}>
              🚪 Logout
            </button>
          </li>
        </ul>
      </aside>

      {/* Main Content */}
      <main className="flex-grow-1 p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default TeacherDashboardLayout;
