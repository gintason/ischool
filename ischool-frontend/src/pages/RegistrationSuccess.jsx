import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CenteredToast from '../components/CenteredToast';

const RegistrationSuccess = () => {
  const [showToast, setShowToast] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setShowToast(true);
    const timer = setTimeout(() => {
      navigate('/student/login');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <>
      {showToast && <CenteredToast message="Registration completed successfully! Please check your email for login credentials" />}
      <div className="text-center mt-5">
        <h3>Redirecting to login page...</h3>
      </div>
    </>
  );
};

export default RegistrationSuccess;
