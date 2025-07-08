import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("🔥 Error Boundary Caught an error:", error);
    console.error("📌 Component Stack Trace:", errorInfo);
    this.setState({ error, errorInfo }); // Save the error for display if needed
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', backgroundColor: '#fdd', borderRadius: '8px' }}>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error?.toString()}
            <br />
            {this.state.errorInfo?.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
