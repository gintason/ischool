import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";


const OlePaymentVerify = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [status, setStatus] = useState("verifying"); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState("");
  const [loginDetails, setLoginDetails] = useState(null);

  const getQueryParams = () => new URLSearchParams(location.search);

  useEffect(() => {
    const query = getQueryParams();
    const reference = query.get("reference");

    if (!reference) {
      setStatus("error");
      setMessage("Missing payment reference.");
      return;
    }

    const verifiedKey = `verified_${reference}`;
    const alreadyVerified = localStorage.getItem(verifiedKey);

    if (alreadyVerified) {
      setStatus("success");
      setMessage("You have already verified your payment.");
      setLoginDetails({ email: "", password: null });
      setTimeout(() => navigate("/ole_student/login"), 5000);
      return;
    }

    const verifyPayment = async () => {
      try {
        const response = await axios.post("https://api.ischool.ng/api/users/ole-student/verify-payment/", {
          reference
        });

        if (response.status === 201 || response.status === 200) {
          const isNew = response.status === 201;
          setStatus("success");
          setMessage(response.data.message);

          setLoginDetails({
            email: response.data.email,
            password: response.data.temporary_password ?? null,
          });

          localStorage.setItem(verifiedKey, "true");

          setTimeout(() => {
            navigate("/ole_student/login");
          }, 10000);
        } else {
          setStatus("error");
          setMessage(response.data.error || "Payment verification failed.");
        }
      } catch (error) {
        setStatus("error");
        setMessage(error.response?.data?.error || "Verification service unavailable.");
      }
    };

    verifyPayment();
  }, [location.search, navigate]);

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow-lg border-0 mb-5">
            <div className="card-body p-5 text-center">
              {status === "verifying" && (
                <>
                  <div className="spinner-border text-primary mb-4" role="status" />
                  <h5 className="mb-3">Verifying Payment</h5>
                  <p className="text-muted">Please wait while we confirm your transaction...</p>
                </>
              )}

              {status === "success" && (
                <>
                  <div className="text-success mb-4" style={{ fontSize: "2rem" }}>
                    <i className="bi bi-check-circle-fill"></i>
                  </div>
                  <h4 className="fw-bold mb-3">Payment Verified Successfully!</h4>
                  <p className="mb-3">{message}</p>
                  {loginDetails?.password ? (
                    <div className="alert alert-light border">
                      <p className="mb-1"><strong>Email:</strong> {loginDetails.email}</p>
                      <p className="mb-0"><strong>Password:</strong> {loginDetails.password}</p>
                    </div>
                  ) : (
                    <p className="text-muted">Use your existing login details to sign in.</p>
                  )}
                  <p className="text-muted mt-4">You will be redirected to login shortly...</p>
                </>
              )}

              {status === "error" && (
                <>
                  <div className="text-danger mb-4" style={{ fontSize: "2rem" }}>
                    <i className="bi bi-x-circle-fill"></i>
                  </div>
                  <h4 className="fw-bold mb-3">Payment Verification Failed</h4>
                  <p className="mb-3">{message}</p>
                  <p className="text-muted">Please try again or contact support.</p>
                  <button
                    className="btn btn-outline-danger mt-4"
                    onClick={() => window.location.reload()}
                  >
                    <i className="bi bi-arrow-clockwise me-2"></i>Try Again
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OlePaymentVerify;
