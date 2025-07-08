import React from "react";
import { useParams } from "react-router-dom";
import { Container, Row, Col, Image } from "react-bootstrap";
import blog1 from "../assets/blog1.jpg";
import blog2 from "../assets/blog2.jpg";
import blog3 from "../assets/blog3.jpg";

const blogArticles = {
  1: {
    title: "Top 5 Tips to Ace Your Online CBT Exams",
    content: `
Preparing for online CBTs? Here are 5 proven strategies:

1. Set up a quiet, distraction-free environment.
2. Practice regularly using trusted platforms like iSchool Ola.
3. Time yourself during practice to simulate real exams.
4. Focus on understanding questions, not just cramming.
5. Review past results to improve weak areas.

Success in CBT exams begins with preparation and consistency.
    `,
    image: blog1,
  },
  2: {
    title: "Why Practice Tests Boost Confidence",
    content: `
Confidence in exams doesn’t happen overnight—it’s built over time. Regular practice with online CBTs:

• Reduces anxiety.
• Builds familiarity with test formats.
• Improves speed and accuracy.

iSchool Ola offers tailored tests for JSS1 to SS3 that mirror real-life exam scenarios.
    `,
    image: blog2,
  },
  3: {
    title: "Transforming Secondary Education Through Digital Learning",
    content: `
Digital transformation in education is no longer optional—it's essential. iSchool Ola empowers students by:

• Offering anytime access to curriculum-aligned tests.
• Tracking performance and growth with data.
• Enabling schools to modernize learning assessment.

Join us in revolutionizing how Nigerian students prepare for the future!
    `,
    image: blog3,
  },
};

const NewsDetailPage = () => {
  const { id } = useParams();
  const article = blogArticles[id];

  if (!article) {
    return (
      <Container className="py-5 text-center">
        <h2 className="text-danger">Article not found</h2>
        <p>Please go back and try another blog post.</p>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <Row className="justify-content-center mb-5">
        <Col lg={10}>
          <h1 className="fw-bold text-primary mb-4 text-center">{article.title}</h1>
          <Image
            src={article.image}
            alt={article.title}
            fluid
            rounded
            className="mb-4 shadow-sm d-block mx-auto"
            style={{ maxHeight: "400px", objectFit: "cover", width: "100%" }}
          />
          <p style={{ whiteSpace: "pre-line", lineHeight: "1.8", fontSize: "1.1rem", color: "#555" }}>
            {article.content}
          </p>
        </Col>
      </Row>
    </Container>
  );
};

export default NewsDetailPage;
