import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Alert } from 'react-bootstrap';
import ClassLevelSelector from '../components/ClassLevelSelector';
import SubjectSelector from '../components/SubjectSelector';
import TopicSelector from '../components/TopicSelector';
import Quiz from '../components/Quiz';

const TestPage = () => {
  const [classLevel, setClassLevel] = useState('');
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');

  useEffect(() => {
    console.log("📌 TestPage rendered:");
    console.log({ classLevel, subject, topic });
  }, [classLevel, subject, topic]);

  const resetSelections = () => {
    setClassLevel('');
    setSubject('');
    setTopic('');
  };

  return (
    <Container className="my-5 d-flex justify-content-center">
      <Card className="p-4 shadow-lg rounded-4 w-100" style={{ maxWidth: '900px' }}>
        <h2 className="text-center text-primary mb-4">📝 Take a Test</h2>

        {/* Step 1: Select Class Level */}
        {!classLevel && (
          <>
            <Alert variant="info" className="text-center">🔹 Please select your class level:</Alert>
            <Row className="mb-3">
              <Col>
                <ClassLevelSelector onSelect={setClassLevel} />
              </Col>
            </Row>
          </>
        )}

        {/* Step 2: Select Subject */}
        {classLevel && !subject && (
          <>
            <Alert variant="success" className="text-center">
              🔹 Class Level Selected: <strong>{classLevel}</strong><br />
              Now choose a subject:
            </Alert>
            <Row className="mb-3">
              <Col>
                <SubjectSelector classLevel={classLevel} onSelect={setSubject} />
              </Col>
            </Row>
          </>
        )}

        {/* Step 3: Select Topic */}
        {classLevel && subject && !topic && (
          <>
            <Alert variant="warning" className="text-center">
              🔹 Class Level: <strong>{classLevel}</strong> | Subject: <strong>{subject}</strong><br />
              Now select a topic:
            </Alert>
            <Row className="mb-3">
              <Col>
                <TopicSelector
                  classLevel={classLevel}
                  subject={subject}
                  onSelect={setTopic}
                />
              </Col>
            </Row>
          </>
        )}

        {/* Step 4: Start Quiz */}
        {classLevel && subject && topic && (
          <>
            <Alert variant="primary" className="text-center">
              🔹 Starting Quiz for: <strong>{classLevel} / {subject} / {topic}</strong>
            </Alert>
            <Quiz
              classLevel={classLevel}
              subject={subject}
              topic={topic}
              onRestart={resetSelections}
            />
          </>
        )}
      </Card>
    </Container>
  );
};

export default TestPage;
