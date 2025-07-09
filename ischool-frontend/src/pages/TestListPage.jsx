// src/pages/TestListPage.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Container, Card, Button, Spinner, Alert } from 'react-bootstrap';

function TestListPage() {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    axios.get('https://www.ischool.ng/api/tests/', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((res) => {
      setTests(res.data);
      setLoading(false);
    })
    .catch((err) => {
      console.error('Failed to load tests', err);
      setLoading(false);
    });
  }, [navigate]);

  if (loading) {
    return (
      <Container className="mt-5 text-center">
        <Spinner animation="border" />
      </Container>
    );
  }

  if (tests.length === 0) {
    return (
      <Container className="mt-5">
        <Alert variant="info">No tests available yet.</Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-5">
      <h2>📋 Available Tests</h2>
      {tests.map((test) => (
        <Card className="my-3" key={test.id}>
          <Card.Body>
            <Card.Title>{test.topic}</Card.Title>
            <Card.Text>
              Subject: {test.subject} <br />
              Class: {test.class_level}
            </Card.Text>
            <Button onClick={() => navigate(`/test/${test.id}`)}>
              Start Test
            </Button>
          </Card.Body>
        </Card>
      ))}
    </Container>
  );
}

export default TestListPage;
