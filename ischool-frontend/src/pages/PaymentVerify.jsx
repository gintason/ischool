// src/pages/PaymentVerify.jsx
import { useEffect } from 'react';
import axios from 'axios';
import { useLocation, useNavigate } from 'react-router-dom';

const PaymentVerify = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const transaction_id = queryParams.get('transaction_id');
  const tx_ref = queryParams.get('tx_ref');

  useEffect(() => {
    const verifyAndRegister = async () => {
      try {
        const registrationData = JSON.parse(localStorage.getItem("signupData"));
        if (!registrationData) {
          alert("Missing registration data. Please try again.");
          return;
        }

        const res = await axios.post('https://www.ischool.ng/api/payments/api/verify-and-register/', {
          ...registrationData,
          transaction_id,
          tx_ref,
        });

        alert("🎉 Registration complete. Login details sent via email.");
        localStorage.removeItem("signupData");
        navigate('/success');  // Redirect to success page
      } catch (error) {
        console.error("Verification error:", error);
        alert("❌ Verification failed. Please contact support.");
      }
    };

    if (transaction_id && tx_ref) {
      verifyAndRegister();
    }
  }, [transaction_id, tx_ref, navigate]);

  return <p>⏳ Verifying payment and completing registration...</p>;
};

export default PaymentVerify;
