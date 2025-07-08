import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import logo from '../assets/logo1.png';
import { FaFacebookF, FaTwitter, FaInstagram, FaYoutube } from 'react-icons/fa';
import googlePlayBadge from '../assets/google-play-badge.png';
import appStoreBadge from '../assets/app-store-badge.png';


const Footer = () => {
  return (
    <footer
      style={{
        background: 'linear-gradient(to bottom, #00BFFF, #050809)', // ✅ fixed gradient
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
              alt="iSchool Ola Logo"
              style={{ width: '150px', height: 'auto', marginBottom: '10px' }}
            />
            <p>
              iSchool Ola provides an innovative online assessment platform for
              secondary school students to improve learning and test-taking skills.
            </p>
          </Col>

          <Col xs={12} sm={6} md={4}>
            <h5 className="text-dark">Quick Links</h5>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li><a href="/ola_home" style={{ color: 'white', textDecoration: 'none' }}>Home</a></li>
              <li><a href="/about_us" style={{ color: 'white', textDecoration: 'none' }}>About Us</a></li>
              <li><a href="/news" style={{ color: 'white', textDecoration: 'none' }}>News</a></li>
              <li><a href="/sign_up" style={{ color: 'white', textDecoration: 'none' }}>Take Test</a></li>
              <li><a href="/contact" style={{ color: 'white', textDecoration: 'none' }}>Contact Us</a></li>
            </ul>
          </Col>

          <Col xs={12} sm={6} md={4}>
            <h5 className="text-dark">Follow Us</h5>
            <div>
              <a
                href="https://facebook.com/ischool.ng"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}
              >
                <FaFacebookF />
              </a>
              <a
                href="https://x.com/Ischoololeola"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}
              >
                <FaTwitter />
              </a>
              <a
                href="https://www.instagram.com/ischool_ng/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'white', marginRight: '15px', fontSize: '1.4rem' }}
              >
                <FaInstagram />
              </a>
              <a
                href="https://www.youtube.com/channel/UCl1Nnri9ooaH0MGhReQnuDg"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'white', fontSize: '1.4rem' }}
              >
                <FaYoutube />
              </a>
            </div>

            {/* App Download Badges */}
        <div className="app-downloads mt-3" style={{ display: 'flex', gap: '10px', justifyContent: 'flex-start' }}>
          <a href="https://play.google.com/store/apps/details?id=your.app.id" target="_blank" rel="noopener noreferrer">
            <img 
              src={googlePlayBadge}
              alt="Download on Google Play" 
              style={{ height: '40px', cursor: 'pointer' }} 
            />
          </a>
          <a href="https://apps.apple.com/app/idyourappid" target="_blank" rel="noopener noreferrer">
            <img 
              src={appStoreBadge}
              alt="Download on the App Store" 
              style={{ height: '40px', cursor: 'pointer' }} 
            />
          </a>
        </div>

          </Col>
        </Row>

        <Row>
          <Col className="text-center mt-4 text-white">
            <p>&copy; {new Date().getFullYear()} iSchool Ola. All Rights Reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
