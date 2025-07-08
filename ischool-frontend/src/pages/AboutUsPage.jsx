import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { FaChalkboardTeacher, FaLaptopCode, FaUserGraduate, FaBookOpen } from 'react-icons/fa';
import './styles/AboutUsPage.css';
import heroImage from '../assets/slider2.png';
import sideOneImage from '../assets/sideone.jpg'; // adjust path as needed



const AboutUsPage = () => {
  return (
    <div className="about-page">
      {/* Hero Section */}
         <div
          className="hero-section text-white text-center"
          style={{
            backgroundImage: `linear-gradient(rgba(16, 17, 18, 0.7), rgba(5, 5, 5, 0.7)), url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            padding: '6rem 1rem',
          }}
        >
          <div className="text-center" style={{ marginTop: '250px' }}>
          <h1 className="display-4 fw-bold">About iSchool Ola</h1>
          <p className="lead">Your trusted CBT portal for Secondary School Excellence</p>
         </div>
        </div>

      {/* Who We Are */}
      <Container className="py-5 bg-light">
        <Row className="align-items-center g-3">
          <Col md={5} className="text-center">
            <img
              src={sideOneImage}
              alt="Students taking CBT"
              className="img-fluid rounded shadow-sm"
              style={{ maxWidth: '100%', height: 'auto' }}
            />
          </Col>
          <Col md={7}>
            <h2 className="fw-bold text-primary mb-4">Who We Are</h2>
            <p className="lead text-secondary">
              <strong>iSchool Ola</strong> is a trusted online CBT (Computer-Based Test) portal designed exclusively
              for Nigerian secondary school students from JSS1 to SS3.
            </p>
            <p className="text-muted">
              Whether at home or school, students can easily access timed assessments that mirror real exam environments.
              We are passionate about simplifying learning through modern digital tools, empowering students and schools
              with real-time performance insights.
            </p>
          </Col>
        </Row>
      </Container>


  {/* What We Offer */}
   <Container className="py-5 bg-light">
      <h2 className="text-center fw-bold text-success mb-4">What We Offer</h2>
      <p className="text-center text-muted fs-5 mb-5">
        iSchool Ola empowers secondary school students and educators through seamless digital assessment tools.
      </p>

      <Row className="g-4">
        <Col md={6} lg={3}>
          <Card className="text-center border-0 shadow-sm h-100 rounded-4 p-3 mb-3">
            <Card.Body>
              <FaLaptopCode size={40} className="mb-3 text-primary" />
              <Card.Title className="fw-bold fs-5">Online CBT Tests</Card.Title>
              <Card.Text className="text-muted small">
                Timed multiple choice and theory tests for JSS1–SS3 students, accessible anytime, anywhere.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3}>
          <Card className="text-center border-0 shadow-sm h-100 rounded-4 p-3 mb-3">
            <Card.Body>
              <FaChalkboardTeacher size={40} className="mb-3 text-success" />
              <Card.Title className="fw-bold fs-5">Teacher & School Dashboard</Card.Title>
              <Card.Text className="text-muted small">
                Assign tests, track student progress, and monitor performance in one powerful dashboard.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3}>
          <Card className="text-center border-0 shadow-sm h-100 rounded-4 p-3 mb-3">
            <Card.Body>
              <FaBookOpen size={40} className="mb-3 text-warning" />
              <Card.Title className="fw-bold fs-5">Curriculum-Based Content</Card.Title>
              <Card.Text className="text-muted small">
                WAEC & NECO-aligned questions built on Nigeria’s official secondary school curriculum.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6} lg={3}>
          <Card className="text-center border-0 shadow-sm h-100 rounded-4 p-3 mb-3">
            <Card.Body>
              <FaUserGraduate size={40} className="mb-3 text-danger" />
              <Card.Title className="fw-bold fs-5">Student Reports</Card.Title>
              <Card.Text className="text-muted small">
                Instantly view or download detailed student performance reports with insightful metrics.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>

      {/* Call to Action */}
      <div className="cta-section py-5 mb-0 text-white text-center">
        <Container className='mb-0'>
          <h2 className="fw-bold mb-3">Ready to Empower Your Students?</h2>
          <p className="mb-4">Join the iSchool Ola community today and take learning to the next level.</p>
          <Button variant="light" size="lg" href="/sign_up">Get Started</Button>
        </Container>
      </div>
    </div>
  );
};

export default AboutUsPage;
