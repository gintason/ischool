import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import OleLayout from './components/OleLayout'; // ✅ import OleLayout

// Page Imports
import SignUpPage from './pages/SignUpPage';
import HomePage from './pages/HomePage';
import StudentLogin from './pages/student/StudentLogin';
import StudentDashboard from './pages/StudentDashboard';
import OnboardingPage from "./pages/OnboardingPage";
import TestPage from './pages/TestPage';
import ContactPage from './pages/ContactPage';
import AboutUsPage from './pages/AboutUsPage';
import NewsPage from './pages/NewsPage';
import NewsDetailPage from './pages/NewsDetailPage';
import TestListPage from './pages/TestListPage';
import ErrorBoundary from './pages/ErrorBoundary';
import RegistrationSuccess from './pages/RegistrationSuccess';

import Apply from './pages/teacher/Apply';
import Shortlisted from './pages/teacher/Shortlisted';
import TeacherDashboard from './pages/teacher/TeacherDashboard';
import TeacherLogin from "./pages/teacher/TeacherLogin";
import TeacherPrivateRoute from "./pages/teacher/components/TeacherPrivateRoute";
import TeacherUpcomingClasses from './pages/teacher/TeacherUpcomingClasses';
import LiveClassSession from './pages/teacher/LiveClassSession';

import OleStudentRegister from './pages/ole_student/OleStudentRegister';
import OlePaymentVerification from './pages/ole_student/OlePaymentVerification';
import OleStudentLogin from './pages/ole_student/OleStudentLogin';
import OleStudentDashboard from './pages/ole_student/OleStudentDashboard';
import OleStudentLessonHistory from "./pages/ole_student/OleStudentLessonHistory";
import RenewSubscription from "./pages/ole_student/RenewSubscription";
import StudentJoinClass from "./pages/ole_student/StudentJoinClass";
import OleHome from "./pages/teacher/OleHome";
import AboutOle from "./pages/AboutOle";
import ContactOle from "./pages/ContactOle";
import OleHow from "./pages/OleHow";

import OleStudentPrivateRoute from "./components/OleStudentPrivateRoute";

function App() {
  return (
    <Router>
      <Routes>
         {/* === Onboarding Page (No Layout) === */}
        <Route path="/" element={<OnboardingPage />} />

        {/* === General Public Pages wrapped with default Layout === */}
        <Route element={<Layout />}>
          <Route path="/ola_home" element={<HomePage />} />
          <Route path="/about_us" element={<AboutUsPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/news/:id" element={<NewsDetailPage />} />
          <Route path="/sign_up" element={<SignUpPage />} />
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/student_dash" element={<StudentDashboard />} />
          <Route path="/take_test" element={<ErrorBoundary><TestPage /></ErrorBoundary>} />
          <Route path="/tests" element={<TestListPage />} />
          <Route path="/registration_success" element={<RegistrationSuccess />} />
         
        </Route>

        {/* === Ole Student Pages wrapped with OleLayout === */}
        <Route element={<OleLayout />}>
          <Route path="/teacher/login" element={<TeacherLogin />} />
          <Route path="/ole_student/register" element={<OleStudentRegister />} />
          <Route path="/ole_student/login" element={<OleStudentLogin />} />
          <Route path="/ole-subscription/verify" element={<OlePaymentVerification />} />
          <Route path="/ole_student/lesson-history" element={<OleStudentLessonHistory />} />
          <Route path="/ole_student/renew_sub" element={<RenewSubscription />} />
          <Route path="/ole_student/join-class/:lessonId" element={<StudentJoinClass />} />
          <Route path="/ole_home" element={<OleHome />} />
          <Route path="/about_ole" element={<AboutOle />} />
          <Route path="/contact_ole" element={<ContactOle />} />
          <Route path="/ole_how" element={<OleHow />} />
          <Route path="/teacher/apply" element={<Apply />} />
          <Route path="/ole_student/dashboard" element={<OleStudentDashboard />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/shortlisted" element={<Shortlisted />} />
          <Route path="/teacher/upcoming-classes" element={<TeacherUpcomingClasses />} />
         <Route path="/teacher/live-session/:scheduleId" element={<LiveClassSession />} />
        </Route>

        {/* === Protected Ole Student Dashboard === */}
        <Route element={<OleStudentPrivateRoute />}>
       
        </Route>

        <Route element={<TeacherPrivateRoute />}>
         
        </Route>

        {/* === Fallback Route === */}
        <Route path="*" element={<h2>Tests Coming Soon</h2>} />
      </Routes>
    </Router>
  );
}

export default App;
