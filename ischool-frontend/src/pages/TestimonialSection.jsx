import { Container, Carousel } from "react-bootstrap";
import { Fade } from "react-awesome-reveal";

const testimonials = [
  {
    name: "Chinedu A.",
    role: "JSS3 Student",
    feedback:
      "iSchool Ola has completely changed how I prepare for exams. The tests are challenging but fair, and I feel confident every time!",
  },
  {
    name: "Amaka O.",
    role: "SS2 Student",
    feedback:
      "I love the simplicity and reliability of the platform. The results and feedback help me focus on my weak areas. Highly recommended!",
  },
  {
    name: "Tunde S.",
    role: "Teacher",
    feedback:
      "iSchool Ola makes it easy to track student progress and provide additional support where needed. The CBT format is very effective.",
  },
];

function TestimonialSection() {
  return (
    <section className="py-5 bg-light text-info text-center">
      <Container>
        <h2 className="mb-5 text-dark">What Our Students Say</h2>

        <Carousel
          fade
          controls={false}
          indicators={true}
          interval={6000}
          className="testimonial-carousel"
        >
          {testimonials.map(({ name, role, feedback }, idx) => (
            <Carousel.Item key={idx}>
              <Fade triggerOnce>
                <div className="testimonial-item px-4">
                  <p className="lead fst-italic">&quot;{feedback}&quot;</p>
                  <h5 className="mt-4">{name}</h5>
                  <small className="text-muted">{role}</small>
                </div>
              </Fade>
            </Carousel.Item>
          ))}
        </Carousel>
      </Container>

      <style jsx>{`
        .testimonial-carousel .carousel-indicators li {
          background-color: white;
        }
        .testimonial-item {
          max-width: 700px;
          margin: 0 auto;
        }
      `}</style>
    </section>
  );
}

export default TestimonialSection;
