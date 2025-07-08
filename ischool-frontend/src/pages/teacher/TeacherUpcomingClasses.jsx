import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function TeacherUpcomingClasses() {
  const [data, setData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("api/teachers/dashboard/upcoming-classes/", {
      headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` }
    })
    .then(res => setData(res.data))
    .catch(err => console.error("Error loading upcoming classes:", err));
  }, []);

  const handleStart = (scheduleId) => {
    axios.post(`/teachers/dashboard/start-class/${scheduleId}/`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` }
    })
    .then(res => {
      const { session_id } = res.data;
      navigate(`/teacher/class/${scheduleId}`);  // redirect to live class screen
    })
    .catch(err => {
      alert(err.response?.data?.error || "Cannot start class.");
    });
  };

  return (
    <div className="container mt-4">
      <h3>Upcoming Classes</h3>
      {data.map(group => (
        <div key={`${group.subject}-${group.class_level}`} className="mb-4">
          <h5>{group.subject} – {group.class_level}</h5>
          {group.sessions.map(s => (
            <div key={s.id} className="d-flex justify-content-between align-items-center border-bottom py-2">
              <span>{s.date} | {s.start_time}–{s.end_time}</span>
              <button
                className="btn btn-sm btn-primary"
                onClick={() => handleStart(s.id)}
              >
                Start Class
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
