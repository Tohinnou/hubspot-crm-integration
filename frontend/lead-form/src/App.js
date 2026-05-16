import { useState } from "react";

const SOURCES = [
  { value: "facebook_ads", label: "Facebook Ads" },
  { value: "google_ads", label: "Google Ads" },
  { value: "referral", label: "Referral" },
  { value: "organic", label: "Organic" },
];

function ScoreBar({ score }) {
  const color = score >= 70 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ margin: "16px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontWeight: 600 }}>Lead Score</span>
        <span style={{ fontWeight: 700, color }}>{score}/100</span>
      </div>
      <div style={{ background: "#e5e7eb", borderRadius: 8, height: 12 }}>
        <div style={{
          width: `${score}%`,
          background: color,
          height: 12,
          borderRadius: 8,
          transition: "width 0.8s ease"
        }} />
      </div>
    </div>
  );
}

export default function App() {
  const [form, setForm] = useState({
    firstname: "",
    lastname: "",
    email: "",
    phone: "",
    lead_source_custom: "organic",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (data.status === "success") {
        setResult(data);
      } else {
        setError(data.message || "Something went wrong");
      }
    } catch (err) {
      setError("Cannot connect to server. Is FastAPI running?");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setForm({
      firstname: "",
      lastname: "",
      email: "",
      phone: "",
      lead_source_custom: "organic",
    });
  };

  const styles = {
    container: {
      minHeight: "100vh",
      background: "#f3f4f6",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "Inter, sans-serif",
      padding: 20,
    },
    card: {
      background: "#fff",
      borderRadius: 16,
      padding: 40,
      width: "100%",
      maxWidth: 480,
      boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    },
    title: {
      fontSize: 24,
      fontWeight: 700,
      marginBottom: 8,
      color: "#111827",
    },
    subtitle: {
      color: "#6b7280",
      marginBottom: 28,
      fontSize: 14,
    },
    label: {
      display: "block",
      fontSize: 13,
      fontWeight: 600,
      color: "#374151",
      marginBottom: 6,
    },
    input: {
      width: "100%",
      padding: "10px 14px",
      borderRadius: 8,
      border: "1px solid #d1d5db",
      fontSize: 14,
      marginBottom: 16,
      boxSizing: "border-box",
      outline: "none",
    },
    button: {
      width: "100%",
      padding: "12px",
      background: loading ? "#9ca3af" : "#ff5c35",
      color: "#fff",
      border: "none",
      borderRadius: 8,
      fontSize: 15,
      fontWeight: 600,
      cursor: loading ? "not-allowed" : "pointer",
      marginTop: 8,
    },
    success: {
      background: "#f0fdf4",
      border: "1px solid #bbf7d0",
      borderRadius: 12,
      padding: 24,
    },
    error: {
      background: "#fef2f2",
      border: "1px solid #fecaca",
      borderRadius: 8,
      padding: 12,
      color: "#dc2626",
      fontSize: 14,
      marginBottom: 16,
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {!result ? (
          <>
            <div style={styles.title}>Get in Touch</div>
            <div style={styles.subtitle}>Fill out the form and we'll be in touch shortly.</div>

            {error && <div style={styles.error}>{error}</div>}

            <form onSubmit={handleSubmit}>
              <div style={{ display: "flex", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>First Name *</label>
                  <input
                    style={styles.input}
                    name="firstname"
                    value={form.firstname}
                    onChange={handleChange}
                    required
                    placeholder="John"
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={styles.label}>Last Name *</label>
                  <input
                    style={styles.input}
                    name="lastname"
                    value={form.lastname}
                    onChange={handleChange}
                    required
                    placeholder="Doe"
                  />
                </div>
              </div>

              <label style={styles.label}>Email *</label>
              <input
                style={styles.input}
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="john@example.com"
              />

              <label style={styles.label}>Phone</label>
              <input
                style={styles.input}
                name="phone"
                value={form.phone}
                onChange={handleChange}
                placeholder="+1 234 567 890"
              />

              <label style={styles.label}>How did you hear about us? *</label>
              <select
                style={styles.input}
                name="lead_source_custom"
                value={form.lead_source_custom}
                onChange={handleChange}
              >
                {SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>

              <button style={styles.button} type="submit" disabled={loading}>
                {loading ? "Submitting..." : "Submit →"}
              </button>
            </form>
          </>
        ) : (
          <div style={styles.success}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
            <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
              Thanks, {result.name}!
            </div>
            <div style={{ color: "#6b7280", fontSize: 14, marginBottom: 20 }}>
              You've been added to our CRM. We'll be in touch at {result.email}.
            </div>
            <ScoreBar score={result.lead_score} />
            <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 20 }}>
              Contact ID: {result.contact_id}
            </div>
            <button
              style={{ ...styles.button, background: "#6b7280" }}
              onClick={reset}
            >
              Submit another
            </button>
          </div>
        )}
      </div>
    </div>
  );
}