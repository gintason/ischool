import React, { useEffect, useRef, useState } from 'react';
import './styles/CenteredToast.css';

const CenteredToast = ({ message, onClose, duration = 3000 }) => {
  const [fadingOut, setFadingOut] = useState(false);
  const toastRef = useRef();

  useEffect(() => {
    const timer = setTimeout(() => {
      setFadingOut(true);
      setTimeout(onClose, 300); // match with fadeOut duration
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div
      className="centered-toast"
      style={{ animation: fadingOut ? 'fadeOut 0.3s ease-out forwards' : '' }}
    >
      <div className="toast-content">
        🎉 {message}
      </div>
    </div>
  );
};

export default CenteredToast;

