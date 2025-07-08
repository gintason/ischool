import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import blog1 from '../assets/blog1.jpg';
import blog2 from '../assets/blog2.jpg';
import blog3 from '../assets/blog3.jpg'; // Make sure this image exists in your assets folder

const NewsPage = () => {
  const navigate = useNavigate();

  const articles = [
    {
      id: 1,
      title: "Top 5 Tips to Ace Your Online CBT Exams",
      summary: "Discover key strategies that help students prepare and perform excellently in online CBT assessments using platforms like iSchool Ola.",
      image: blog1,
    },
    {
      id: 2,
      title: "Why Practice Tests Boost Confidence",
      summary: "Learn how regular exposure to timed tests can build exam confidence, reduce anxiety, and enhance familiarity with real exam formats.",
      image: blog2,
    },
    {
      id: 3,
      title: "Transforming Secondary Education Through Digital Learning",
      summary: "Explore how platforms like iSchool Ola are revolutionizing the educational landscape by delivering curriculum-aligned, accessible testing solutions.",
      image: blog3,
    },
  ];

  return (
    <div className="py-5 bg-light">
      <Container>
        <h2 className="text-center fw-bold mb-4 text-primary">iSchool Ola News & Blog</h2>
        <p className="text-center text-muted mb-5">Stay informed with the latest updates, expert articles, and digital learning insights.</p>

        <Row className="g-4">
          {articles.map((article) => (
            <Col md={6} lg={4} key={article.id}>
              <Card className="h-100 border-0 shadow-sm">
                <Card.Img variant="top" src={article.image} />
                <Card.Body>
                  <Card.Title>{article.title}</Card.Title>
                  <Card.Text className="text-muted">{article.summary}</Card.Text>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={() => navigate(`/news/${article.id}`)}
                  >
                    Read More
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
    </div>
  );
};

export default NewsPage;
