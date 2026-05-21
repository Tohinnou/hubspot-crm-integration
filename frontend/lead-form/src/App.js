import { useState, useEffect, useCallback } from "react";
import { API_URL, GITHUB_URL } from "./config";

const SOURCES = [
  { value: "facebook_ads", label: "Facebook Ads" },
  { value: "google_ads", label: "Google Ads" },
  { value: "referral", label: "Referral" },
  { value: "organic", label: "Organic" },
];

const theme = {
  orange: "#ff5c35",
  orangeDark: "#e8421b",
  ink: "#111827",
  sub: "#6b7280",
  border: "#e5e7eb",
  bg: "#f9fafb",
  card: "#ffffff",
  green: "#22c55e",
  amber: "#f59e0b",
  red: "#ef4444",
};

const scoreColor = (s) =>
  s >= 70 ? theme.green : s >= 40 ? theme.amber : theme.red;

function Hero() {
  return (
    <header
      style={{
        background: `linear-gradient(135deg, ${theme.orange} 0%, ${theme.orangeDark} 100%)`,
        color: "#fff",
        padding: "56px 24px 72px",
        textAlign: "center",
      }}
    >
      <div style={{ maxWidth: 920, margin: "0 auto" }}>
        <div
          style={{
            display: "inline-block",
            background: "rgba(255,255,255,0.18)",
            padding: "6px 14px",
            borderRadius: 999,
            fontSize: 12,
            fontWeight: 600,
            letterSpacing: 0.4,
            marginBottom: 20,
          }}
        >
          OAUTH 2.0 · LEAD SCORING · WEBHOOKS
        </div>
        <h1
          style={{
            fontSize: "clamp(28px, 4.5vw, 44px)",
            fontWeight: 800,
            margin: "0 0 12px",
            letterSpacing: -0.5,
            lineHeight: 1.15,
          }}
        >
          HubSpot CRM Integration
        </h1>
        <p
          style={{
            fontSize: 17,
            opacity: 0.92,
            maxWidth: 620,
            margin: "0 auto 28px",
            lineHeight: 1.55,
          }}
        >
          Full-stack demo: OAuth install flow, lead capture form, automatic
          scoring, and HubSpot CRM sync — all wired end to end.
        </p>
        <div
          style={{
            display: "flex",
            gap: 12,
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <a
            href={`${API_URL}/oauth/install`}
            style={{
              background: "#fff",
              color: theme.orangeDark,
              padding: "12px 22px",
              borderRadius: 10,
              fontWeight: 700,
              fontSize: 15,
              textDecoration: "none",
              boxShadow: "0 4px 14px rgba(0,0,0,0.15)",
            }}
          >
            Install on HubSpot →
          </a>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            style={{
              background: "rgba(255,255,255,0.12)",
              border: "1px solid rgba(255,255,255,0.35)",
              color: "#fff",
              padding: "12px 22px",
              borderRadius: 10,
              fontWeight: 600,
              fontSize: 15,
              textDecoration: "none",
            }}
          >
            View on GitHub
          </a>
        </div>
      </div>
    </header>
  );
}

function ScoreBar({ score }) {
  const color = scoreColor(score);
  return (
    <div style={{ margin: "16px 0" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 4,
        }}
      >
        <span style={{ fontWeight: 600, fontSize: 13 }}>Lead Score</span>
        <span style={{ fontWeight: 700, color }}>{score}/100</span>
      </div>
      <div
        style={{ background: theme.border, borderRadius: 8, height: 10 }}
      >
        <div
          style={{
            width: `${score}%`,
            background: color,
            height: 10,
            borderRadius: 8,
            transition: "width 0.8s ease",
          }}
        />
      </div>
    </div>
  );
}

function LeadForm({ onSubmitted }) {
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
      const response = await fetch(`${API_URL}/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (data.status === "success") {
        setResult(data);
        onSubmitted && onSubmitted();
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

  const inputStyle = {
    width: "100%",
    padding: "10px 14px",
    borderRadius: 8,
    border: `1px solid ${theme.border}`,
    fontSize: 14,
    marginBottom: 14,
    boxSizing: "border-box",
    outline: "none",
    fontFamily: "inherit",
    background: "#fff",
  };

  const labelStyle = {
    display: "block",
    fontSize: 12,
    fontWeight: 600,
    color: "#374151",
    marginBottom: 5,
    letterSpacing: 0.2,
    textTransform: "uppercase",
  };

  if (result) {
    return (
      <div
        style={{
          background: "#f0fdf4",
          border: "1px solid #bbf7d0",
          borderRadius: 12,
          padding: 24,
        }}
      >
        <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
        <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
          Thanks, {result.name}!
        </div>
        <div
          style={{ color: theme.sub, fontSize: 14, marginBottom: 16 }}
        >
          You've been added to HubSpot CRM. We'll be in touch at{" "}
          {result.email}.
        </div>
        <ScoreBar score={result.lead_score} />
        <div
          style={{
            fontSize: 12,
            color: "#9ca3af",
            marginBottom: 20,
            fontFamily: "monospace",
          }}
        >
          Contact ID: {result.contact_id}
        </div>
        <button
          onClick={reset}
          style={{
            width: "100%",
            padding: "12px",
            background: theme.sub,
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 15,
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "inherit",
          }}
        >
          Submit another
        </button>
      </div>
    );
  }

  return (
    <>
      <div
        style={{
          fontSize: 20,
          fontWeight: 700,
          marginBottom: 4,
          color: theme.ink,
        }}
      >
        Capture a Lead
      </div>
      <div style={{ color: theme.sub, marginBottom: 24, fontSize: 14 }}>
        Submit a contact and watch it get scored & synced to HubSpot.
      </div>

      {error && (
        <div
          style={{
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 8,
            padding: 12,
            color: "#dc2626",
            fontSize: 13,
            marginBottom: 16,
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>First Name *</label>
            <input
              style={inputStyle}
              name="firstname"
              value={form.firstname}
              onChange={handleChange}
              required
              placeholder="John"
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Last Name *</label>
            <input
              style={inputStyle}
              name="lastname"
              value={form.lastname}
              onChange={handleChange}
              required
              placeholder="Doe"
            />
          </div>
        </div>

        <label style={labelStyle}>Email *</label>
        <input
          style={inputStyle}
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
          placeholder="john@example.com"
        />

        <label style={labelStyle}>Phone</label>
        <input
          style={inputStyle}
          name="phone"
          value={form.phone}
          onChange={handleChange}
          placeholder="+1 234 567 890"
        />

        <label style={labelStyle}>Lead Source *</label>
        <select
          style={inputStyle}
          name="lead_source_custom"
          value={form.lead_source_custom}
          onChange={handleChange}
        >
          {SOURCES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            background: loading ? "#9ca3af" : theme.orange,
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontSize: 15,
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
            marginTop: 8,
            fontFamily: "inherit",
          }}
        >
          {loading ? "Submitting..." : "Submit Lead →"}
        </button>
      </form>
    </>
  );
}

function Dashboard({ refreshKey }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/leads?limit=10`);
      const data = await response.json();
      if (data.status === "ok") {
        setLeads(data.leads || []);
      } else {
        setError(data.message || "Failed to fetch leads");
      }
    } catch (err) {
      setError("Cannot reach API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads, refreshKey]);

  const fmtDate = (iso) => {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso.slice(0, 10);
    }
  };

  return (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: theme.ink,
            }}
          >
            Recent Leads
          </div>
          <div style={{ color: theme.sub, fontSize: 13 }}>
            Live from your HubSpot CRM
          </div>
        </div>
        <button
          onClick={fetchLeads}
          disabled={loading}
          style={{
            background: "transparent",
            border: `1px solid ${theme.border}`,
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 13,
            fontWeight: 600,
            color: theme.ink,
            cursor: loading ? "wait" : "pointer",
            fontFamily: "inherit",
          }}
        >
          {loading ? "..." : "↻ Refresh"}
        </button>
      </div>

      {error && (
        <div
          style={{
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 8,
            padding: 12,
            color: "#dc2626",
            fontSize: 13,
            marginBottom: 12,
          }}
        >
          {error}
        </div>
      )}

      {!error && leads.length === 0 && !loading && (
        <div
          style={{
            border: `1px dashed ${theme.border}`,
            borderRadius: 10,
            padding: 32,
            textAlign: "center",
            color: theme.sub,
            fontSize: 14,
          }}
        >
          No leads yet — submit the form to see one here.
        </div>
      )}

      {leads.length > 0 && (
        <div
          style={{
            border: `1px solid ${theme.border}`,
            borderRadius: 10,
            overflow: "hidden",
          }}
        >
          {leads.map((l, i) => (
            <div
              key={l.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "12px 14px",
                borderTop: i === 0 ? "none" : `1px solid ${theme.border}`,
                background: i === 0 ? "#fff7ed" : "#fff",
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  background: theme.orange,
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 14,
                  flexShrink: 0,
                }}
              >
                {(l.firstname || "?").charAt(0).toUpperCase()}
                {(l.lastname || "").charAt(0).toUpperCase()}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontWeight: 600,
                    color: theme.ink,
                    fontSize: 14,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {(l.firstname || "—") + " " + (l.lastname || "")}
                </div>
                <div
                  style={{
                    color: theme.sub,
                    fontSize: 12,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {l.email || "no email"} · {fmtDate(l.created_at)}
                </div>
              </div>
              <div
                style={{
                  background: scoreColor(l.score) + "1a",
                  color: scoreColor(l.score),
                  fontWeight: 700,
                  fontSize: 13,
                  padding: "4px 10px",
                  borderRadius: 999,
                  flexShrink: 0,
                }}
              >
                {l.score}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

function StatCard({ label, value, sub, accent }) {
  return (
    <div
      style={{
        background: "#fff",
        border: `1px solid ${theme.border}`,
        borderRadius: 10,
        padding: "14px 16px",
        minWidth: 0,
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 600,
          color: theme.sub,
          textTransform: "uppercase",
          letterSpacing: 0.4,
          marginBottom: 6,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 24,
          fontWeight: 700,
          color: accent || theme.ink,
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 11, color: theme.sub, marginTop: 4 }}>
          {sub}
        </div>
      )}
    </div>
  );
}

function StatusPill({ status }) {
  const isError = status === "error";
  const color = isError ? theme.red : theme.green;
  return (
    <span
      style={{
        background: color + "1a",
        color,
        fontSize: 11,
        fontWeight: 700,
        padding: "3px 8px",
        borderRadius: 999,
        textTransform: "uppercase",
        letterSpacing: 0.3,
      }}
    >
      {status}
    </span>
  );
}

function SyncMonitor({ refreshKey, onReplayed }) {
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [replayingIds, setReplayingIds] = useState(() => new Set());
  const [replayFlash, setReplayFlash] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const statusParam = filter === "errors" ? "&status=error" : "";
      const [statsRes, eventsRes] = await Promise.all([
        fetch(`${API_URL}/sync/stats`).then((r) => r.json()),
        fetch(`${API_URL}/sync/events?limit=20${statusParam}`).then((r) =>
          r.json()
        ),
      ]);
      if (statsRes.status === "ok") setStats(statsRes);
      if (eventsRes.status === "ok") setEvents(eventsRes.events || []);
    } catch (err) {
      setError("Cannot reach sync API");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll, refreshKey]);

  const handleReplay = async (id) => {
    setReplayingIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    setReplayFlash(null);
    try {
      const res = await fetch(`${API_URL}/sync/events/${id}/retry`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      const ok = res.ok && data.status === "ok";
      setReplayFlash({
        kind: ok ? "ok" : "err",
        text: ok
          ? `Event #${id} replayed successfully`
          : `Replay failed: ${data.message || res.statusText}`,
      });
      await fetchAll();
      if (ok && onReplayed) onReplayed();
    } catch (err) {
      setReplayFlash({ kind: "err", text: "Replay request failed" });
    } finally {
      setReplayingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const fmtTime = (iso) => {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString(undefined, {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return iso.slice(11, 19);
    }
  };

  const rateColor =
    !stats || stats.success_rate >= 95
      ? theme.green
      : stats.success_rate >= 80
      ? theme.amber
      : theme.red;

  return (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div>
          <div
            style={{ fontSize: 20, fontWeight: 700, color: theme.ink }}
          >
            Sync Monitor
          </div>
          <div style={{ color: theme.sub, fontSize: 13 }}>
            HubSpot sync operations · last 24h
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <div
            style={{
              display: "inline-flex",
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              overflow: "hidden",
            }}
          >
            {["all", "errors"].map((v) => (
              <button
                key={v}
                onClick={() => setFilter(v)}
                style={{
                  background: filter === v ? theme.ink : "transparent",
                  color: filter === v ? "#fff" : theme.ink,
                  border: "none",
                  padding: "8px 14px",
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  fontFamily: "inherit",
                  textTransform: "capitalize",
                }}
              >
                {v === "all" ? "All" : "Errors only"}
              </button>
            ))}
          </div>
          <button
            onClick={fetchAll}
            disabled={loading}
            style={{
              background: "transparent",
              border: `1px solid ${theme.border}`,
              borderRadius: 8,
              padding: "8px 12px",
              fontSize: 13,
              fontWeight: 600,
              color: theme.ink,
              cursor: loading ? "wait" : "pointer",
              fontFamily: "inherit",
            }}
          >
            {loading ? "..." : "↻ Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 8,
            padding: 12,
            color: "#dc2626",
            fontSize: 13,
            marginBottom: 12,
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: 12,
          marginBottom: 20,
        }}
        className="sync-stats-grid"
      >
        <StatCard
          label="Success rate"
          value={stats ? `${stats.success_rate}%` : "—"}
          sub={stats ? `${stats.success_count} of ${stats.total}` : ""}
          accent={stats ? rateColor : null}
        />
        <StatCard
          label="Total syncs"
          value={stats ? stats.total : "—"}
          sub="last 24h"
        />
        <StatCard
          label="Failed"
          value={stats ? stats.error_count : "—"}
          sub={stats && stats.error_count > 0 ? "needs attention" : "all good"}
          accent={
            stats && stats.error_count > 0 ? theme.red : null
          }
        />
        <StatCard
          label="Avg latency"
          value={stats ? `${stats.avg_duration_ms} ms` : "—"}
          sub="HubSpot round-trip"
        />
      </div>

      {events.length === 0 && !loading && !error && (
        <div
          style={{
            border: `1px dashed ${theme.border}`,
            borderRadius: 10,
            padding: 32,
            textAlign: "center",
            color: theme.sub,
            fontSize: 14,
          }}
        >
          {filter === "errors"
            ? "No errors in the selected window. "
            : "No sync events yet — submit a lead to generate one."}
        </div>
      )}

      {replayFlash && (
        <div
          style={{
            background:
              replayFlash.kind === "ok" ? "#f0fdf4" : "#fef2f2",
            border: `1px solid ${
              replayFlash.kind === "ok" ? "#bbf7d0" : "#fecaca"
            }`,
            color: replayFlash.kind === "ok" ? "#15803d" : "#dc2626",
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 13,
            marginBottom: 12,
          }}
        >
          {replayFlash.text}
        </div>
      )}

      {events.length > 0 && (
        <div
          style={{
            border: `1px solid ${theme.border}`,
            borderRadius: 10,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "110px 140px minmax(0, 1fr) 80px 90px minmax(0, 1.2fr) 90px",
              gap: 12,
              padding: "10px 14px",
              background: "#f9fafb",
              fontSize: 11,
              fontWeight: 700,
              color: theme.sub,
              textTransform: "uppercase",
              letterSpacing: 0.4,
            }}
            className="sync-row sync-header"
          >
            <div>Time</div>
            <div>Operation</div>
            <div>Contact</div>
            <div>Status</div>
            <div>Duration</div>
            <div>Error</div>
            <div style={{ textAlign: "right" }}>Action</div>
          </div>
          {events.map((e) => {
            const isReplaying = replayingIds.has(e.id);
            const canReplay = e.status === "error" && e.replayable;
            return (
              <div
                key={e.id}
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "110px 140px minmax(0, 1fr) 80px 90px minmax(0, 1.2fr) 90px",
                  gap: 12,
                  padding: "10px 14px",
                  borderTop: `1px solid ${theme.border}`,
                  fontSize: 13,
                  alignItems: "center",
                  background:
                    e.status === "error" ? "#fef2f2" : "#fff",
                }}
                className="sync-row"
              >
                <div style={{ color: theme.sub, fontFamily: "monospace" }}>
                  {fmtTime(e.created_at)}
                </div>
                <div style={{ fontWeight: 600, color: theme.ink }}>
                  {e.operation}
                </div>
                <div
                  style={{
                    fontFamily: "monospace",
                    color: theme.sub,
                    fontSize: 12,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  title={
                    e.retried_from_id
                      ? `Retried from event #${e.retried_from_id}`
                      : ""
                  }
                >
                  {e.contact_id || "—"}
                  {e.retried_from_id ? (
                    <span
                      style={{
                        marginLeft: 6,
                        fontSize: 10,
                        background: theme.border,
                        color: theme.sub,
                        padding: "1px 6px",
                        borderRadius: 999,
                        fontFamily: "inherit",
                      }}
                    >
                      ↻ #{e.retried_from_id}
                    </span>
                  ) : null}
                </div>
                <div>
                  <StatusPill status={e.status} />
                </div>
                <div
                  style={{
                    fontFamily: "monospace",
                    color:
                      e.duration_ms > 2000 ? theme.amber : theme.ink,
                  }}
                >
                  {e.duration_ms} ms
                </div>
                <div
                  style={{
                    color: theme.red,
                    fontSize: 12,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  title={e.error_message || ""}
                >
                  {e.error_type || ""}
                </div>
                <div style={{ textAlign: "right" }}>
                  {canReplay ? (
                    <button
                      onClick={() => handleReplay(e.id)}
                      disabled={isReplaying}
                      title="Replay this failed sync"
                      style={{
                        background: isReplaying
                          ? "#9ca3af"
                          : theme.orange,
                        color: "#fff",
                        border: "none",
                        borderRadius: 6,
                        padding: "5px 10px",
                        fontSize: 12,
                        fontWeight: 700,
                        cursor: isReplaying ? "wait" : "pointer",
                        fontFamily: "inherit",
                      }}
                    >
                      {isReplaying ? "..." : "↻ Replay"}
                    </button>
                  ) : (
                    <span style={{ color: theme.sub, fontSize: 12 }}>
                      —
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: theme.bg,
        fontFamily: "Inter, system-ui, sans-serif",
        color: theme.ink,
      }}
    >
      <Hero />

      <main
        style={{
          maxWidth: 1080,
          margin: "-32px auto 0",
          padding: "0 24px 64px",
          display: "grid",
          gap: 20,
          gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)",
        }}
      >
        <section
          style={{
            background: theme.card,
            borderRadius: 14,
            padding: 28,
            boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
          }}
        >
          <LeadForm onSubmitted={() => setRefreshKey((k) => k + 1)} />
        </section>

        <section
          style={{
            background: theme.card,
            borderRadius: 14,
            padding: 28,
            boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
          }}
        >
          <Dashboard refreshKey={refreshKey} />
        </section>

        <section
          style={{
            background: theme.card,
            borderRadius: 14,
            padding: 28,
            boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
            gridColumn: "1 / -1",
          }}
        >
          <SyncMonitor
            refreshKey={refreshKey}
            onReplayed={() => setRefreshKey((k) => k + 1)}
          />
        </section>
      </main>

      <footer
        style={{
          textAlign: "center",
          padding: "24px",
          color: theme.sub,
          fontSize: 13,
        }}
      >
        Built with FastAPI · PostgreSQL · React ·{" "}
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          style={{ color: theme.orange, textDecoration: "none" }}
        >
          Source
        </a>
      </footer>

      <style>{`
        @media (max-width: 768px) {
          main {
            grid-template-columns: 1fr !important;
          }
          .sync-stats-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
          }
          .sync-row {
            grid-template-columns: 70px 100px minmax(0, 1fr) 60px 80px !important;
          }
          .sync-row > :nth-child(5), .sync-row > :nth-child(6) {
            display: none !important;
          }
          .sync-row > :nth-child(7) {
            grid-column: 5 !important;
          }
        }
        input:focus, select:focus {
          border-color: ${theme.orange} !important;
          box-shadow: 0 0 0 3px ${theme.orange}25;
        }
      `}</style>
    </div>
  );
}
