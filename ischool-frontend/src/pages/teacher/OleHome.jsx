import React, { useEffect } from 'react';
import { Link } from "react-router-dom";
import {
  FaChalkboardTeacher,
  FaBookOpen,
  FaClock,
  FaLaptopHouse,
  FaUserGraduate,
  FaRegSmile,
} from "react-icons/fa";
import "./OleHome.css";

import slide1 from "../../assets/oleslide1.jpg";
import slide2 from "../../assets/oleslide2.jpg";
import olehside from "../../assets/olehside.jpg";


const OleHomePage = () => {

  useEffect(() => {
    const el = document.querySelector('#oleHeroCarousel');
    if (el && window.bootstrap?.Carousel) {
      const carousel = new window.bootstrap.Carousel(el, {
        interval: 5000,
        ride: 'carousel',
        pause: false,
      });
      carousel.cycle(); // Start auto-slide
    }
  }, []);


  return (
    <div className="ole-home">

      {/* ✅ Full-width Hero Carousel */}
      <div
        id="oleHeroCarousel"
        className="carousel slide"
        data-bs-ride="carousel"
        data-bs-interval="5000"
      >
        <div className="carousel-indicators">
          <button type="button" data-bs-target="#oleHeroCarousel" data-bs-slide-to="0" className="active" aria-current="true" aria-label="Slide 1"></button>
          <button type="button" data-bs-target="#oleHeroCarousel" data-bs-slide-to="1" aria-label="Slide 2"></button>
        </div>

        <div className="carousel-inner">
          <div className="carousel-item active">
            <div
              className="hero-slide d-flex align-items-center text-white text-center"
              style={{
                minHeight: "70vh",
                background: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${slide1}) center/cover no-repeat`,
              }}
            >
              <div className="container">
                <h1 className="display-4 fw-bold">Join iSchool Ole</h1>
                <p className="lead">Personalized live online classes from home.</p>
                <Link to="/ole_student/register" className="btn btn-primary btn-lg mt-3 shadow">Get Started Now</Link>
              </div>
            </div>
          </div>

          <div className="carousel-item">
            <div
              className="hero-slide d-flex align-items-center text-white text-center"
              style={{
                minHeight: "70vh",
                background: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${slide2}) center/cover no-repeat`,
              }}
            >
              <div className="container">
                <h1 className="display-4 fw-bold">Become a Teacher</h1>
                <p className="lead">Apply to teach and impact lives.</p>
                <Link to="/teacher/apply" className="btn btn-success btn-lg mt-3 shadow">Apply Now</Link>
              </div>
            </div>
          </div>
        </div>

        <button className="carousel-control-prev" type="button" data-bs-target="#oleHeroCarousel" data-bs-slide="prev">
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
        </button>
        <button className="carousel-control-next" type="button" data-bs-target="#oleHeroCarousel" data-bs-slide="next">
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
        </button>
      </div>

      {/* ✅ Page Content with Breathing Space */}
      <div className="px-3 px-md-5"> 
        {/* How it Works */}
      <section className="ole-full-width-section ole-slanted-section py-5 bg-dark text-white">
      <div className="row g-4 mx-0 px-3 px-md-5"> 
        <h2 className="text-center text-primary fw-bold w-100 mb-5">How iSchool Ole Works</h2>

        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100 text-center p-4 bg-white text-dark">
            <FaUserGraduate size={48} className="mb-3 text-primary" />
            <h5 className="fw-bold">Sign Up</h5>
            <p>Create a student or teacher account in minutes.</p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100 text-center p-4" style={{ backgroundColor: "#e7fbe7" }}>
            <FaClock size={48} className="mb-3 text-success" />
            <h5 className="fw-bold">Subscribe</h5>
            <p>Select a learning plan that suits your needs.</p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card border-0 shadow-sm h-100 text-center p-4" style={{ backgroundColor: "#fff7e6" }}>
            <FaLaptopHouse size={48} className="mb-3 text-warning" />
            <h5 className="fw-bold">Start Learning</h5>
            <p>Join live lessons with verified teachers.</p>
          </div>
        </div>
      </div>
    </section>



        {/* Why Choose Us */}
      <section className="py-5 bg-white">
      <div className="container">
        <h2 className="text-center mb-5 text-success fw-bold">Why Choose iSchool Ole?</h2>
        <div className="row g-4 align-items-center">
          <div className="col-md-6">
            <div className="row g-3">
              <div className="col-sm-6">
                <div className="card h-100 shadow border-0 p-3 text-center" style={{ backgroundColor: "#e3f2fd" }}>
                  <FaChalkboardTeacher size={40} className="text-primary mb-2" />
                  <h6>Certified Teachers</h6>
                  <p className="small">Experienced professionals guiding every lesson.</p>
                </div>
              </div>
              <div className="col-sm-6">
                <div className="card h-100 shadow border-0 p-3 text-center" style={{ backgroundColor: "#f3e5f5" }}>
                  <FaBookOpen size={40} className="text-purple mb-2" style={{ color: "#6f42c1" }} />
                  <h6>Curriculum-Aligned</h6>
                  <p className="small">Lessons tailored to local and global standards.</p>
                </div>
              </div>
              <div className="col-sm-6">
                <div className="card h-100 shadow border-0 p-3 text-center" style={{ backgroundColor: "#e8f5e9" }}>
                  <FaClock size={40} className="text-success mb-2" />
                  <h6>Flexible Schedules</h6>
                  <p className="small">Learn at your pace—anytime, anywhere.</p>
                </div>
              </div>
              <div className="col-sm-6">
                <div className="card h-100 shadow border-0 p-3 text-center" style={{ backgroundColor: "#e3f2fd" }}>
                  <FaRegSmile size={40} className="text-info mb-2" />
                  <h6>Student-Centered</h6>
                  <p className="small">Engaging, interactive, and student-focused methods.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 text-center">
            <img
              src={olehside}
              alt="Learning"
              className="img-fluid rounded shadow"
              style={{ maxHeight: "320px", objectFit: "cover" }}
            />
          </div>
        </div>
      </div>
    </section>

        {/* Testimonials Carousel - Full Width Light Grey with Avatars */}
      <section className="ole-full-width-test-section bg-light-grey py-5">
        <div className="container-fluid">
          <h2 className="text-center mb-5 text-primary fw-bold">What Our Students & Parents Say</h2>

          <div
            id="testimonialCarousel"
            className="carousel slide"
            data-bs-ride="carousel"
            data-bs-interval="6000"
          >
            <div className="carousel-inner text-center">

              {/* Slide 1 */}
              <div className="carousel-item active">
                <div className="card mx-auto border-0 shadow-sm p-4 bg-white" style={{ maxWidth: "650px" }}>
                  <div className="d-flex align-items-center justify-content-center mb-3">
                    <div className="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center me-3" style={{ width: "60px", height: "60px", fontSize: "24px", fontWeight: "bold" }}>
                      G
                    </div>
                    <div className="text-start">
                      <h6 className="mb-0">Grace O.</h6>
                      <small className="text-muted">Parent of JS1 Student</small>
                    </div>
                  </div>
                  <p className="fst-italic text-muted">“iSchool Ole has transformed how my daughter learns at home. The teachers are professional and the content is top-notch.”</p>
                </div>
              </div>

              {/* Slide 2 */}
              <div className="carousel-item">
                <div className="card mx-auto border-0 shadow-sm p-4 bg-white" style={{ maxWidth: "650px" }}>
                  <div className="d-flex align-items-center justify-content-center mb-3">
                    <div className="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center me-3" style={{ width: "60px", height: "60px", fontSize: "24px", fontWeight: "bold" }}>
                      D
                    </div>
                    <div className="text-start">
                      <h6 className="mb-0">David M.</h6>
                      <small className="text-muted">SS2 Student</small>
                    </div>
                  </div>
                  <p className="fst-italic text-muted">“I love how flexible the schedule is. I can attend classes even after school hours and still keep up with other activities.”</p>
                </div>
              </div>

              {/* Slide 3 */}
              <div className="carousel-item">
                <div className="card mx-auto border-0 shadow-sm p-4 bg-white" style={{ maxWidth: "650px" }}>
                  <div className="d-flex align-items-center justify-content-center mb-3">
                    <div className="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center me-3" style={{ width: "60px", height: "60px", fontSize: "24px", fontWeight: "bold" }}>
                      M
                    </div>
                    <div className="text-start">
                      <h6 className="mb-0">Mrs. Okon</h6>
                      <small className="text-muted">Parent</small>
                    </div>
                  </div>
                  <p className="fst-italic text-muted">“The student-focused approach is amazing. My son is always excited to join his live classes. Highly recommended!”</p>
                </div>
              </div>
            </div>

            {/* Controls */}
            <button className="carousel-control-prev" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="prev">
              <span className="carousel-control-prev-icon" aria-hidden="true"></span>
            </button>
            <button className="carousel-control-next" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="next">
              <span className="carousel-control-next-icon" aria-hidden="true"></span>
            </button>

            {/* Indicators */}
            <div className="carousel-indicators mt-4">
              <button type="button" data-bs-target="#testimonialCarousel" data-bs-slide-to="0" className="active" aria-label="Slide 1"></button>
              <button type="button" data-bs-target="#testimonialCarousel" data-bs-slide-to="1" aria-label="Slide 2"></button>
              <button type="button" data-bs-target="#testimonialCarousel" data-bs-slide-to="2" aria-label="Slide 3"></button>
            </div>
          </div>
        </div>
      </section>



      </div>
    </div>
  );
};

export default OleHomePage;
