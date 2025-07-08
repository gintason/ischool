import React, { useEffect, useState } from 'react';
import axios from 'axios';

const WeeklySummary = () => {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    axios.get('/api/teachers/weekly-summary/')
      .then(res => setSummary(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="card mb-4">
      <div className="card-header">📊 This Week's Summary</div>
      <div className="card-body">
        {summary ? (
          <>
            <p><strong>Week:</strong> {summary.week_range}</p>
            <p><strong>Classes Held:</strong> {summary.total_classes_held}</p>
            <p><strong>Students Attended:</strong> {summary.total_students_attended}</p>
          </>
        ) : (
          <p className="text-muted">Loading summary...</p>
        )}
      </div>
    </div>
  );
};

export default WeeklySummary;
