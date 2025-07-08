import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Container, Row, Col, Card, Button, Alert } from "react-bootstrap";

const StudentJoinClass = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [attendanceId, setAttendanceId] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const baseURL = import.meta.env.VITE_API_BASE_URL || "https://ischool.ng/api";
  const token = localStorage.getItem("ole_token");
  const oleUser = JSON.parse(localStorage.getItem("ole_user")); // ✅ use local storage for subscription status

  useEffect(() => {
    if (!token) {
      localStorage.removeItem("ole_token");
      navigate("/ole_student/login");
      return;
    }

    if (!lessonId) {
      setErrorMessage("Invalid lesson ID.");
      setLoading(false);
      return;
    }

    fetch(`${baseURL}/users/ole-student/lesson/${lessonId}/`, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
      .then(async (res) => {
        const contentType = res.headers.get("content-type");
        const text = await res.text();

        console.log("📡 Status:", res.status);
        console.log("🧾 Content-Type:", contentType);
        console.log("📦 Raw response body:", text);

        if (!res.ok) {
          throw new Error(`Server error ${res.status}: ${text}`);
        }

        if (!contentType || !contentType.includes("application/json")) {
          throw new Error("Invalid response format. Expected JSON.");
        }

        return JSON.parse(text);
      })
      .then((data) => {
        setLesson(data);

        const sessionId = data.session?.id ?? data.id;
        const meetingLink = data.session?.meeting_link || data.meeting_link;

        // ✅ Only log attendance if there's a valid meeting link
        if (meetingLink) {
          return fetch(`${baseURL}/users/log-join/`, {
            method: "POST",
            headers: {
              Authorization: `Token ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ session_id: sessionId }),
          });
        } else {
          return null;
        }
      })
      .then((res) => (res ? res.json() : null))
      .then((logData) => {
        if (logData?.attendance_id) {
          setAttendanceId(logData.attendance_id);
        }
      })
      .catch((err) => {
        console.error("❌ Error:", err.message);
        if (err.message.includes("403")) {
          setErrorMessage("You are not authorized to join this lesson.");
        } else {
          setErrorMessage("An error occurred while loading the lesson. Please try again.");
        }
      })
      .finally(() => setLoading(false));
  }, [lessonId, navigate, token, baseURL]);

  useEffect(() => {
    const handleBeforeUnload = () => {
      if (!lesson) return;

      const sessionId = lesson.session?.id ?? lesson.id;

      const payload = {
        session_id: sessionId,
      };

      navigator.sendBeacon(
        `${baseURL}/log-leave/`,
        new Blob([JSON.stringify(payload)], { type: "application/json" })
      );
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [lesson, baseURL]);

  if (loading)
    return (
      <div className="p-4 text-center">
        <div className="spinner-border text-success" role="status"></div>
        <p className="mt-2">Fetching lesson details...</p>
      </div>
    );

  if (errorMessage)
    return <p className="p-4 text-danger">❌ {errorMessage}</p>;

  if (!lesson)
    return <p className="p-4 text-danger">Lesson not found or access denied.</p>;

  const canJoin = oleUser?.subscription_status?.is_active;
  const link = lesson.session?.meeting_link || lesson.meeting_link;

  return (
    <Container className="py-5 px-3">
  <Row className="justify-content-center">
    <Col md={10} lg={8}>
      <Card className="shadow-lg rounded-4 p-4 border-0 mt-5 mb-5">
        <Card.Body className="px-md-5 py-4">
          <h4 className="mb-4 text-success fw-bold text-center">
            You're About to Join a Live Class
          </h4>

          <div className="mb-4">
            <Row className="mb-3">
              <Col xs={5}><strong>Subject:</strong></Col>
              <Col xs={7}>{lesson.subject?.name || "N/A"}</Col>
            </Row>

            <Row className="mb-3">
              <Col xs={5}><strong>Teacher:</strong></Col>
              <Col xs={7}>{lesson.teacher?.full_name || "N/A"}</Col>
            </Row>

            <Row className="mb-3">
              <Col xs={5}><strong>Start Time:</strong></Col>
              <Col xs={7}>{lesson.start_time}</Col>
            </Row>
          </div>

          {!canJoin ? (
            <Alert variant="warning" className="text-center px-3 py-2">
              Subscription inactive. Please{" "}
              <Alert.Link href="/ole_student/renew_sub">renew</Alert.Link> to access live classes.
            </Alert>
          ) : link ? (
            <div className="text-center mt-4">
              <Button
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                variant="success"
                size="lg"
                className="px-4 py-2"
              >
                Join Live Class
              </Button>
            </div>
          ) : (
            <p className="text-muted text-center mt-3">
              Live class link not available yet.
            </p>
          )}
        </Card.Body>
      </Card>
    </Col>
  </Row>
</Container>
  );
};

export default StudentJoinClass;
