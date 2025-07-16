import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../../utils/axiosInstance";
import { Container, Row, Col, Form, Button, Alert, Card } from "react-bootstrap";
import { FaEnvelope, FaLock, FaChalkboardTeacher } from "react-icons/fa";
import { ToastContainer, toast } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

const TeacherLogin = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await axiosInstance.post("login/", {
        email: form.email,
        password: form.password,
      });

      const { token, user } = res.data;

      if (user.role !== "teacher") {
        setError("Access denied. This account is not a teacher.");
        return;
      }

      // ✅ Save token and teacher info to localStorage
      localStorage.setItem("token", token);
      localStorage.setItem("teacherEmail", user.email);
      localStorage.setItem("teacherName", user.full_name);
      localStorage.setItem("teacherRole", user.role);

      toast.success("Login successful!", { autoClose: 3000 });
      setTimeout(() => navigate("/teacher/dashboard"), 1500);
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Access denied. This account is not a teacher.");
      } else if (err.response?.status === 400) {
        setError("Invalid credentials. Please try again.");
      } else {
        setError("Login failed. Please check your internet or try again.");
      }
    }
  };

  return (
    <Container className="py-5">
      <ToastContainer position="top-center" />
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow border-0 mb-5">
            <Card.Body className="p-5">
              <div className="text-center mb-4">
                <FaChalkboardTeacher size={40} className="text-primary mb-2" />
                <h3 className="fw-bold">Teacher Login</h3>
              </div>

              {error && <Alert variant="danger">{error}</Alert>}

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <FaEnvelope className="me-2 text-primary" />
                    Email
                  </Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="Enter your email"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>
                    <FaLock className="me-2 text-primary" />
                    Password
                  </Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    required
                  />
                </Form.Group>

                <div className="d-grid">
                  <Button type="submit" variant="primary" size="lg">
                    Login
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TeacherLogin;
