import React from 'react';
import { Container, Row, Col, Card, ListGroup } from 'react-bootstrap';
import { FaChalkboardTeacher, FaBookOpen, FaCalendarAlt, FaUsers } from 'react-icons/fa';

const AboutOle = () => {
  return (
    <Container fluid className="py-5 bg-light">
      <Row className="justify-content-center">
        <Col lg={8}>
          <Card className="shadow-sm border-0 p-4">
            <h2 className="text-success fw-bold mb-3 text-center">About iSchool Ole</h2>
            <p className="lead text-secondary text-center">
              <strong>iSchool Ole</strong> is a unique online learning experience that connects students with live teachers for real-time, interactive lessons.
            </p>
            <p className="text-muted fs-5 text-center">
              Tailored for both primary and secondary school students, iSchool Ole delivers personalized, curriculum-aligned learning — all from the comfort of home.
            </p>

            <h5 className="mt-4 mb-3 text-success">Key Features:</h5>
            <ListGroup variant="flush" className="fs-5">
              <ListGroup.Item className="d-flex align-items-center">
                <FaChalkboardTeacher className="me-2 text-success" />
                Real-time teaching by qualified educators
              </ListGroup.Item>
              <ListGroup.Item className="d-flex align-items-center">
                <FaBookOpen className="me-2 text-primary" />
                Access to lesson materials and class recordings
              </ListGroup.Item>
              <ListGroup.Item className="d-flex align-items-center">
                <FaCalendarAlt className="me-2 text-warning" />
                Structured learning via scheduled timetables
              </ListGroup.Item>
              <ListGroup.Item className="d-flex align-items-center">
                <FaUsers className="me-2 text-danger" />
                Unlimited students per class (with visibility limits)
              </ListGroup.Item>
            </ListGroup>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AboutOle;
