export function AuthHeader() {
  return (
    <div style={{
      padding: '1.5rem 2rem',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      {/* Brand */}
      <span style={{
        fontFamily: "'DM Sans', system-ui, sans-serif",
        fontWeight: 700,
        fontSize: '1.25rem',
        color: '#f5f5f5',
        letterSpacing: '-0.02em',
        marginBottom: '2rem',
      }}>
        Flow
      </span>

      {/* Hero */}
      <h1 style={{
        fontFamily: "'DM Sans', system-ui, sans-serif",
        fontWeight: 900,
        fontSize: 'clamp(3.5rem, 8vw, 6rem)',
        lineHeight: 0.9,
        color: '#f5f5f5',
        letterSpacing: '-0.04em',
        textTransform: 'uppercase',
        margin: 0,
      }}>
        Track<br />
        Your<br />
        <span style={{ color: 'hsl(175, 84%, 40%)' }}>Lifts.</span>
      </h1>
      <p style={{
        color: 'rgba(245, 245, 245, 0.5)',
        fontSize: '1rem',
        marginTop: '1.5rem',
        lineHeight: 1.6,
        maxWidth: '320px',
        fontFamily: "'Inter', system-ui, sans-serif",
      }}>
        Periodized training blocks, workout tracking, and strength analytics. Built for powerlifting athletes and coaches.
      </p>
    </div>
  );
}
