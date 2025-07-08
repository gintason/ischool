import React, { useEffect, useState } from 'react';
import axios from 'axios';
import axiosInstance from '../../utils/axiosInstance';
import { useNavigate } from 'react-router-dom';
import {
  FaChalkboardTeacher,
  FaCalendarDay,
  FaUserCheck,
  FaRegCalendarCheck,
  FaSignOutAlt
} from 'react-icons/fa';
import { Button } from 'react-bootstrap';

const TeacherDashboard = () => {
  const navigate = useNavigate();
  const [dailyTimetable, setDailyTimetable] = useState([]);
  const [weeklySummary, setWeeklySummary] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("teacherRole");
    if (!token || role !== "teacher") {
      localStorage.clear();
      navigate("/teacher/login");
      return;
    }
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [timetableRes, upcomingRes, summaryRes, attendanceRes] = await Promise.all([
        axiosInstance.get('daily-timetable/'),
        axiosInstance.get('upcoming-classes/'),
        axiosInstance.get('weekly-summary/'),
        axiosInstance.get('latest-attendance/')
      ]);
      setDailyTimetable(Array.isArray(timetableRes.data) ? timetableRes.data : []);
      setWeeklySummary(summaryRes.data || null);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/teacher/login');
      } else {
        console.error("Dashboard fetch error:", err);
      }
    }
  };

  // ✅ Logout function
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('teacherRole');
    localStorage.removeItem('teacherEmail');
    localStorage.removeItem('teacherName');
    navigate('/teacher/login');
  };

  return (
    <div className="container py-5">
      <div className="d-flex flex-column align-items-center text-center gap-3 mb-5">
  <div>
    <h2 className="fw-bold text-primary mb-2">
      <FaChalkboardTeacher className="me-2" />
      Welcome, Teacher
    </h2>
    <p className="lead text-muted mb-0">
      Manage your schedule, classes, and performance insightfully.
    </p>
  </div>
  
    <Button variant="outline-danger" size="sm" onClick={handleLogout}>
      <FaSignOutAlt className="me-1" />
      Logout
    </Button>
  </div>

      <section className="mb-5 justify-content-center">
        <h4 className="text-secondary mb-4 text-center">
          <div className="d-inline-flex align-items-center justify-content-center gap-2">
            <FaCalendarDay className="text-success" />
            Today’s Timetable
          </div>
        </h4>

        <div className="bg-white rounded-4 shadow-sm p-4 mx-auto" style={{ maxWidth: '960px' }}>
          {dailyTimetable.length === 0 ? (
            <div className="alert alert-info shadow-sm p-3 mb-0">
              No classes scheduled today.
            </div>
          ) : (
            <div className="row row-cols-1 row-cols-md-2 g-4">
              {dailyTimetable.map((item, idx) => (
                <div className="col" key={idx}>
                  <div className="card h-100 border-0 shadow-sm rounded-4 p-3">
                    <div className="card-body">
                      <h5 className="card-title text-primary">{item.subject}</h5>
                      <p className="card-text mb-2">
                        <strong>Class Level:</strong> {item.class_level}
                      </p>
                      <p className="card-text">
                        <strong>Time:</strong> {item.start_time} – {item.end_time}
                      </p>
                      {new Date() >= new Date(`${item.date}T${item.start_time}`) ? (
                        <Button
                          variant="success"
                          size="sm"
                          className="mt-2"
                         onClick={() => navigate(`/teacher/live-session/${item.id}`)}
                        >
                          Join Class
                        </Button>
                      ) : (
                        <span className="badge bg-secondary mt-2">Not started</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="mb-5">
        <h4 className="text-secondary mb-4 text-center">
          <div className="d-inline-flex align-items-center justify-content-center gap-2">
            <FaRegCalendarCheck className="text-warning" />
            Weekly Summary
          </div>
        </h4>

        <div className="bg-white rounded-4 shadow-sm p-4 mx-auto" style={{ maxWidth: '960px' }}>
          {weeklySummary ? (
            <div className="row g-4">
              <div className="col-md-4">
                <div className="card shadow-sm rounded-4 border-0 p-3 h-100">
                  <div className="card-body">
                    <h6 className="card-title text-muted mb-2">Week</h6>
                    <p className="fs-5 fw-semibold text-dark">{weeklySummary.week_range}</p>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card shadow-sm rounded-4 border-0 p-3 h-100">
                  <div className="card-body">
                    <h6 className="card-title text-muted mb-2">Classes Held</h6>
                    <p className="fs-4 text-success fw-bold">{weeklySummary.total_classes_held}</p>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="card shadow-sm rounded-4 border-0 p-3 h-100">
                  <div className="card-body">
                    <h6 className="card-title text-muted mb-2">Students Attended</h6>
                    <p className="fs-4 text-info fw-bold">{weeklySummary.total_students_attended}</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="alert alert-secondary shadow-sm p-3">Loading summary...</div>
          )}
        </div>
      </section>
    </div>
  );
};

export default TeacherDashboard;
