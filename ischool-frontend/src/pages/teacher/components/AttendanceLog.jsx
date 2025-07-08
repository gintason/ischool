import React, { useEffect, useState } from 'react';
import axios from 'axios';

const AttendanceLog = () => {
  const [log, setLog] = useState([]);

  useEffect(() => {
    axios.get('/api/teachers/latest-attendance/')
      .then(res => setLog(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="card mb-4">
      <div className="card-header">📋 Latest Class Attendance</div>
      <ul className="list-group list-group-flush">
        {log.length === 0 ? (
          <li className="list-group-item text-muted">No attendance yet</li>
        ) : (
          log.map((entry, idx) => (
            <li key={idx} className="list-group-item">
              <strong>{entry.student}</strong> - {entry.subject} ({entry.class_level})<br />
              Joined at: {new Date(entry.joined_at).toLocaleString()}
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default AttendanceLog;
