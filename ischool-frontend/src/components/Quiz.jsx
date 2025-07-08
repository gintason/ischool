import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles/Quiz.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Quiz = ({ classLevel, subject, topic }) => {
  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchQuestions = async () => {
      if (!classLevel || !subject || !topic) return;

      const token = localStorage.getItem("token");

      if (!token) {
        alert("You are not logged in. Please log in first.");
        window.location.href = "/student/login";
        return;
      }

      try {
        const response = await axios.post('/api/start/', {
          class_level: classLevel,
          subject,
          topic
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSessionId(response.data.session_id);
        setQuestions(response.data.questions);
      } catch (error) {
        console.error('Error starting test:', error.response?.data || error.message);
        if (error.response?.status === 401) {
          alert("Session expired. Please log in again.");
          localStorage.removeItem("token");
          window.location.href = "/student/login";
        }
      }
    };

    fetchQuestions();
  }, [classLevel, subject, topic]);

  useEffect(() => {
    if (timeLeft <= 0) {
      handleFinalSubmit(); // auto-submit when time runs out
      return;
    }
    const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleAnswer = (answer) => {
    setSelectedAnswer(answer);
  };

  const handleNext = () => {
    if (!selectedAnswer) {
      toast.error("Please select an answer before proceeding.", { position: "top-center" });
      return;
    }

    const question = questions[currentQuestionIdx];
    setAnswers(prev => [...prev, { question_id: question.id, answer: selectedAnswer }]);
    setSelectedAnswer('');
    setCurrentQuestionIdx(prev => prev + 1);
  };

  const handleFinalSubmit = async () => {
    if (!selectedAnswer) {
      toast.error("Please select an answer before submitting.", { position: "top-center" });
      return;
    }

    const token = localStorage.getItem("token");
    setIsSubmitting(true);

    const finalAnswers = [...answers, {
      question_id: questions[currentQuestionIdx].id,
      answer: selectedAnswer,
    }];

    try {
      await axios.post('/api/submit/', {
        session_id: sessionId,
        answers: finalAnswers,
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success(
            <div>
              <strong className="d-block mb-1">✅ Test Submitted Successfully</strong>
              <small>Please check your email for your test result.</small>
            </div>,
            {
              position: "top-center",
              autoClose: 9000,
              closeOnClick: true,
              pauseOnHover: true,
              toastClassName: "custom-toast",
              bodyClassName: "custom-toast-body",
              onClose: () => (window.location.href = "/student_dash"),
            }
          );


    } catch (error) {
      console.error('❌ Submission error:', error);
      toast.error("Something went wrong while submitting the test.", {
        position: "top-center",
        theme: "colored",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!questions.length) return <div className="text-center mt-5">Loading questions...</div>;

  const currentQuestion = questions[currentQuestionIdx];

  return (
    <div className="quiz-container">
      <ToastContainer />
      <div className="quiz-card">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <span className="badge bg-danger quiz-timer">
            ⏱️ Time Left: {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
          </span>
          <span className="text-muted">Question {currentQuestionIdx + 1} of {questions.length}</span>
        </div>

        <h5 className="mb-3">{currentQuestion.text}</h5>

        {currentQuestion.question_type === 'mcq' ? (
          <ul className="list-unstyled quiz-options">
            {currentQuestion.options && Object.entries(currentQuestion.options).map(([key, value]) => (
              <li key={key}>
                <button
                  onClick={() => handleAnswer(key)}
                  className={selectedAnswer === key ? 'selected sky-blue' : 'sky-blue'}
                >
                  {key}: {value}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div className="mb-3">
            <textarea
              rows="5"
              className="form-control"
              placeholder="Write your answer here..."
              value={selectedAnswer}
              onChange={(e) => handleAnswer(e.target.value)}
            />
          </div>
        )}


        <div className="quiz-actions text-end">
          {selectedAnswer && (
            currentQuestionIdx + 1 < questions.length ? (
              <button onClick={handleNext} className="sky-blue">Next</button>
            ) : (
              <button onClick={handleFinalSubmit} className="sky-blue" disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Submit Test'}
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default Quiz;
