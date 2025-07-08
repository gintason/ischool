import React, { useState, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import { getDecodedUser } from '../utils/auth';
import { Outlet } from 'react-router-dom'; // ✅ Add this import

const Layout = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const user = getDecodedUser();
    setIsLoggedIn(!!user); // true if valid user exists
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setIsLoggedIn(false);
    window.location.reload(); // force UI update if not using React Context
  };

  return (
    <>
      <Header isLoggedIn={isLoggedIn} onLogout={handleLogout} />
      <main style={{ minHeight: '100vh', padding: '0px' }}>
        <Outlet /> {/* ✅ This renders nested route content */}
      </main>
      <Footer />
    </>
  );
};

export default Layout;
