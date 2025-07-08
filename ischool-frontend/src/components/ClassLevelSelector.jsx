import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ClassLevelSelector = ({ onSelect }) => {
  const [classLevels, setClassLevels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("📡 Fetching class levels...");
    axios.get('/api/class-levels/')
      .then(response => {
        console.log("✅ API response:", response);
        if (response.data && Array.isArray(response.data.class_levels)) {
          setClassLevels(response.data.class_levels);
        } else {
          console.warn("⚠️ Unexpected response format:", response.data);
        }
      })
      .catch(error => {
        console.error('❌ Error fetching class levels:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="text-center my-3">
        <div className="spinner-border text-primary" role="status" />
        <p className="mt-2">Loading class levels...</p>
      </div>
    );
  }

  return (
    <div className="mb-4">
      <label htmlFor="classLevelSelect" className="form-label fw-semibold">Select Your Class Level:</label>
      <select
        id="classLevelSelect"
        className="form-select"
        onChange={e => onSelect(e.target.value)}
        defaultValue=""
      >
        <option value="" disabled>--Select Class Level--</option>
        {classLevels.map(level => (
          <option key={level} value={level}>{level}</option>
        ))}
      </select>
    </div>
  );
};

export default ClassLevelSelector;
