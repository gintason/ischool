import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import {
  FaUser,
  FaEnvelope,
  FaPhone,
  FaBook,
  FaClock,
  FaFileUpload,
  FaSpinner,
  FaArrowLeft,
  FaCheckCircle,
} from "react-icons/fa";

const Apply = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    subjects: "",
    availability: "",
    cv: null,
  });

  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "", variant: "success" });
  const [showModal, setShowModal] = useState(true); // Show salary modal on page load

  useEffect(() => {
    if (toast.show && toast.variant === "success") {
      const redirectTimer = setTimeout(() => {
        navigate("/ole_home");
      }, 2500);
      return () => clearTimeout(redirectTimer);
    }
  }, [toast.show, toast.variant, navigate]);

  useEffect(() => {
    if (toast.show) {
      const dismissTimer = setTimeout(() => {
        setToast((prev) => ({ ...prev, show: false }));
      }, 4000);
      return () => clearTimeout(dismissTimer);
    }
  }, [toast.show]);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (
      form.cv &&
      ![
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ].includes(form.cv.type)
    ) {
      setToast({
        show: true,
        message: "Please upload a valid CV file (PDF, DOC, or DOCX).",
        variant: "danger",
      });
      return;
    }

    if (form.cv && form.cv.size > 5 * 1024 * 1024) {
      setToast({
        show: true,
        message: "CV file size must be under 5MB.",
        variant: "danger",
      });
      return;
    }

    setLoading(true);
    const data = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      data.append(key, value);
    });

    try {
      await axios.post("https://ischool-backend.onrender.com/api/teachers/apply/", data, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setToast({
        show: true,
        message: "Application submitted successfully! We will update you via email. Thank you.",
        variant: "success",
      });

      setTimeout(() => {
        setForm({
          full_name: "",
          email: "",
          phone: "",
          subjects: "",
          availability: "",
          cv: null,
        });
      }, 800);
    } catch (err) {
      console.error("❌ Submission error:", err.response ?? err);
      const message = err.response?.data?.error || "Submission failed. Try again.";
      setToast({ show: true, message, variant: "danger" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Salary Notice Modal */}
      {showModal && (
        <>
          <div className="modal show fade d-block" tabIndex="-1" role="dialog">
            <div className="modal-dialog modal-dialog-centered" role="document">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Important Information</h5>
                </div>
                <div className="modal-body">
                  <p>
                    Please note: The salary for teaching is <strong>₦6,200 per hour</strong>.
                    Make sure you are comfortable with this rate before submitting your application.
                  </p>
                </div>
                <div className="modal-footer">
                  <button className="btn btn-primary" onClick={() => setShowModal(false)}>
                    I Understand
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </>
      )}

      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-10 col-lg-8">
            <div className="card shadow border-0 mb-5">
              <div className="card-body p-5 bg-light">
                <h3 className="text-center mb-4 fw-bold">Teacher Application</h3>

                {toast.show && (
                  <div
                    className={`alert alert-${toast.variant} alert-dismissible fade show`}
                    role="alert"
                  >
                    {toast.message}
                    <button
                      type="button"
                      className="btn-close"
                      onClick={() => setToast({ ...toast, show: false })}
                    ></button>
                  </div>
                )}

                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label">
                      <FaUser className="me-2 text-primary" />
                      Full Name
                    </label>
                    <input
                      type="text"
                      name="full_name"
                      className="form-control"
                      value={form.full_name}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">
                      <FaEnvelope className="me-2 text-primary" />
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      value={form.email}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">
                      <FaPhone className="me-2 text-primary" />
                      Phone
                    </label>
                    <input
                      type="text"
                      name="phone"
                      className="form-control"
                      value={form.phone}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">
                      <FaBook className="me-2 text-primary" />
                      Subjects (comma-separated)
                    </label>
                    <input
                      type="text"
                      name="subjects"
                      className="form-control"
                      value={form.subjects}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">
                      <FaClock className="me-2 text-primary" />
                      Availability (e.g. Mon–Fri, 8am–4pm)
                    </label>
                    <textarea
                      name="availability"
                      className="form-control"
                      rows="3"
                      value={form.availability}
                      onChange={handleChange}
                      required
                    ></textarea>
                  </div>

                  <div className="mb-4">
                    <label className="form-label">
                      <FaFileUpload className="me-2 text-primary" />
                      Upload CV (PDF/DOCX)
                    </label>
                    <input
                      type="file"
                      name="cv"
                      className="form-control"
                      accept=".pdf,.doc,.docx"
                      onChange={handleChange}
                      required
                    />
                    {form.cv && (
                      <div className="mt-2">
                        <small className="text-muted d-block">
                          Selected file: {form.cv.name}
                        </small>
                        <a
                          href={URL.createObjectURL(form.cv)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-outline-secondary mt-2"
                        >
                          Preview CV
                        </a>
                      </div>
                    )}
                  </div>

                  <div className="d-grid">
                    <button
                      type="submit"
                      className="btn btn-primary w-100 d-flex align-items-center justify-content-center"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <FaSpinner className="me-2 spin" /> Submitting...
                        </>
                      ) : (
                        <>
                          <FaCheckCircle className="me-2" /> Submit Application
                        </>
                      )}
                    </button>
                  </div>
                </form>

                <div className="text-center mt-4">
                  <Link to="/ole_home" className="text-decoration-none me-3">
                    <FaArrowLeft className="me-1" />
                    Back to Home
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Spinner Animation */}
        <style>{`
          .spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </>
  );
};

export default Apply;
