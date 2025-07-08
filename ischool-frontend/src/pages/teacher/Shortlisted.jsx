import React, { useEffect, useState } from "react";
import axios from "axios";

const Shortlisted = () => {
  const [data, setData] = useState(null);
  const [email, setEmail] = useState("teacher@example.com"); // Replace with auth email
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`/api/teachers/application-status/?email=${email}`);
        setData(res.data);
      } catch (err) {
        setError("Unable to fetch status.");
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, [email]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Application Status</h2>
      <p><strong>Full Name:</strong> {data.full_name}</p>
      <p><strong>Status:</strong> {data.status}</p>
      <p><strong>Subjects:</strong> {data.subjects}</p>
      <p><strong>Submitted:</strong> {new Date(data.applied_at).toLocaleDateString()}</p>
    </div>
  );
};

export default Shortlisted;
