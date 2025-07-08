import React from "react";
import { useNavigate } from "react-router-dom";
import "./OnboardingPage.css"; // Ensure it includes .onboarding-bg and .fade-in styles

const OnboardingPage = () => {
  const navigate = useNavigate();

  const handleNavigate = (path) => {
    navigate(path);
  };

  return (
    <div className="onboarding-bg text-white d-flex justify-content-center align-items-center min-vh-100 fade-in">
      <div className="container px-3 px-md-5 py-5">
        <div className="text-center mb-5">
          <h1 className="fw-bold display-4 mb-3">
            Welcome to <span className="text-warning">iSchool.ng</span>
          </h1>
          <p className="lead mb-0 text-light fs-5">
            Empowering Students with Digital Learning Solutions
          </p>
        </div>

        <div className="row justify-content-center g-4">
          {/* iSchool Ole FIRST */}
          <div className="col-lg-5">
            <div
              className="card h-100 shadow-lg border-0 option-card"
              onClick={() => handleNavigate("/ole_home")}
            >
              <div className="card-body py-5 text-center">
                <h3 className="card-title fw-bold text-success">iSchool Ole</h3>
                <p className="card-text fs-5 text-secondary">
                  Get matched with a teacher for live interactive lessons
                </p>
                <button className="btn btn-success rounded-pill px-4 mt-3">
                  Go to iSchool Ole
                </button>
              </div>
            </div>
          </div>

          {/* iSchool Ola SECOND */}
          <div className="col-lg-5">
            <div
              className="card h-100 shadow-lg border-0 option-card"
              onClick={() => handleNavigate("/ola_home")}
            >
              <div className="card-body py-5 text-center">
                <h3 className="card-title fw-bold text-primary">iSchool Ola</h3>
                <p className="card-text fs-5 text-secondary">
                  For CBT-based tests, revision, and subscriptions
                </p>
                <button className="btn btn-outline-primary rounded-pill px-4 mt-3">
                  Go to iSchool Ola
                </button>
              </div>
            </div>
          </div>
        </div>

        <footer className="mt-5 text-light text-center small">
          &copy; {new Date().getFullYear()} iSchool.ng. All Rights Reserved.
        </footer>
      </div>
    </div>
  );
};

export default OnboardingPage;
