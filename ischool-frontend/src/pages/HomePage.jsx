import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Button, Carousel } from 'react-bootstrap';
import slider1 from '../assets/slider1.png';
import slider2 from '../assets/slider2.png';
import './styles/HomePage.css';
import { FiBookOpen, FiCheckCircle, FiUsers } from 'react-icons/fi';
import { FaUserPlus, FaSignInAlt, FaPenFancy } from 'react-icons/fa';
import { motion } from "framer-motion";
import TestimonialSection from "./TestimonialSection"; // Assuming you save it in this file

const HomePage = () => {
  return (
    <div className="homepage">
      {/* Hero Section with Fullscreen Carousel */}
    <section
    className="hero-section position-relative"
    style={{
      marginTop: '0',
      paddingTop: '0',
      paddingBottom: '3rem', // keep bottom spacing if needed
    }}
  >
  {/* Carousel */}
  <Carousel
    fade
    controls={false}
    indicators={false}
    interval={4000}
    className="hero-carousel"
  >
    <Carousel.Item>
      <img className="d-block w-100 hero-bg" src={slider1} alt="Slide 1" />
    </Carousel.Item>
    <Carousel.Item>
      <img className="d-block w-100 hero-bg" src={slider2} alt="Slide 2" />
    </Carousel.Item>
  </Carousel>

  {/* Gradient Overlay */}
  <div className="hero-gradient-overlay position-absolute top-0 start-0 w-100 h-100"></div>

  {/* Text Overlay */}
  <motion.div
    className="hero-content text-white position-absolute top-50 start-50 translate-middle text-center px-3 px-md-5"
    initial={{ opacity: 0, y: 60 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 1 }}
    style={{ marginTop: '-65px' }} // shift upward
  >
    <Container>
      <motion.h1
        className="fw-bold display-5 display-md-3 mb-3"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        Welcome to iSchool Ola
      </motion.h1>

      <motion.p
        className="lead fs-6 fs-md-5 mb-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        Your trusted online CBT portal for Nigerian secondary school students. Take tests from the comfort of your home or school.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8 }}
      >
        <Link to="/sign_up">
          <Button variant="light" size="lg">
            Get Started
          </Button>
        </Link>
      </motion.div>
    </Container>
  </motion.div>
</section>

      {/* Features Section */}
      <section className="py-5 text-center features-section">
        <Container>
          <h2 className="mb-4"></h2>
          <Row className="g-4">
            <Col md={4}>
              <div className="feature-box p-4 shadow rounded h-100 bg-edu-blue text-white d-flex flex-column align-items-center justify-content-center">
                <FiBookOpen size={48} className="mb-3" />
                <h5>CBT Exam Practice</h5>
                <p>Practice with real exam-style multiple choice questions for JSS1–SSS3 students.</p>
              </div>
            </Col>
            <Col md={4}>
              <div className="feature-box p-4 shadow rounded h-100 bg-edu-green text-white d-flex flex-column align-items-center justify-content-center">
                <FiCheckCircle size={48} className="mb-3" />
                <h5>Instant Grading</h5>
                <p>Receive instant results with email delivery after each test.</p>
              </div>
            </Col>
            <Col md={4}>
              <div className="feature-box p-4 shadow rounded h-100 bg-edu-orange text-white d-flex flex-column align-items-center justify-content-center">
                <FiUsers size={48} className="mb-3" />
                <h5>Role-Based Access</h5>
                <p>Teachers, Students, Parents, and Admins have personalized dashboards and access.</p>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      <section className="how-it-works-section py-5 text-center">
  <Container>
    <h2 className="mb-5 text-white">How It Works</h2>
    <Row className="g-4 justify-content-center">
      <Col md={4}>
        <div className="step-box p-4 rounded shadow">
          <div className="icon-wrapper mb-3">
            <FaUserPlus size={50} />
          </div>
          <h5 className="mb-3">1. Register And Pay for Slots</h5>
          <p>Register via school, home, or referral to get your credentials.</p>
        </div>
      </Col>
      <Col md={4}>
        <div className="step-box p-4 rounded shadow">
          <div className="icon-wrapper mb-3">
            <FaSignInAlt size={50} />
          </div>
          <h5 className="mb-3">2. Login</h5>
          <p>Use your system-generated username and password to log in.</p>
        </div>
      </Col>
      <Col md={4}>
        <div className="step-box p-4 rounded shadow">
          <div className="icon-wrapper mb-3">
            <FaPenFancy size={50} />
          </div>
          <h5 className="mb-3">3. Take a Test</h5>
          <p>Select your class and subject to begin your test experience.</p>
        </div>
      </Col>
    </Row>
  </Container>
</section>


      {/* Call to Action */}
      <section className="py-5 bg-dark text-white text-center mb-5 pb-3">
        <Container>
          <h2 className="mb-3">Ready to Test Smarter?</h2>
          <p>Join thousands of students who are preparing smarter and performing better with iSchool Ola.</p>
          <Link to="/sign_up">
          <Button variant="primary" size="lg" className="mt-2">
            Take a Test Now
          </Button>
        </Link>
        
        </Container>
      </section>


       {/* Testimonial Section */}
      <TestimonialSection />

    </div>
  );
};

export default HomePage;
