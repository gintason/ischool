import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Timetable = () => {
  const [timetable, setTimetable] = useState([]);

  useEffect(() => {
  const rawToken = localStorage.getItem('token'); // ✅ fixed

  if (!rawToken) {
    console.warn("❌ No token found in localStorage. Timetable fetch aborted.");
    return;
  }

  const token = rawToken.trim();
  console.log("🔐 Timetable token:", token);

  axios.get('/api/teachers/daily-timetable/', {
    headers: {
      Authorization: `Token ${token}`,
      "Content-Type": "application/json",
    }
  })
  .then(res => {
    console.log("✅ Timetable response:", res.data);
    setTimetable(res.data);
  })
  .catch(err => {
    if (err.response) {
      console.error(`❌ Timetable fetch failed: ${err.response.status} - ${err.response.statusText}`, err.response.data);
    } else {
      console.error("❌ Network error while fetching timetable:", err.message);
    }
  });
}, []);

  return (
    <div className="card mb-4">
      <div className="card-header">Today's Timetable</div>
      <ul className="list-group list-group-flush">
        {timetable.length === 0 ? (
          <li className="list-group-item text-muted">No classes scheduled today</li>
        ) : (
          timetable.map((item, idx) => (
            <li key={idx} className="list-group-item">
              {item.subject} ({item.class_level}) - {item.start_time} to {item.end_time}
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default Timetable;
