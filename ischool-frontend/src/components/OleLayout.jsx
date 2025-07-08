import React, { useState, useEffect } from 'react';
import OleHeader from './OleHeader';
import OleFooter from './OleFooter';
import { getDecodedUser } from '../utils/auth';
import { Outlet } from 'react-router-dom'; // ✅ Import Outlet for nested routing

const OleLayout = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const user = getDecodedUser();
    setIsLoggedIn(!!user);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setIsLoggedIn(false);
    window.location.reload();
  };

  return (
    <>
      <OleHeader isLoggedIn={isLoggedIn} onLogout={handleLogout} />

      <main className="container-fluid px-0 mx-0" style={{ minHeight: '100vh' }}>
        <Outlet /> {/* ✅ Inject routed page content here */}
      </main>

      <OleFooter />
    </>
  );
};

export default OleLayout;
