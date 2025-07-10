import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Row,
  Col,
  Card,
  Spinner,
  Alert,
  ListGroup,
  Badge,
  Button,
} from 'react-bootstrap';
import axios from 'axios';

function StudentDashboard() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) {
      navigate('/student/login');
    } else {
      axios
        .get('https://api.ischool.ng/api/student/dashboard/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          setDashboardData(response.data);
          setLoading(false);
        })
        .catch((error) => {
          console.error('Failed to fetch dashboard data:', error);
          setLoading(false);
        });
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh'); // in case you're storing refresh tokens too
    navigate('/student/login');
  };

  return (
    <Container className="my-5">
      <div className="w-100 w-md-75 mx-auto">
        <Card className="shadow-lg rounded-4 p-4 bg-white border-0">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="text-primary fw-bold">🎓 Student Dashboard</h2>
            <Button variant="outline-danger" size="sm" onClick={handleLogout}>
              🔒 Logout
            </Button>
          </div>

          {loading ? (
            <div className="text-center my-5">
              <Spinner animation="border" variant="primary" />
              <p className="mt-3">Loading dashboard...</p>
            </div>
          ) : dashboardData ? (
            <>
              <Row className="g-4 mb-4">
                <Col md={6}>
                  <Card className="p-3 shadow-sm border-0 rounded-3 bg-light">
                    <h5 className="mb-3 text-muted">👤 Account Info</h5>
                    <p className="mb-2"><strong>Username:</strong> {dashboardData.username}</p>
                    {dashboardData.related_students?.map((student, index) => (
                      <div key={index} className="mb-2">
                        <p className="mb-1"><strong>Full Name:</strong> {student.full_name}</p>
                        <p className="mb-0"><strong>Email:</strong> {student.email}</p>
                      </div>
                    ))}
                  </Card>
                </Col>

                <Col md={6}>
                  <Card className="p-3 shadow-sm border-0 rounded-3 bg-light">
                    <h5 className="mb-3 text-muted">📊 Test Summary</h5>
                    <p className="mb-2">
                      <strong>Tests Taken Today:</strong> {dashboardData.tests_taken_today}
                    </p>
                    <p className="mb-0">
                      <strong>Tests Remaining Today:</strong> {dashboardData.tests_remaining_today}
                    </p>
                  </Card>
                </Col>
              </Row>

              <Row className="g-4">
                <Col>
                  <Card className="p-3 shadow-sm border-0 rounded-3 bg-light">
                    <h5 className="mb-3 text-muted">📝 Recent Tests</h5>
                    {dashboardData.recent_tests?.length === 0 ? (
                      <Alert variant="info">No recent tests.</Alert>
                    ) : (
                      <ListGroup variant="flush">
                        {dashboardData.recent_tests.map((test, idx) => (
                          <ListGroup.Item
                            key={idx}
                            className="d-flex justify-content-between align-items-center py-2"
                          >
                            <span>{test.title || `Test ${idx + 1}`}</span>
                            <Badge bg="primary" pill>
                              Score: {test.score || 'N/A'}
                            </Badge>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    )}
                  </Card>
                </Col>
              </Row>

              <Row className="mt-5">
                <Col className="text-center">
                  <Button
                    variant="success"
                    size="lg"
                    className="rounded-pill px-4 py-2 shadow"
                    onClick={() => navigate('/take_test')}
                  >
                    🚀 Start New Test
                  </Button>
                </Col>
              </Row>
            </>
          ) : (
            <Alert variant="danger" className="text-center">
              Something went wrong loading your dashboard.
            </Alert>
          )}
        </Card>
      </div>
    </Container>
  );
}

export default StudentDashboard;
