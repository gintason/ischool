import React, { useEffect, useState } from "react";
import axios from "axios";

const RenewSubscription = () => {
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [token, setToken] = useState("");
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    setToken(localStorage.getItem("ole_token"));
    setUserEmail(localStorage.getItem("ole_email"));
    axios
      .get(`${process.env.REACT_APP_API_BASE_URL}/ole-student/subscription-plans/`)
      .then((res) => setPlans(res.data))
      .catch((err) => console.error(err));
  }, []);

  const handleRenew = async () => {
    if (!selectedPlanId || !token) {
      alert("Select a plan before proceeding.");
      return;
    }

    try {
      const initRes = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/ole-student/init-subscription/`,
        { plan_id: selectedPlanId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const { reference, amount, email, public_key, metadata } = initRes.data;

      const handler = window.PaystackPop && window.PaystackPop.setup({
        key: public_key,
        email,
        amount,
        ref: reference,
        metadata, // ✅ use metadata from backend
        callback: async (response) => {
          try {
            await axios.post(
              `${process.env.REACT_APP_API_BASE_URL}/ole-student/verify-subscription-payment/`,
              { reference: response.reference },
              { headers: { Authorization: `Bearer ${token}` } }
            );
            alert("Subscription renewed successfully!");
            window.location.href = "/ole_student/dashboard";
          } catch (err) {
            alert("Verification failed. Please contact support.");
          }
        },
        onClose: () => {
          alert("Payment window closed.");
        },
      });

      if (handler) handler.openIframe();
    } catch (err) {
      alert("Could not initiate payment. Please try again.");
    }
  };

  return (
    <div className="container mt-4">
      <h2>Select a Subscription Plan</h2>
      <select
        className="form-control mb-3"
        value={selectedPlanId}
        onChange={(e) => setSelectedPlanId(e.target.value)}
      >
        <option value="">-- Select Plan --</option>
        {plans.map((plan) => (
          <option key={plan.id} value={plan.id}>
            {plan.name} - ₦{plan.amount / 100}
          </option>
        ))}
      </select>
      <button className="btn btn-primary" onClick={handleRenew}>
        Renew Now
      </button>
    </div>
  );
};

export default RenewSubscription;
