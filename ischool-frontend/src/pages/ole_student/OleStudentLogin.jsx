import React, { useState, useEffect } from "react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { FaEnvelope, FaLock, FaEye, FaEyeSlash } from "react-icons/fa";

const OleStudentLogin = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const baseURL = import.meta.env.VITE_API_BASE_URL || "https://ischool.ng/api";


  // Auto-fill if previously saved
  useEffect(() => {
    const savedEmail = localStorage.getItem("ole_remember_email");
    if (savedEmail) {
      setEmail(savedEmail);
      setRememberMe(true);
    }
  }, []);

  const handleLogin = async (e) => {
  e.preventDefault();
  setError("");
  setLoading(true);

  try {
    const response = await axios.post(`${baseURL}/users/ole-student/login/`, {
      email,
      password,
    });

    console.log("✅ Login response:", response.data);

    const { key } = response.data;

    if (!key) {
      throw new Error("Login response missing key (token)");
    }

    localStorage.setItem("ole_token", key); // ✅ Save correct token

    if (rememberMe) {
      localStorage.setItem("ole_remember_email", email);
    } else {
      localStorage.removeItem("ole_remember_email");
    }

    toast.success("Login successful!", {
      autoClose: 3000,
      onClose: () => {
        window.location.href = "/ole_student/dashboard";
      },
    });
  } catch (err) {
    console.error("❌ Login error response:", err.response?.data || err.message);
    const message =
      err.response?.data?.non_field_errors?.[0] ||
      err.response?.data?.detail ||
      err.response?.data?.error ||
      "Login failed";
    setError(message);
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="container py-5 mt-3">
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow-lg border-0 mb-5 mt-5 pt-5">
            <div className="card-body p-4 bg-light">
              <div className="text-center mb-4">
    
                <h3 className="fw-bold">Ole Student Login</h3>
              </div>

              {error && (
                <div className="alert alert-danger text-center">{error}</div>
              )}

              <form onSubmit={handleLogin}>
                <div className="mb-3">
                  <div className="input-group">
                    <span className="input-group-text">
                      <FaEnvelope />
                    </span>
                    <input
                      type="email"
                      placeholder="Email"
                      className="form-control"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <div className="input-group">
                    <span className="input-group-text">
                      <FaLock />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="Password"
                      className="form-control"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={() => setShowPassword(!showPassword)}
                      tabIndex={-1}
                    >
                      {showPassword ? <FaEyeSlash /> : <FaEye />}
                    </button>
                  </div>
                </div>

                <div className="form-check mb-3">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="rememberMe"
                    checked={rememberMe}
                    onChange={() => setRememberMe(!rememberMe)}
                  />
                  <label className="form-check-label" htmlFor="rememberMe">
                    Remember Me
                  </label>
                </div>

                <div className="d-grid mb-3">
                  <button
                    className="btn btn-primary btn-lg"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? "Logging in..." : "Login"}
                  </button>
                </div>

                <div className="text-center mb-2">
                  <a href="#" className="text-decoration-none">
                    Forgot Password?
                  </a>
                </div>

                <div className="text-center">
                  <span>Don’t have an account? </span>
                  <a href="/ole_student/register" className="fw-bold">
                    Register Now
                  </a>
                </div>
              </form>
            </div>
          </div>
          <ToastContainer position="top-center" />
        </div>
      </div>
    </div>
  );
};

export default OleStudentLogin;
