import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import CenteredToast from '../../components/CenteredToast';
import backgroundImage from '../../assets/login-bg.png';

const StudentLogin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const navigate = useNavigate();

  const showToastNotification = (message) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    if (username && password) {
      try {
        const response = await fetch("https://ischool.ng/api/users/auth/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
          localStorage.setItem("user_id", data.user_id);
          localStorage.setItem("role", data.role);
          localStorage.setItem("token", data.access);

          showToastNotification("Login successful!");
          setTimeout(() => navigate("/student_dash"), 2000);
        } else {
          // ✅ Handle expired subscription redirection
          if (data.detail === "Your subscription has expired. Please buy slots again to continue.") {
            showToastNotification("Your subscription has expired. Redirecting to slot purchase...");
            setTimeout(() => {
              navigate("/signup");
            }, 3000);
          } else {
            showToastNotification(data.error || data.detail || "Login failed. Please try again.");
          }
        }
      } catch (error) {
        console.error("Login error:", error);
        showToastNotification("An error occurred. Please try again later.");
      }
    } else {
      showToastNotification("Please enter both username and password.");
    }
  };

  return (
    <>
      {showToast && <CenteredToast message={toastMessage} />}
      <div
        className="d-flex align-items-center justify-content-center"
        style={{
          minHeight: "100vh",
          padding: "1rem",
          backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url(${backgroundImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        <div
          className="card shadow-lg p-4 w-100"
          style={{
            maxWidth: "450px",
            borderRadius: "16px",
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(4px)",
          }}
        >
          <div className="text-center mb-4">
            <h3 className="mt-3">Student Login</h3>
            <p className="text-muted">Enter your details to access your dashboard</p>
          </div>
          <form onSubmit={handleLogin}>
            <div className="mb-3">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary w-100">
              Login
            </button>
          </form>
          <div className="text-center mt-3">
            <small className="text-muted">iSchool Ola © {new Date().getFullYear()}</small>
          </div>
        </div>
      </div>
    </>
  );
};

export default StudentLogin;
