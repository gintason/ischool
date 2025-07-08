import React from 'react';
import { Navbar, Nav, Container, Button, NavDropdown } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import logo from '../assets/olelogo.png';
import './Header.css';
import './OleHeader.css';
import { getDecodedUser } from "../utils/auth";
import { FaUserCircle } from "react-icons/fa";
import { FaUserGraduate, FaChalkboardTeacher } from "react-icons/fa";


const OleHeader = ({ onLogout }) => {
  const navigate = useNavigate();
  const user = getDecodedUser();
  const isLoggedIn = !!user;

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <Navbar expand="lg" className="ole-navbar" variant="dark">
      <Container className="px-5">
        <Navbar.Brand as={Link} to="/ole_home">
          <img
            src={logo}
            alt="iSchool Ole Logo"
            height="40"
            className="d-inline-block align-top"
          />
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="ole-navbar" />
        <Navbar.Collapse id="ole-navbar">
          <Nav className="me-auto ms-4">
            <Nav.Link as={Link} to="/ole_home" className="text-white">Home</Nav.Link>
            <Nav.Link as={Link} to="/about_ole" className="text-white">About</Nav.Link>
            <Nav.Link as={Link} to="/ole_how" className="text-white">How It Works</Nav.Link>
            <Nav.Link as={Link} to="/teacher/apply" className="text-white">Become A Teacher</Nav.Link>
            <Nav.Link as={Link} to="/contact_ole" className="text-white">Contact Us</Nav.Link>
          </Nav>

          <Nav className="ms-auto align-items-center">
            {isLoggedIn ? (
              <Button
                variant="outline-light"
                className="rounded-pill ms-3"
                onClick={handleLogout}
              >
                Logout
              </Button>
            ) : (
              <>
               <NavDropdown
                id="login-dropdown"
                title={<FaUserCircle size={22} className="text-white" />}
                align="end"
                className="dropdown-shift-left"
                renderMenuOnMount={true}
                menuVariant="light"
                style={{ position: 'absolute', zIndex: 1050 }}
              >
               <NavDropdown.Item as={Link} to="/ole_student/login">
              <span className="me-2"><FaUserGraduate /></span> Student Login
              </NavDropdown.Item>
              <NavDropdown.Item as={Link} to="/teacher/login">
                <span className="me-2"><FaChalkboardTeacher /></span> Teacher Login
              </NavDropdown.Item>
              </NavDropdown>

                <Button
                  as={Link}
                  to="/ole_student/register"
                  className="rounded-pill ms-5 ms-5 ole-register-btn"
                >
                  Get Matched
                </Button>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default OleHeader;
