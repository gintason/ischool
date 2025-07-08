// You can copy the exact content from your current Footer.jsx
import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import logo from '../assets/olelogo.png';
import { FaFacebookF, FaTwitter, FaInstagram, FaYoutube } from 'react-icons/fa';
import googlePlayBadge from '../assets/google-play-badge.png';
import appStoreBadge from '../assets/app-store-badge.png';

const OleFooter = () => {
  return (
    <footer
      style={{
        background: 'linear-gradient(to bottom, #00BFFF, #050809)',
        color: 'white',
        padding: '20px 0',
        position: 'relative',
        bottom: 0,
        width: '100%',
      }}
    >
      <Container className="px-5 pt-3">
        <Row>
          <Col xs={12} sm={6} md={4}>
            <img
              src={logo}
              alt="iSchool Ole Logo"
              style={{ width: '150px', height: 'auto', marginBottom: '10px' }}
            />
            <p>
              iSchool Ole connects students to experienced teachers for live,
              personalized online learning in real time.
            </p>
          </Col>

          <Col xs={12} sm={6} md={4}>
            <h5 className="text-dark">Quick Links</h5>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li><a href="/ole_home" style={{ color: 'white', textDecoration: 'none' }}>Home</a></li>
              <li><a href="/about_ole" style={{ color: 'white', textDecoration: 'none' }}>About</a></li>
              <li><a href="/teacher/apply" style={{ color: 'white', textDecoration: 'none' }}>Teacher Application</a></li>
              <li><a href="/contact_ole" style={{ color: 'white', textDecoration: 'none' }}>Contact</a></li>
            </ul>
          </Col>

          <Col xs={12} sm={6} md={4}>
            <h5 className="text-dark">Follow Us</h5>
            <div>
              <a href="https://facebook.com/ischool.ng" target="_blank" rel="noopener noreferrer" style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}>
                <FaFacebookF />
              </a>
              <a href="https://x.com/Ischoololeola" target="_blank" rel="noopener noreferrer" style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}>
                <FaTwitter />
              </a>
              <a href="https://instagram.com/ischool_ng" target="_blank" rel="noopener noreferrer" style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}>
                <FaInstagram />
              </a>
              <a href="https://www.youtube.com/channel/UCl1Nnri9ooaH0MGhReQnuDg" target="_blank" rel="noopener noreferrer" style={{ color: 'white', fontSize: '1.4rem' }}>
                <FaYoutube />
              </a>
            </div>

            <div className="app-downloads mt-3" style={{ display: 'flex', gap: '10px' }}>
              <a href="https://play.google.com/store/apps/details?id=your.app.id" target="_blank" rel="noopener noreferrer">
                <img src={googlePlayBadge} alt="Download on Google Play" style={{ height: '40px' }} />
              </a>
              <a href="https://apps.apple.com/app/idyourappid" target="_blank" rel="noopener noreferrer">
                <img src={appStoreBadge} alt="Download on the App Store" style={{ height: '40px' }} />
              </a>
            </div>
          </Col>
        </Row>

        <Row>
          <Col className="text-center mt-4 text-white">
            <p>&copy; {new Date().getFullYear()} iSchool Ole. All Rights Reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default OleFooter;
 