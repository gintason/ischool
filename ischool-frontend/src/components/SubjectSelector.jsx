import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SubjectSelector = ({ classLevel, onSelect }) => {
  console.log("Rendering SubjectsSelector");
  const [subjects, setSubjects] = useState([]);

  useEffect(() => {
    if (classLevel) {
      axios.get(`/api/subjects/?class_level=${classLevel}`)
        .then(response => setSubjects(response.data.subjects))
        .catch(error => console.error('Error fetching subjects:', error));
    }
  }, [classLevel]);

  return (
    <div className="mb-4">
      <label htmlFor="subjectSelect" className="form-label fw-semibold">Select Subject:</label>
      <select
        id="subjectSelect"
        className="form-select"
        onChange={e => onSelect(e.target.value)}
        defaultValue=""
      >
        <option value="" disabled>--Select Subject--</option>
        {subjects.map(subject => (
          <option key={subject} value={subject}>{subject}</option>
        ))}
      </select>
    </div>
  );
};

export default SubjectSelector;

