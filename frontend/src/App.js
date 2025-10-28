import React, { useMemo, useState } from "react";

const API_BASE =
  process.env.REACT_APP_API_URL || window.location.origin || "http://localhost:8000";

async function jsonFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    const msg =
      typeof data === "object" && data?.detail
        ? Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || d).join(", ")
          : data.detail
        : text || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function Card({ title, children }) {
  return (
    <div style={styles.card}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      {children}
    </div>
  );
}

export default function App() {
  return (
    <div style={styles.container}>
      <h1>Group Expense Tracker</h1>
      <CreateGroup />
      <AddExpense />
      <ListExpenses />
      <GroupBalance />
      <FooterNote />
    </div>
  );
}

/** ---------------- Create Group ---------------- */
function CreateGroup() {
  const [name, setName] = useState("");
  const [membersText, setMembersText] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCreate() {
    setLoading(true);
    setResult("");
    try {
      const members = membersText
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const data = await jsonFetch(`${API_BASE}/groups/`, {
        method: "POST",
        body: JSON.stringify({ name: name.trim(), members }),
      });
      setResult(JSON.stringify(data, null, 2));
      setName("");
      setMembersText("");
    } catch (e) {
      setResult(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="Create Group">
      <label style={styles.label}>
        Group name
        <input
          style={styles.input}
          placeholder="Trip to Rome"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Members (comma separated)
        <input
          style={styles.input}
          placeholder="alice,bob,carol"
          value={membersText}
          onChange={(e) => setMembersText(e.target.value)}
        />
      </label>
      <button style={styles.button} onClick={handleCreate} disabled={loading}>
        {loading ? "Creating..." : "Create Group"}
      </button>
      <Pre>{result}</Pre>
    </Card>
  );
}

/** ---------------- Add Expense ---------------- */
function AddExpense() {
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [gid, setGid] = useState("1");
  const [payer, setPayer] = useState("");
  const [amount, setAmount] = useState("60");
  const [desc, setDesc] = useState("Dinner");
  const [date, setDate] = useState(today);
  const [type, setType] = useState("equal");
  const [splitsText, setSplitsText] = useState(
    '[{"user_id":"alice"},{"user_id":"bob"},{"user_id":"carol"}]'
  );
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  function parseSplits(text) {
    try {
      const parsed = text ? JSON.parse(text) : [];
      if (!Array.isArray(parsed)) throw new Error("Splits JSON must be an array");
      return parsed;
    } catch (e) {
      throw new Error(`Invalid Splits JSON: ${e.message}`);
    }
  }

  async function handleAdd() {
    setLoading(true);
    setResult("");
    try {
      const payload = {
        payer_id: payer.trim(),
        amount: Number(amount),
        description: desc.trim() || null,
        date: date || new Date().toISOString().slice(0, 10),
        split_type: type,
        splits: parseSplits(splitsText),
      };
      const data = await jsonFetch(`${API_BASE}/groups/${gid}/expenses`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="Add Expense">
      <label style={styles.label}>
        Group ID
        <input
          style={styles.input}
          type="number"
          value={gid}
          onChange={(e) => setGid(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Payer ID
        <input
          style={styles.input}
          placeholder="alice"
          value={payer}
          onChange={(e) => setPayer(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Amount
        <input
          style={styles.input}
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Description
        <input
          style={styles.input}
          placeholder="Dinner"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Date
        <input
          style={styles.input}
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </label>
      <label style={styles.label}>
        Split Type
        <select
          style={styles.input}
          value={type}
          onChange={(e) => setType(e.target.value)}
        >
          <option value="equal">equal</option>
          <option value="shares">shares</option>
          <option value="percent">percent</option>
        </select>
      </label>
      <label style={styles.label}>
        Splits JSON
        <textarea
          style={{ ...styles.input, height: 96, fontFamily: "ui-monospace, monospace" }}
          value={splitsText}
          onChange={(e) => setSplitsText(e.target.value)}
          placeholder='[{"user_id":"alice"},{"user_id":"bob"},{"user_id":"carol"}]'
        />
      </label>
      <button style={styles.button} onClick={handleAdd} disabled={loading}>
        {loading ? "Adding..." : "Add Expense"}
      </button>
      <Pre>{result}</Pre>
    </Card>
  );
}

/** ---------------- List Expenses ---------------- */
function ListExpenses() {
  const [gid, setGid] = useState("1");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLoad() {
    setLoading(true);
    setResult("");
    try {
      const data = await jsonFetch(`${API_BASE}/groups/${gid}/expenses`);
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="List Expenses">
      <label style={styles.label}>
        Group ID
        <input
          style={styles.input}
          type="number"
          value={gid}
          onChange={(e) => setGid(e.target.value)}
        />
      </label>
      <button style={styles.button} onClick={handleLoad} disabled={loading}>
        {loading ? "Loading..." : "Load"}
      </button>
      <Pre>{result}</Pre>
    </Card>
  );
}

/** ---------------- Group Balance ---------------- */
function GroupBalance() {
  const [gid, setGid] = useState("1");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCompute() {
    setLoading(true);
    setResult("");
    try {
      const data = await jsonFetch(`${API_BASE}/groups/${gid}/balance`);
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="Group Balance">
      <label style={styles.label}>
        Group ID
        <input
          style={styles.input}
          type="number"
          value={gid}
          onChange={(e) => setGid(e.target.value)}
        />
      </label>
      <button style={styles.button} onClick={handleCompute} disabled={loading}>
        {loading ? "Computing..." : "Compute"}
      </button>
      <Pre>{result}</Pre>
    </Card>
  );
}

function Pre({ children }) {
  if (!children) return null;
  return (
    <pre style={styles.pre}>
      {typeof children === "string" ? children : JSON.stringify(children, null, 2)}
    </pre>
  );
}

function FooterNote() {
  return;
}

const styles = {
  container: {
    fontFamily: "system-ui, Arial, sans-serif",
    maxWidth: 900,
    margin: "2rem auto",
    padding: "0 1rem",
  },
  card: {
    border: "1px solid #ddd",
    borderRadius: 8,
    padding: "1rem",
    margin: ".75rem 0",
  },
  label: { display: "block", margin: ".25rem 0" },
  input: { display: "block", margin: ".25rem 0 .75rem", padding: ".5rem", width: "100%" },
  button: { padding: ".6rem 1rem", cursor: "pointer" },
  pre: {
    background: "#f6f8fa",
    padding: ".75rem",
    borderRadius: 6,
    overflow: "auto",
  },
};
