import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaUserGraduate,
  FaCalendarAlt,
  FaSignOutAlt,
  FaBook,
} from "react-icons/fa";

const OleStudentDashboard = () => {
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upcomingLessons, setUpcomingLessons] = useState([]);
  const [lessonHistory, setLessonHistory] = useState([]);
  const [now, setNow] = useState(new Date());

  const baseURL =
    import.meta.env.VITE_API_BASE_URL || "https://www.ischool.ng/api";

  useEffect(() => {
    const rawToken = localStorage.getItem("ole_token");
    if (!rawToken) {
      navigate("/ole_student/login");
      return;
    }

    const token = rawToken.trim();

    const headers = {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    };

    fetch(`${baseURL}/users/ole-student/dashboard/`, {
      method: "GET",
      headers,
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403) {
          localStorage.removeItem("ole_token");
          localStorage.removeItem("ole_user");
          navigate("/ole_student/login");
          throw new Error("Unauthorized");
        }
        return res.json();
      })
      .then((data) => {
        setStudent(data);
        localStorage.setItem("ole_user", JSON.stringify(data));
      })
      .catch((err) => console.error("Dashboard error:", err))
      .finally(() => setLoading(false));

    const fetchLessons = () => {
      fetch(`${baseURL}/teachers/ole-student/upcoming-lessons/`, {
        method: "GET",
        headers,
      })
        .then((res) => res.json())
        .then((data) => {
        // Filter duplicates by lesson ID
        const uniqueLessons = Array.from(
          new Map(data.map((lesson) => [lesson.id, lesson])).values()
        );
        setUpcomingLessons(uniqueLessons);
      })
              .catch((err) => console.error("Upcoming lessons error:", err));
    };

    const fetchHistory = () => {
      fetch(`${baseURL}/teachers/lesson-history/`, {
        method: "GET",
        headers,
      })
        .then((res) => res.json())
        .then((data) => setLessonHistory(data))
        .catch((err) => console.error("Lesson history error:", err));
    };

    fetchLessons();
    fetchHistory();

    const refreshInterval = setInterval(fetchLessons, 30000); // every 30 seconds
    const nowInterval = setInterval(() => setNow(new Date()), 1000); // every 1 second

    return () => {
      clearInterval(refreshInterval);
      clearInterval(nowInterval);
    };
  }, [navigate, baseURL]);

  const handleLogout = () => {
    localStorage.removeItem("ole_token");
    localStorage.removeItem("ole_user");
    navigate("/ole_student/login");
  };

  const renderSubscription = () => {
    if (!student?.subscription_status) return null;
    const { plan_type, is_active, expires_in_days } = student.subscription_status;

    return (
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <h5 className="card-title">📄 Subscription Details</h5>
          <p><strong>Plan:</strong> {plan_type || "N/A"}</p>
          <p><strong>Status:</strong> {is_active ? "✅ Active" : "❌ Inactive"}</p>
          <p><strong>Expires In:</strong> {expires_in_days >= 0 ? `${expires_in_days} days` : "Expired"}</p>
        </div>
      </div>
    );
  };
  

  const renderUpcomingLessons = () => {
  if (!upcomingLessons.length) return <p>No upcoming lessons.</p>;

  return (
    <div className="card shadow-sm mb-4">
      <div className="card-body">
        <h5 className="card-title">
          <FaCalendarAlt className="me-2" />Upcoming Lessons
        </h5>
        <ul className="list-group list-group-flush">
          {upcomingLessons.map((lesson) => {
            const startTime = new Date(`${lesson.date}T${lesson.start_time}`);
            if (isNaN(startTime.getTime())) {
              console.warn("❌ Invalid startTime for lesson:", lesson);
              return null; // skip invalid dates
            }

            const timeDiff = (startTime - now) / 1000;
            const hasStarted = timeDiff <= 0;
            const isStartingSoon = timeDiff > 0 && timeDiff <= 1800;

            // ✅ Use fallback meeting link
            const meetingLink =
              lesson.session?.meeting_link || lesson.meeting_link || "";

            const canJoin = hasStarted && !!meetingLink.trim();

            // ✅ Debug logs for testing
            console.log("📚 Lesson:", lesson.subject);
            console.log("⏱️ TimeDiff:", timeDiff);
            console.log("✅ hasStarted:", hasStarted);
            console.log("🔗 meetingLink:", meetingLink);
            console.log("🟢 canJoin:", canJoin);

            const formatCountdown = (seconds) => {
              const mins = Math.floor(Math.abs(seconds) / 60);
              const secs = Math.floor(Math.abs(seconds) % 60);
              return `${mins}m ${secs < 10 ? "0" : ""}${secs}s`;
            };

            return (
              <li
                className={`list-group-item d-flex justify-content-between align-items-center ${
                  isStartingSoon ? "bg-warning-subtle" : ""
                }`}
                key={lesson.id}
              >
                <div>
                  <strong>{lesson.subject || "Subject"}</strong> with{" "}
                  {lesson.teacher || "Teacher"} on <strong>{lesson.date}</strong>
                  {(isStartingSoon || !hasStarted) && (
                    <span
                      className="badge bg-warning text-dark ms-2 blinking"
                      style={{ animation: "blinker 1s linear infinite" }}
                    >
                      {hasStarted
                        ? "Ongoing"
                        : `Starting in ${formatCountdown(timeDiff)}`}
                    </span>
                  )}
                </div>

                <button
                  className="btn btn-sm btn-success"
                  onClick={() =>
                    navigate(`/ole_student/join-class/${lesson.id}`)
                  }
                  disabled={!canJoin}
                  title={canJoin ? "Join live class" : "Not yet started"}
                >
                  Join
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};


  const renderLessonHistory = () => {
    if (!lessonHistory.length) return <p>No lesson history available.</p>;

    return (
      <div className="card shadow-sm">
        <div className="card-body">
          <h5 className="card-title">
            <FaBook className="me-2" />
            Lesson History
          </h5>
          <ul className="list-group list-group-flush">
            {lessonHistory.map((lesson, idx) => (
              <li className="list-group-item" key={idx}>
                {lesson.topic_title} — Viewed on{" "}
                <strong>{lesson.viewed_on}</strong>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  };

  return (
    <div className="container-fluid">
      <style>
        {`
          @keyframes blinker {
            50% { opacity: 0.4; }
          }
        `}
      </style>
      <div className="row">
        {/* Sidebar */}
        <div className="col-md-3 bg-white shadow-sm vh-100 p-4 d-flex flex-column justify-content-between">
          <div>
            <h4 className="text-primary mb-4">
              <FaUserGraduate className="me-2" />iSchool Ole
            </h4>
            <ul className="nav flex-column">
              <li className="nav-item mb-2">
                <button
                  className="btn btn-outline-primary w-100 text-start"
                  onClick={() => navigate("/ole_student/dashboard")}
                >
                  <FaUserGraduate className="me-2" /> Dashboard
                </button>
              </li>
              <li className="nav-item mb-2">
                <button
                  className="btn btn-outline-secondary w-100 text-start"
                  onClick={() => navigate("/ole_student/lesson-history")}
                >
                  <FaBook className="me-2" /> Lesson History
                </button>
              </li>
            </ul>
          </div>
          <button className="btn btn-danger w-100 mt-4" onClick={handleLogout}>
            <FaSignOutAlt className="me-2" /> Logout
          </button>
        </div>

        {/* Main content */}
        <div className="col-md-9 p-5">
          <h2 className="mb-4">👋 Welcome, Ole Student!</h2>
          {loading ? (
            <div className="text-center mt-5">
              <div className="spinner-border text-primary" role="status"></div>
              <p className="mt-3">Loading student info...</p>
            </div>
          ) : student ? (
            <>
              <div className="card shadow-sm mb-4">
                <div className="card-body">
                  <h5 className="card-title">
                    <FaUserGraduate className="me-2" />Student Info
                  </h5>
                  <p>
                    <strong>Full Name:</strong> {student.full_name}
                  </p>
                  <p>
                    <strong>Email:</strong> {student.email}
                  </p>
                  <p>
                    <strong>Plan:</strong>{" "}
                    {student.plan_type?.toUpperCase() || "N/A"}
                  </p>
                  <p>
                    <strong>Class Level:</strong> {student.class_level}
                  </p>
                  <p>
                    <strong>Subjects:</strong>{" "}
                    {student.subjects?.join(", ")}
                  </p>
                </div>
              </div>
              {renderSubscription()}
              {renderUpcomingLessons()}
              {renderLessonHistory()}
            </>
          ) : (
            <p>Student data not available.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default OleStudentDashboard;
