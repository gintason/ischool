import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./OnboardingPage.css";

const OnboardingPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Add entrance animation classes after mount
    const timer = setTimeout(() => {
      document.querySelector('.onboarding-container')?.classList.add('loaded');
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const handleNavigate = (path) => {
    // Add exit animation before navigating
    const cards = document.querySelectorAll('.option-card');
    cards.forEach(card => card.classList.add('card-exit'));
    
    setTimeout(() => {
      navigate(path);
    }, 400);
  };

  return (
    <div className="onboarding-wrapper">
      {/* Background with overlay */}
      <div className="onboarding-bg">
        <div className="bg-overlay"></div>
        <div className="bg-grid"></div>
        <div className="bg-particles">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
          <div className="particle particle-5"></div>
          <div className="particle particle-6"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="onboarding-container">
        <div className="content-wrapper">
          
          {/* Logo & Header Section */}
          <div className="header-section animate-slide-down">
            </div>
            
            <div className="slogan-section animate-fade-in delay-1">
              <h1 className="slogan-main">
                Welcome to <span className="text-gradient">iSchool</span>.ng
              </h1>
              <p className="slogan-sub">Empowering Students with Digital Learning Solutions</p>
            </div>

            <div className="divider-line animate-scale-in delay-2"></div>
          </div>

          {/* Cards Section */}
          <div className="cards-container">
            
            {/* iSchool Ole Card */}
            <div 
              className="option-card card-ole animate-slide-left delay-3"
              onClick={() => handleNavigate("/ole_home")}
            >
              <div className="card-inner">
                <div className="card-glow glow-ole"></div>
                
                <div className="card-icon-container">
                  <div className="card-icon icon-ole">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                      <path d="M6 12v5c0 2 4 3 6 3s6-1 6-3v-5"/>
                    </svg>
                  </div>
                </div>

                <div className="card-content">
                  <h3 className="card-title">iSchool Ole</h3>
                  <p className="card-description">
                    Get matched with a teacher for live interactive lessons.
                  </p>
                </div>

                <div className="card-action">
                  <button className="btn-card btn-ole">
                    <span>Get Started</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* iSchool Ola Card */}
            <div 
              className="option-card card-ola animate-slide-right delay-4"
              onClick={() => handleNavigate("/ola_home")}
            >
              <div className="card-inner">
                <div className="card-glow glow-ola"></div>
                
                <div className="card-icon-container">
                  <div className="card-icon icon-ola">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                      <path d="M8 21h8M12 17v4"/>
                    </svg>
                  </div>
                </div>

                <div className="card-content">
                  <h3 className="card-title">iSchool Ola</h3>
                  <p className="card-description">
                    For CBT-based tests, revision, and subscriptions.
                  </p>
                </div>

                <div className="card-action">
                  <button className="btn-card btn-ola">
                    <span>Get Started</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

          </div>

          {/* Footer */}
          <div className="footer-section animate-fade-in delay-5">
            <p className="footer-text">v1.0.0 • Developed By AiTrend</p>
            <p className="footer-copyright">
              &copy; {new Date().getFullYear()} iSchool.ng. All Rights Reserved.
            </p>
          </div>

        </div>
      </div>
  );
};

export default OnboardingPage;