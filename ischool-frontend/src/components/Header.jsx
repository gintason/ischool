import React from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import logo from '../assets/logo1.png';
import './Header.css';
import { getDecodedUser } from "../utils/auth";

const Header = ({ onLogout }) => {
  const navigate = useNavigate();
  const user = getDecodedUser();
  const isLoggedIn = !!user;

  const handleLogout = () => {
    onLogout(); // Clear tokens
    navigate('/');
  };

  return (
    <Navbar expand="lg" className="custom-navbar" variant="dark">
      <Container className="px-5">
        <Navbar.Brand as={Link} to="/ola_home">
          <img
            src={logo}
            alt="Logo"
            height="40"
            className="d-inline-block align-top"
          />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="main-navbar" />
        <Navbar.Collapse id="main-navbar">
          <Nav className="me-auto ms-4">
            <Nav.Link as={Link} to="/ola_home" className="text-white">HOME</Nav.Link>
            <Nav.Link as={Link} to="/about_us" className="text-white">ABOUT US</Nav.Link>
            <Nav.Link as={Link} to="/news" className="text-white">NEWS</Nav.Link>
            <Nav.Link as={Link} to="/sign_up" className="text-white">TAKE TEST</Nav.Link>
            <Nav.Link as={Link} to="/contact" className="text-white">CONTACT US</Nav.Link>
          </Nav>

          <Nav className="ms-auto align-items-center">
            {user && user.registration_group ? (
              <Button
                variant="outline-light"
                className="rounded-pill ms-3"
                onClick={handleLogout}
              >
                Logout
              </Button>
            ) : (
              <>
                <Nav.Link
                  as={Link}
                  to="/student/login"
                  className="text-white me-2"
                >
                  Student LogIn
                </Nav.Link>
                <Button
                  as={Link}
                  to="/sign_up"
                  className="rounded-pill ms-2 register-btn"
                >
                  Get Started
                </Button>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
