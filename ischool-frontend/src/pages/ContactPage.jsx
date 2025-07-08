import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Alert, Card } from 'react-bootstrap';
import { FaEnvelope, FaPhone, FaWhatsapp, FaMapMarkerAlt } from 'react-icons/fa';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    message: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(false);
    setError(false);

    try {
      const res = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/core/ola-contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) throw new Error('Failed to send message');

      setSubmitted(true);
      setFormData({ fullName: '', email: '', message: '' });
    } catch (err) {
      setError(true);
    }
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center mb-5">
        <Col lg={8} className="text-center">
          <h2 className="fw-bold text-primary mb-3">Contact iSchool Ola</h2>
          <p className="lead text-muted">Have questions, suggestions or need help with tests? We'd love to hear from you!</p>
        </Col>
      </Row>

      <Row className="g-5">
        <Col md={6}>
          <Card className="shadow border-0">
            <Card.Body>
              <h4 className="mb-4 text-secondary">Send Us a Message</h4>
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

                <Form.Group className="mb-3" controlId="message">
                  <Form.Label>Your Message</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={5}
                    name="message"
                    placeholder="Type your message here"
                    value={formData.message}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>

                <Button variant="primary" type="submit" className="px-4 py-2 w-100">
                  Send Message
                </Button>

                {submitted && (
                  <Alert variant="success" className="mt-4">
                    ✅ Thank you! Your message has been received.
                  </Alert>
                )}

                {error && (
                  <Alert variant="danger" className="mt-4">
                    ❌ Something went wrong. Please try again later.
                  </Alert>
                )}
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="bg-light border-0 h-100 shadow-sm p-4">
            <h4 className="text-secondary mb-4">Other Ways to Reach Us</h4>
            <ul className="list-unstyled fs-5">
              <li className="mb-3">
                <FaEnvelope className="me-2 text-primary" />
                <strong>Email:</strong> info@ischool.ng
              </li>
              <li className="mb-3">
                <FaPhone className="me-2 text-success" />
                <strong>Phone:</strong> +234 810 145 5725
              </li>
              <li className="mb-3">
                <FaWhatsapp className="me-2 text-success" />
                <strong>WhatsApp:</strong>  +234 905 6417 800
              </li>
              <li className="mb-3">
                <FaMapMarkerAlt className="me-2 text-danger" />
                <strong>Location:</strong> iSchool.ng HQ, Abuja, Nigeria
              </li>
            </ul>
            <p className="text-muted mt-4">📅 We’re available Monday–Saturday, 8:00 AM to 6:00 PM.</p>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ContactPage;
