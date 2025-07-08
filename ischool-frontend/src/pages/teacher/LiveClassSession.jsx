import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Badge,
  Spinner,
} from "react-bootstrap";
import axiosInstance from "../../utils/axiosInstance";

export default function LiveClassSession() {
  const { scheduleId } = useParams();
  const [session, setSession] = useState(null);
  const [lessonPlans, setLessonPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [markingCompleted, setMarkingCompleted] = useState(false);

  useEffect(() => {
    const accessToken = localStorage.getItem("accessToken");

    axiosInstance
      .post(`dashboard/start-class/${scheduleId}/`, {}, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        fetchSessionDetails(res.data.session_id, accessToken);
      })
      .catch((err) => {
        const errorMsg = err.response?.data?.error || err.message;
        if (errorMsg === "Class session already started.") {
          fetchSessionDetails(scheduleId, accessToken);
        } else {
          alert("Error starting session: " + errorMsg);
        }
      });
  }, [scheduleId]);

  const fetchSessionDetails = (sessionId, token) => {
    axiosInstance
      .get(`dashboard/session-detail/${sessionId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setSession(res.data);
        if (!res.data.lesson_plan) {
          fetchLessonPlans(res.data.subject_id, res.data.class_level_id);
        }
      });
  };

  const fetchLessonPlans = (subjectId, classLevelId) => {
    const accessToken = localStorage.getItem("accessToken");

    axiosInstance
      .get(`dashboard/lesson-plans/?subject=${subjectId}&class_level=${classLevelId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        if (Array.isArray(res.data)) {
          setLessonPlans(res.data);
        } else if (Array.isArray(res.data.results)) {
          setLessonPlans(res.data.results);
        } else {
          setLessonPlans([]);
        }
      });
  };

  const handleSelectPlan = () => {
    if (!selectedPlanId) return;

    const accessToken = localStorage.getItem("accessToken");

    axiosInstance
      .post(`dashboard/set-lesson-plan/${session.id}/`, {
        lesson_plan_id: selectedPlanId,
      }, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then((res) => {
        alert("Lesson plan set!");
        setSession((prev) => ({
          ...prev,
          lesson_plan: res.data.lesson_plan,
        }));
      });
  };

  const handleMarkCompleted = () => {
    const accessToken = localStorage.getItem("accessToken");
    setMarkingCompleted(true);

    axiosInstance
      .post(`dashboard/mark-completed/${session.id}/`, {}, {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then(() => {
        setSession((prev) => ({ ...prev, completed: true }));
      })
      .catch((err) => {
        alert("Failed to mark as completed.");
        console.error(err);
      })
      .finally(() => setMarkingCompleted(false));
  };

  if (!session) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">Loading session...</p>
      </Container>
    );
  }

  return (
    <Container className="py-5 ms-5 me-5">
      <Row className="mb-4 ms-5 me-5">
        <Col>
          <h2 className="text-danger fw-bold">Ole Live Class Session</h2>
          <p className="text-muted mb-1">
            <strong>Subject:</strong> {session.subject} &nbsp; | &nbsp;
            <strong>Class:</strong> {session.class_level}
          </p>
          <p className="text-muted">
            <strong>Date:</strong> {session.date} &nbsp; | &nbsp;
            <strong>Time:</strong> {session.start_time} - {session.end_time}
          </p>
        </Col>
      </Row>

      <Row className="mb-4 ms-5 me-5">
        <Col md={6}>
          <Card className="shadow-sm border-0">
            <Card.Body>
              <Card.Title className="mb-3 text-primary">Lesson Plan</Card.Title>
              {session.lesson_plan ? (
                <Card.Text className="text-muted fs-6">
                  {session.lesson_plan.topic}
                </Card.Text>
              ) : (
                <>
                  <Form.Group controlId="lessonPlanSelect">
                    <Form.Label>Select a Lesson Topic</Form.Label>
                    <Form.Select
                      value={selectedPlanId || ""}
                      onChange={(e) => setSelectedPlanId(e.target.value)}
                    >
                      <option value="">-- Choose Topic --</option>
                      {lessonPlans.map((plan) => (
                        <option key={plan.id} value={plan.id}>
                          {plan.topic}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                  <div className="d-grid mt-3">
                    <Button
                      variant="primary"
                      onClick={handleSelectPlan}
                      disabled={!selectedPlanId}
                    >
                      Assign Lesson Plan
                    </Button>
                  </div>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="shadow-sm border-0">
            <Card.Body>
              <Card.Title className="mb-3 text-primary">Lesson Status</Card.Title>
              {session.completed ? (
                <Badge bg="success" className="fs-6 px-3 py-2">
                  Completed
                </Badge>
              ) : (
                <>
                  <Badge bg="warning" text="dark" className="fs-6 px-3 py-2">
                    In Progress
                  </Badge>
                  <div className="d-grid mt-3">
                    <Button
                      variant="outline-success"
                      onClick={handleMarkCompleted}
                      disabled={markingCompleted}
                    >
                      {markingCompleted ? "Marking..." : "Mark Lesson as Completed"}
                    </Button>
                  </div>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {session.meeting_link && (
        <Row className="mt-4 ms-3 me-3">
          <Col>
            <Card className="shadow-sm border-0">
              <Card.Body>
                <Card.Title className="mb-3 text-danger">Ole Live Class Video</Card.Title>
                <div className="ratio ratio-16x9">
                  <iframe
                    src={session.meeting_link}
                    allow="camera; microphone; fullscreen; display-capture"
                    style={{ border: 0 }}
                    title="Live Class Video"
                    allowFullScreen
                    aria-label="Live class video"
                  ></iframe>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {!session.meeting_link && (
        <Row className="mt-4">
          <Col>
            <p className="text-muted text-center">Video will be available once the session starts.</p>
          </Col>
        </Row>
      )}
    </Container>
  );
}
