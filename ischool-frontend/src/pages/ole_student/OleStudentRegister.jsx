import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
  FaUser,
  FaEnvelope,
  FaClipboardList,
  FaGraduationCap,
  FaBook,
} from 'react-icons/fa';

const OleStudentRegister = () => {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    plan_type: 'monthly',
    class_level_id: '',
    subject_ids: [],
  });

  const [loading, setLoading] = useState(false);
  const [classLevels, setClassLevels] = useState([]);
  const [subjects, setSubjects] = useState([]);

  // ✅ Fetch class levels
  useEffect(() => {
    axios
      .get('https://api.ischool.ng/api/teachers/class-levels/')
      .then((res) => {
        if (Array.isArray(res.data)) {
          setClassLevels(res.data);
        } else {
          setClassLevels([]);
          toast.error("Invalid class level data.");
        }
      })
      .catch(() => toast.error("Failed to load class levels"));
  }, []);

  // ✅ Fetch subjects based on selected class level
  useEffect(() => {
    if (form.class_level_id) {
      axios
        .get(`https://api.ischool.ng/api/teachers/subjects/?class_level_id=${form.class_level_id}`)
        .then((res) => {
          if (Array.isArray(res.data)) {
            setSubjects(res.data);
          } else {
            setSubjects([]);
            toast.error("Subjects data not valid.");
          }
        })
        .catch(() => toast.error("Failed to load subjects"));
    } else {
      setSubjects([]);
    }
  }, [form.class_level_id]);

  // ✅ Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  // ✅ Handle multiple select
  const handleSubjectChange = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions).map((opt) => opt.value);
    setForm((prev) => ({ ...prev, subject_ids: selectedOptions }));
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  if (!form.full_name || !form.email || !form.class_level_id || form.subject_ids.length === 0) {
    toast.error("Please complete all required fields.");
    return;
  }

  setLoading(true);
  console.log("Form data being submitted:", form); // 🧪 Inspect payload

  try {
    const response = await axios.post(
      'https://api.ischool.ng/api/users/ole-student/register/',
      form
    );

    const { authorization_url } = response.data;

    localStorage.setItem("ole_student_email", form.email);
    localStorage.setItem("ole_student_full_name", form.full_name);
    localStorage.setItem("ole_student_plan_type", form.plan_type);

    window.location.href = authorization_url;
  } catch (error) {
    console.error("Registration error:", error.response?.data || error.message);
    const errMsg =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      JSON.stringify(error.response?.data) ||
      "Registration or payment initialization failed.";
    toast.error(errMsg);
  } finally {
    setLoading(false);
  }
};

  // ✅ Payment success listener
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const verified = params.get('payment') === 'success';
    if (verified) {
      toast.success("Payment successful! Check your email for login details.", {
        autoClose: 5000,
        onClose: () => (window.location.href = "/ole-student/login"),
      });
    }
  }, []);

  return (
    <div className="container py-5 mb-5">
      <div className="row justify-content-center">
        <div className="col-lg-8 col-md-10">
          <div className="card shadow-lg border-0 mb-5">
            <div className="card-body p-5 bg-light">
              <h3 className="text-center mb-4 fw-bold">Register for iSchool Ole</h3>

              <form onSubmit={handleSubmit}>
                {/* Full Name */}
                <div className="mb-3">
                  <label className="form-label">Full Name</label>
                  <div className="input-group">
                    <span className="input-group-text"><FaUser /></span>
                    <input
                      type="text"
                      name="full_name"
                      className="form-control"
                      required
                      onChange={handleChange}
                      value={form.full_name}
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="mb-3">
                  <label className="form-label">Email Address</label>
                  <div className="input-group">
                    <span className="input-group-text"><FaEnvelope /></span>
                    <input
                      type="email"
                      name="email"
                      className="form-control"
                      required
                      onChange={handleChange}
                      value={form.email}
                    />
                  </div>
                </div>

                {/* Plan Type */}
                <div className="mb-3">
                  <label className="form-label">Select Plan</label>
                  <div className="input-group">
                    <span className="input-group-text"><FaClipboardList /></span>
                    <select
                      name="plan_type"
                      className="form-select"
                      onChange={handleChange}
                      value={form.plan_type}
                    >
                      <option value="monthly">Monthly Plan (₦100)</option>
              
                    </select>
                  </div>
                </div>

                {/* Class Level */}
                <div className="mb-3">
                  <label className="form-label">Class Level</label>
                  <div className="input-group">
                    <span className="input-group-text"><FaGraduationCap /></span>
                    <select
                      name="class_level_id"
                      className="form-select"
                      required
                      onChange={handleChange}
                      value={form.class_level_id}
                    >
                      <option value="">-- Select Class Level --</option>
                      {Array.isArray(classLevels) &&
                        classLevels.map((level) => (
                          <option key={level.id} value={level.id}>
                            {level.name}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* Subjects */}
                {form.class_level_id && Array.isArray(subjects) && (
                  <div className="mb-3">
                    <label className="form-label">Select Subjects</label>
                    <div className="input-group">
                      <span className="input-group-text"><FaBook /></span>
                      <select
                        multiple
                        className="form-select"
                        onChange={handleSubjectChange}
                        value={form.subject_ids}
                        required
                      >
                        {subjects.map((subject) => (
                          <option key={subject.id} value={subject.id}>
                            {subject.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <small className="text-muted">
                      Hold Ctrl (Cmd on Mac) to select multiple.
                    </small>
                  </div>
                )}

                {/* Submit Button */}
                <div className="d-grid mt-4">
                  <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                    {loading ? "Processing..." : "Register and Pay"}
                  </button>
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

export default OleStudentRegister;
