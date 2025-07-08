import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TopicSelector = ({ classLevel, subject, onSelect }) => {
  console.log("Rendering TopicSelector");
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    if (classLevel && subject) {
      axios.get(`/api/topics/?class_level=${classLevel}&subject=${subject}`)
        .then(response => setTopics(response.data.topics))
        .catch(error => console.error('Error fetching topics:', error));
    }
  }, [classLevel, subject]);

  return (
    <div className="mb-4">
      <label htmlFor="topicSelect" className="form-label fw-semibold">Select Topic:</label>
      <select
        id="topicSelect"
        className="form-select"
        onChange={e => onSelect(e.target.value)}
        defaultValue=""
      >
        <option value="" disabled>--Select Topic--</option>
        {topics.map(topic => (
          <option key={topic} value={topic}>{topic}</option>
        ))}
      </select>
    </div>
  );
};

export default TopicSelector;
