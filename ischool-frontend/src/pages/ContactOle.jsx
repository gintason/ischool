import React, { useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, Form, Button, Alert, Card } from 'react-bootstrap';
import { FaEnvelope, FaPhone, FaWhatsapp, FaMapMarkerAlt } from 'react-icons/fa';

const ContactOle = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    message: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitted(false);

    try {
      await axios.post(`${process.env.REACT_APP_API_BASE_URL}/core/ole-contact`, {
        full_name: formData.fullName,
        email: formData.email,
        message: formData.message,
      });

      setSubmitted(true);
      setFormData({ fullName: '', email: '', message: '' });
    } catch (err) {
      console.error(err);
      setError('❌ Failed to send message. Please try again later.');
    }
  };

  return (
    <Container className="py-5 ms-5 me-5">
      <Row className="justify-content-center mb-5">
        <Col lg={8}>
          <h2 className="text-center fw-bold text-success">Contact iSchool Ole</h2>
          <p className="text-center text-muted fs-5">
            Do you have a question, suggestion, or complaint about our live classes? We’d love to hear from you!
          </p>
        </Col>
      </Row>

      <Row className="g-4">
         {/* Contact Info Section */}
        <Col md={6}>
          <Card className="p-4 shadow-sm border-0 bg-light h-100">
            <h5 className="text-dark fw-bold mb-4">Other Ways to Reach Us</h5>
            <ul className="list-unstyled fs-5">
              <li className="mb-3">
                <FaEnvelope className="me-2 text-success" />
                <strong>Email:</strong> support@ischool.ng
              </li>
              <li className="mb-3">
                <FaPhone className="me-2 text-success" />
                <strong>Phone:</strong> +234 810 145 5725
              </li>
              <li className="mb-3">
                <FaWhatsapp className="me-2 text-success" />
                <strong>WhatsApp:</strong> +234 905 641 7800
              </li>
              <li className="mb-3">
                <FaMapMarkerAlt className="me-2 text-success" />
                <strong>Location:</strong> iSchool.ng HQ, Abuja, Nigeria
              </li>
            </ul>
            <p className="mt-4 text-muted small">
              ⏰ Support Hours: Monday – Saturday, 8:00 AM to 6:00 PM.
            </p>
          </Card>
        </Col>
        
        {/* Form Section */}
        <Col md={6}>
          <Card className="p-4 shadow-sm border-0">
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3" controlId="fullName">
                <Form.Label>Full Name</Form.Label>
                <Form.Control
                  type="text"
                  name="fullName"
                  placeholder="Enter your full name"
                  value={formData.fullName}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="email">
                <Form.Label>Email Address</Form.Label>
                <Form.Control
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-4" controlId="message">
                <Form.Label>Your Message</Form.Label>
                <Form.Control
                  as="textarea"
                  name="message"
                  rows={5}
                  placeholder="Type your message here"
                  value={formData.message}
                  onChange={handleChange}
                  required
                />
              </Form.Group>

              <div className="d-grid">
                <Button type="submit" variant="success" size="lg">
                  📩 Send Message
                </Button>
              </div>

              {submitted && (
                <Alert variant="success" className="mt-4">
                  ✅ Thank you! Your message has been received. We’ll get back to you shortly.
                </Alert>
              )}

              {error && (
                <Alert variant="danger" className="mt-4">
                  {error}
                </Alert>
              )}
            </Form>
          </Card>
        </Col>

      
      </Row>
    </Container>
  );
};

export default ContactOle;
