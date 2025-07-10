import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const StudentLessonHistory = () => {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("ole_token");
  const navigate = useNavigate();
  const baseURL = import.meta.env.VITE_API_BASE_URL || "https://ischool-backend.onrender.com/api";

  useEffect(() => {
    if (!token) {
      navigate("/ole_student/login");
      return;
    }

    fetch(`${baseURL}/ole-student/lesson-history/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => setLessons(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [navigate, token]);

  if (loading) return <p className="p-4">Loading lesson history...</p>;

  return (
    <div className="p-5">
      <div className="mb-4">
        <button className="btn btn-outline-primary" onClick={() => navigate("/ole_student/dashboard")}>
          ← Back to Dashboard
        </button>
      </div>

      <h3>Lesson History</h3>

      {lessons.length === 0 ? (
        <p>No previous lessons found.</p>
      ) : (
        lessons.map((lesson) => (
          <div key={lesson.id} className="border rounded p-3 mb-3 bg-light-subtle">
            <p><strong>Subject:</strong> {lesson.subject?.name || "N/A"}</p>
            <p><strong>Topic:</strong> {lesson.topic_title || "N/A"}</p>
            <p><strong>Teacher:</strong> {lesson.teacher?.full_name || "N/A"}</p>
            <p><strong>Viewed On:</strong> {lesson.viewed_on || lesson.date}</p>

            {lesson.materials && lesson.materials.length > 0 && (
              <div>
                <strong>Materials:</strong>
                <ul>
                  {lesson.materials.map((item, i) => (
                    <li key={i}>
                      <a href={item.url} target="_blank" rel="noreferrer">
                        {item.name || item.url}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default StudentLessonHistory;
