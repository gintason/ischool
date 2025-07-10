import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { Form, Button, Container, Row, Col, Card } from 'react-bootstrap';
import { v4 as uuidv4 } from 'uuid';
import { FaUserPlus } from 'react-icons/fa';
import './styles/SignUpPage.css';
import CenteredToast from '../components/CenteredToast';
import bgImage from '../assets/signup-bg.png';

const SLOT_PRICE_MONTHLY = 6100;
const SLOT_PRICE_YEARLY = 52000;

const SignUpPage = () => {
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [formData, setFormData] = useState({
    accountType: '',
    state: '',
    slots: 1,
    name: '',
    location: '',
    email: '',
    referralCode: '',
    accountDetails: '',
    billingCycle: 'monthly'
  });

  const [studentDetails, setStudentDetails] = useState([{ fullName: '', email: '' }]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.body.style.overflow = loading ? 'hidden' : 'auto';
  }, [loading]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData(prev => ({
      ...prev,
      [name]: name === "email" ? value.trim().toLowerCase() : value
    }));

    if (name === 'slots') {
      const newSlotCount = Math.max(parseInt(value) || 1, 1);
      const updatedStudentFields = [...studentDetails];

      while (updatedStudentFields.length < newSlotCount) {
        updatedStudentFields.push({ fullName: '', email: '' });
      }

      while (updatedStudentFields.length > newSlotCount) {
        updatedStudentFields.pop();
      }

      setStudentDetails(updatedStudentFields);
    }
  };

  const handleStudentChange = (index, field, value) => {
    const updatedStudents = [...studentDetails];
    updatedStudents[index][field] = field === 'email' ? value.trim().toLowerCase() : value;
    setStudentDetails(updatedStudents);
  };

  const handlePaystackPayment = () => {
    const tx_ref = String(uuidv4());
    const slots = Math.max(parseInt(formData.slots, 10) || 1, 1);
    const isYearly = formData.billingCycle === 'yearly';
    const slotAmount = isYearly ? SLOT_PRICE_YEARLY : SLOT_PRICE_MONTHLY;
    const totalAmount = slots * slotAmount;

    setTimeout(() => {
      setLoading(true);

      const handler = window.PaystackPop.setup({
        key:'pk_live_aac354a9d3f777557dc1e0e6be5f84700210f358',
        email: formData.email || '',
        amount: totalAmount * 100,
        currency: 'NGN',
        ref: tx_ref,
        callback: function (response) {
          if (response.status === "success" || response.message === "Approved") {
            handleSuccessfulPayment(response, tx_ref, slots);
          } else {
            setLoading(false);
            setToastMessage("Payment was not successful. Please try again.");
            setShowToast(true);
          }
        },
        onClose: () => {
          setLoading(false);
        },
      });

      handler.openIframe();
    }, 100);
  };

  const handleSuccessfulPayment = async (response, tx_ref, slots) => {
    const payload = {
      transaction_id: response.reference,
      tx_ref: tx_ref,
      email: formData.email || '',
      account_type: formData.accountType || '',
      state: formData.state || '',
      slots,
      name: formData.name || '',
      location: formData.location || '',
      referral_code: formData.referralCode || '',
      account_details: formData.accountDetails || '',
      billing_cycle: formData.billingCycle,
      studentDetails: studentDetails.map(student => ({
        fullName: student.fullName || '',
        email: student.email || '',
      }))
    };

    try {
      await axios.post(
        'https://ischool-backend.onrender.com/api/payments/verify-and-register/',
        payload
      );
      setToastMessage('Registration completed successfully! Please check your email for Student(s) login details');
      setShowToast(true);
      setLoading(false);
      setTimeout(() => {
        window.location.href = "/student/login";
      }, 3500);
    } catch (err) {
      setToastMessage('Payment was successful, but registration failed. Please contact support.');
      setShowToast(true);
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (loading) return;
    handlePaystackPayment();
  };

  const perSlotAmount = formData.billingCycle === 'yearly' ? SLOT_PRICE_YEARLY : SLOT_PRICE_MONTHLY;
  const totalAmount = formData.slots * perSlotAmount;

  return (
    <>
      <div
        className="signup-page-wrapper"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          minHeight: '100vh',
          width: '100vw',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          margin: 0,
          padding: 0,
        }}
      >
        <Container className="d-flex justify-content-center mt-5 mb-5 pt-5 pb-5">
          <Card className="p-4 signup-card shadow-lg" style={{ width: '100%', maxWidth: '600px' }}>
            <h3 className="text-center mb-4 text-primary">
              <FaUserPlus className="me-2" />
              Register & Pay for Slots
            </h3>
            <Form onSubmit={handleSubmit} className="w-100" noValidate>
              <Row className="mb-3">
                <Form.Group as={Col} controlId="formGridAccountType">
                  <Form.Label>Account Type</Form.Label>
                  <Form.Select name="accountType" value={formData.accountType} onChange={handleChange} required>
                    <option value="">Choose...</option>
                    <option value="school">School</option>
                    <option value="home">Home</option>
                    <option value="referral">Accredited Referral</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group as={Col} controlId="formGridState">
                  <Form.Label>State</Form.Label>
                  <Form.Control type="text" name="state" value={formData.state} onChange={handleChange} required />
                </Form.Group>
              </Row>

              <Form.Group className="mb-3" controlId="formGridName">
                <Form.Label>Organization/Name</Form.Label>
                <Form.Control type="text" name="name" value={formData.name} onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="formGridLocation">
                <Form.Label>Location</Form.Label>
                <Form.Control type="text" name="location" value={formData.location} onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="formGridEmail">
                <Form.Label>Email</Form.Label>
                <Form.Control type="email" name="email" value={formData.email} onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3" controlId="formGridSlots">
                <Form.Label>Number of Slots</Form.Label>
                <Form.Control
                  type="number"
                  name="slots"
                  value={formData.slots}
                  onChange={handleChange}
                  min={1}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3" controlId="formGridBillingCycle">
                <Form.Label>Billing Cycle</Form.Label>
                <Form.Select name="billingCycle" value={formData.billingCycle} onChange={handleChange} required>
                  <option value="monthly">Monthly - ₦6,100</option>
                  <option value="yearly">Yearly - ₦52,000</option>
                </Form.Select>
              </Form.Group>

              <div className="mb-3 p-3 border rounded bg-light">
                <h6 className="mb-2 text-primary">Payment Summary</h6>
                <p className="mb-1"><strong>Slots:</strong> {formData.slots}</p>
                <p className="mb-1"><strong>Plan:</strong> {formData.billingCycle === 'yearly' ? 'Yearly' : 'Monthly'}</p>
                <p className="mb-1"><strong>Amount per Slot:</strong> ₦{perSlotAmount.toLocaleString()}</p>
                <p className="mb-0"><strong>Total:</strong>{' '}
                  <span className="text-success">₦{totalAmount.toLocaleString()}</span>
                </p>
              </div>

              {studentDetails.map((student, index) => (
                <div key={index} className="mb-3 border rounded p-3 bg-light">
                  <h6>Student {index + 1}</h6>
                  <Form.Group className="mb-2" controlId={`studentFullName${index}`}>
                    <Form.Label>Full Name</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Enter full name"
                      value={student.fullName}
                      onChange={(e) => handleStudentChange(index, 'fullName', e.target.value)}
                      required
                    />
                  </Form.Group>
                  <Form.Group className="mb-2" controlId={`studentEmail${index}`}>
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      placeholder="Enter email"
                      value={student.email}
                      onChange={(e) => handleStudentChange(index, 'email', e.target.value)}
                      required
                    />
                  </Form.Group>
                </div>
              ))}

              {formData.accountType === 'referral' && (
                <>
                  <Form.Group className="mb-3" controlId="formGridReferralCode">
                    <Form.Label>Referral Code</Form.Label>
                    <Form.Control type="text" name="referralCode" value={formData.referralCode} onChange={handleChange} />
                  </Form.Group>

                  <Form.Group className="mb-3" controlId="formGridAccountDetails">
                    <Form.Label>Account Details</Form.Label>
                    <Form.Control type="text" name="accountDetails" value={formData.accountDetails} onChange={handleChange} />
                  </Form.Group>
                </>
              )}

              <Button variant="primary" type="submit" disabled={loading} className="w-100 mt-2">
                {loading ? 'Initializing Payment...' : 'Proceed to Payment'}
              </Button>
            </Form>
          </Card>
        </Container>
      </div>

      {showToast && (
        <CenteredToast
          message={toastMessage}
          onClose={() => setShowToast(false)}
        />
      )}

      {loading && (
        <div className="overlay-spinner">
          <div className="spinner-border text-light" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}
    </>
  );
};

export default SignUpPage;
