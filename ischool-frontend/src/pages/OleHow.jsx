import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import {
  FaUserPlus,
  FaMoneyCheckAlt,
  FaUserCheck,
  FaVideo,
  FaFileAlt,
  FaChalkboardTeacher,
  FaStar,
} from 'react-icons/fa';

const HowItWorksOle = () => {
  return (
   <Container fluid className="py-5 bg-white">
  <Row className="justify-content-center mb-5">
    <Col lg={8}>
      <h2 className="text-center text-success fw-bold mb-3">How iSchool Ole Works</h2>
      <p className="text-center text-muted fs-5">
        Getting started with iSchool Ole is simple and designed for seamless learning.
      </p>
    </Col>
  </Row>

  <Row className="g-4 justify-content-center px-3 px-md-5">
    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-success bg-opacity-10">
        <FaUserPlus size={40} className="mb-3 text-success" />
        <h5 className="fw-bold mb-2">1. Register</h5>
        <p>Create an account as a student or parent and complete your profile.</p>
      </Card>
    </Col>

    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-primary bg-opacity-10">
        <FaMoneyCheckAlt size={40} className="mb-3 text-primary" />
        <h5 className="fw-bold mb-2">2. Subscribe</h5>
        <p>Select a plan that matches your schedule and preferred subjects.</p>
      </Card>
    </Col>

    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-warning bg-opacity-25">
        <FaUserCheck size={40} className="mb-3 text-warning" />
        <h5 className="fw-bold mb-2">3. Get Matched</h5>
        <p>Our system connects students with qualified teachers by class and subject.</p>
      </Card>
    </Col>

    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-danger bg-opacity-10">
        <FaVideo size={40} className="mb-3 text-danger" />
        <h5 className="fw-bold mb-2">4. Join Live Classes</h5>
        <p>Check your dashboard to join live sessions and follow your class timetable.</p>
      </Card>
    </Col>

    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-info bg-opacity-10">
        <FaFileAlt size={40} className="mb-3 text-info" />
        <h5 className="fw-bold mb-2">5. Access Materials</h5>
        <p>Review recorded classes and download lesson materials for revision.</p>
      </Card>
    </Col>

    <Col md={6} lg={4}>
      <Card className="h-100 border-0 shadow-sm text-center p-4 bg-secondary bg-opacity-10">
        <FaChalkboardTeacher size={40} className="mb-3 text-secondary" />
        <h5 className="fw-bold mb-2">6. Apply as a Teacher</h5>
        <p>Join our teaching team and conduct live classes for students across Nigeria.</p>
      </Card>
    </Col>
  </Row>

  <Row className="mt-5 px-3 px-md-5">
    <Col lg={10} className="mx-auto">
      <Card className="p-4 shadow-sm border-0 bg-light">
        <FaStar className="text-warning mb-2" size={24} />
        <p className="mb-0 text-muted fs-5">
          <strong>Bonus:</strong> Teachers only see a limited number of students in class for better focus,
          while admins maintain full visibility for quality assurance and smooth operations.
        </p>
      </Card>
    </Col>
  </Row>
</Container>

  );
};

export default HowItWorksOle;
