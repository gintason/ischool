import React, { useEffect, useState } from 'react';
import axios from 'axios';

const UpcomingClasses = () => {
  const [groupedClasses, setGroupedClasses] = useState([]);

  useEffect(() => {
    axios.get('https://api.ischool.ng/api/teachers/upcoming-classes/')
      .then(res => setGroupedClasses(res.data))
      .catch(err => console.error(err));
  }, []);

  const startClass = async (scheduleId) => {
    try {
      const res = await axios.post(`https://api.ischool.ng/api/teachers/start-class/${scheduleId}/`);
      alert("Class started. Meeting link: " + res.data.meeting_link);
    } catch (err) {
      console.error(err);
      alert("Error starting class");
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-header">Upcoming Classes</div>
      <div className="card-body">
        {groupedClasses.map((group, idx) => (
          <div key={idx} className="mb-3">
            <h5>{group.class_level} - {group.subject}</h5>
            <ul className="list-group">
              {group.classes.map(cls => (
                <li key={cls.id} className="list-group-item d-flex justify-content-between align-items-center">
                  {cls.date} ({cls.start_time} - {cls.end_time})
                  <button className="btn btn-sm btn-primary" onClick={() => startClass(cls.id)}>
                    Start Class
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UpcomingClasses;
