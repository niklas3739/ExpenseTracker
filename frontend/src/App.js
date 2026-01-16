import React, { useEffect, useMemo, useState } from "react";

// ====== Config ======
const API_BASE =
  process.env.NODE_ENV === "production"
    ? "/api"
    : (process.env.REACT_APP_API_URL || "http://localhost:8000");

// ====== HTTP helper ======
async function jsonFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const msg = typeof data === "object" && data?.detail
      ? Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg || d).join(", ")
        : data.detail
      : text || `HTTP ${res.status}`;
    throw new Error(String(msg));
  }
  return data;
}

// ====== Small UI primitives ======
const styles = {
  app: {
    fontFamily: "Inter, system-ui, Arial, sans-serif",
    color: "#0f172a",
    minHeight: "100vh",
    background: "#f8fafc",
  },
  shell: {
    display: "grid",
    gridTemplateColumns: "300px 1fr",
    gap: 16,
    maxWidth: 1200,
    margin: "0 auto",
    padding: "24px 16px 48px",
  },
  h1: { fontSize: 24, margin: "8px 0 16px" },
  sidebar: {
    background: "white",
    border: "1px solid #e2e8f0",
    borderRadius: 16,
    padding: 16,
    position: "sticky",
    top: 16,
    height: "calc(100vh - 64px)",
    overflow: "auto",
  },
  main: { display: "grid", gap: 16 },
  card: {
    background: "white",
    border: "1px solid #e2e8f0",
    borderRadius: 16,
    padding: 16,
  },
  label: { display: "block", fontSize: 12, color: "#475569", marginBottom: 4 },
  input: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #cbd5e1",
    outline: "none",
  },
  select: {
    width: "100%",
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #cbd5e1",
    outline: "none",
    background: "white",
  },
  button: {
    padding: "10px 14px",
    borderRadius: 10,
    border: "1px solid #0ea5e9",
    background: "#0ea5e9",
    color: "white",
    cursor: "pointer",
  },
  buttonGhost: {
    padding: "8px 12px",
    borderRadius: 10,
    border: "1px solid #e2e8f0",
    background: "white",
    color: "#0f172a",
    cursor: "pointer",
  },
  row: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 },
  row3: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 },
  help: { fontSize: 12, color: "#64748b" },
  table: {
    width: "100%",
    borderCollapse: "separate",
    borderSpacing: 0,
  },
  th: {
    textAlign: "left",
    fontSize: 12,
    color: "#475569",
    padding: "10px 12px",
    borderBottom: "1px solid #e2e8f0",
    position: "sticky",
    top: 0,
    background: "white",
  },
  td: { padding: "10px 12px", borderBottom: "1px solid #f1f5f9", fontSize: 14 },
  badge: (bg, color="#0f172a") => ({ background: bg, color, padding: "2px 8px", borderRadius: 999, fontSize: 12 }),
  pre: { background: "#0f172a", color: "#e2e8f0", borderRadius: 10, padding: 12, overflow: "auto" },
};

function Card({ title, extra, children }) {
  return (
    <div style={styles.card}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <h3 style={{ margin: 0, fontSize: 16 }}>{title}</h3>
        {extra}
      </div>
      {children}
    </div>
  );
}

function Field({ label, children, hint }) {
  return (
    <div>
      <label style={styles.label}>{label}</label>
      {children}
      {hint && <div style={styles.help}>{hint}</div>}
    </div>
  );
}

// ====== Local storage helpers for Known Groups ======
const LS_KEY = "known-groups";
function loadKnownGroups() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "[]"); } catch { return []; }
}
function saveKnownGroups(arr) {
  localStorage.setItem(LS_KEY, JSON.stringify(arr));
}

// ====== App ======
export default function App() {
  const [knownGroups, setKnownGroups] = useState(() => loadKnownGroups());
  const [activeGid, setActiveGid] = useState(knownGroups[0]?.id || "");
  const [activeGroup, setActiveGroup] = useState(null);
  const [loadingGroup, setLoadingGroup] = useState(false);
  const [err, setErr] = useState("");

  // Load group when activeGid changes
  useEffect(() => {
    if (!activeGid) { setActiveGroup(null); return; }
    setLoadingGroup(true);
    setErr("");
    jsonFetch(`${API_BASE}/groups/${activeGid}`)
      .then((g) => setActiveGroup(g))
      .catch((e) => setErr(String(e.message || e)))
      .finally(() => setLoadingGroup(false));
  }, [activeGid]);

  function addKnownGroup(g) {
    setKnownGroups((prev) => {
      const next = [...prev.filter((x) => x.id !== g.id), g];
      saveKnownGroups(next);
      if (!activeGid) setActiveGid(String(g.id));
      return next;
    });
  }

  return (
    <div style={styles.app}>
      <div style={styles.shell}>
        {/* Sidebar */}
        <aside style={styles.sidebar}>
          <h2 style={styles.h1}>Expense Tracker</h2>

          <CreateGroupPanel onCreated={(g) => addKnownGroup(g)} />

          <Card title="Known Groups" extra={<span style={styles.help}>local only</span>}>
            {knownGroups.length === 0 ? (
              <div style={styles.help}>No groups saved yet. Create one or add by ID below.</div>
            ) : (
              <div>
                {knownGroups.map((g) => (
                  <button
                    key={g.id}
                    onClick={() => setActiveGid(String(g.id))}
                    style={{
                      ...styles.buttonGhost,
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      marginBottom: 8,
                      borderColor: String(activeGid) === String(g.id) ? "#0ea5e9" : "#e2e8f0",
                    }}
                  >
                    <div style={{ fontWeight: 600 }}>#{g.id} — {g.name}</div>
                    <div style={styles.help}>Members: {g.members?.join(", ") || "-"}</div>
                  </button>
                ))}
              </div>
            )}
            <AddGroupById onLoaded={(g) => addKnownGroup(g)} />
          </Card>
        </aside>

        {/* Main content */}
        <main style={styles.main}>
          {!activeGid ? (
            <EmptyState />
          ) : (
            <>
              <GroupHeader gid={activeGid} group={activeGroup} loading={loadingGroup} error={err} />
              <AddExpensePanel gid={activeGid} group={activeGroup} onAdded={() => { /* could trigger list refresh below */ }} />
              <ExpensesPanel gid={activeGid} />
              <BalancePanel gid={activeGid} />
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <Card title="Pick or Create a Group">
      <div style={styles.help}>Select a group from the left, create a new one, or add by ID.</div>
    </Card>
  );
}

// ====== Panels ======
function CreateGroupPanel({ onCreated }) {
  const [name, setName] = useState("");
  const [membersText, setMembersText] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  async function handleCreate() {
    setLoading(true); setMsg("");
    try {
      const members = membersText
        .split(",")
        .map((s) => String(s).trim())
        .filter((s) => s.length > 0);
      if (!name.trim()) throw new Error("Group name required");
      if (members.length === 0) throw new Error("Provide at least one member name")
      const data = await jsonFetch(`${API_BASE}/groups/`, {
        method: "POST",
        body: JSON.stringify({ name: name.trim(), members }),
      });
      onCreated?.(data);
      setMsg(`Created group #${data.id}`);
      setName(""); setMembersText("");
    } catch (e) { setMsg(String(e.message || e)); }
    finally { setLoading(false); }
  }

  return (
    <Card title="Create Group">
      <div style={{ display: "grid", gap: 10 }}>
        <Field label="Group name">
          <input style={styles.input} value={name} onChange={(e) => setName(e.target.value)} placeholder="Trip to Rome" />
        </Field>
        <Field label="Members (IDs, comma-separated)" hint="e.g. alice,bob,carol">
          <input style={styles.input} value={membersText} onChange={(e) => setMembersText(e.target.value)} placeholder="alice,bob,carol" />
        </Field>
        <div style={{ display: "flex", gap: 8 }}>
          <button style={styles.button} onClick={handleCreate} disabled={loading}>{loading ? "Creating..." : "Create"}</button>
        </div>
        {msg && <div style={{ ...styles.help, color: msg.startsWith("Created") ? "#16a34a" : "#b91c1c" }}>{msg}</div>}
      </div>
    </Card>
  );
}

function AddGroupById({ onLoaded }) {
  const [gid, setGid] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");
  async function handleLoad() {
    setLoading(true); setMsg("");
    try {
      const data = await jsonFetch(`${API_BASE}/groups/${Number(gid)}`);
      onLoaded?.(data);
      setMsg(`Loaded group #${data.id}`);
      setGid("");
    } catch (e) { setMsg(String(e.message || e)); }
    finally { setLoading(false); }
  }
  return (
    <div style={{ marginTop: 12, display: "grid", gap: 8 }}>
      <Field label="Add existing group by ID">
        <div style={{ display: "flex", gap: 8 }}>
          <input style={{ ...styles.input, flex: 1 }} type="number" value={gid} onChange={(e) => setGid(e.target.value)} placeholder="e.g. 1" />
          <button style={styles.buttonGhost} onClick={handleLoad} disabled={!gid || loading}>{loading ? "Loading..." : "Add"}</button>
        </div>
      </Field>
      {msg && <div style={{ ...styles.help, color: msg.startsWith("Loaded") ? "#16a34a" : "#b91c1c" }}>{msg}</div>}
    </div>
  );
}

function GroupHeader({ gid, group, loading, error }) {
  return (
    <Card title={`Group #${gid}`}
      extra={group && <span style={styles.badge("#eff6ff", "#1d4ed8")}>{group?.name}</span>}>
      {loading && <div style={styles.help}>Loading group…</div>}
      {error && <div style={{ ...styles.help, color: "#b91c1c" }}>{error}</div>}
      {group && (
        <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
          <div><div style={styles.label}>Name</div><div>{group.name}</div></div>
          <div><div style={styles.label}>Members</div><div>{group.members?.join(", ")}</div></div>
        </div>
      )}
    </Card>
  );
}

function AddExpensePanel({ gid, group }) {
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [payer, setPayer] = useState("");
  const [amount, setAmount] = useState("");
  const [desc, setDesc] = useState("");
  const [date, setDate] = useState(today);
  const [type, setType] = useState("equal");
  const [splits, setSplits] = useState([]); // [{user_id, amount/share/percent}]
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  // Auto-fill splits for equal when group changes
  useEffect(() => {
    if (group?.members?.length) {
      setSplits(group.members.map((u) => ({ user_id: u })));
    }
  }, [group]);

  function updateSplit(u, key, value) {
    setSplits((prev) => prev.map((sp) => sp.user_id === u ? { ...sp, [key]: value } : sp));
  }
  function ensureNumbers(payload) {
    return {
      ...payload,
      // keep payer_id and user_id as names (strings)
      amount: Number(payload.amount),
      splits: (payload.splits || []).map((sp) => ({
        ...sp,
        amount: sp.amount != null && sp.amount !== "" ? Number(sp.amount) : undefined,
        share: sp.share != null && sp.share !== "" ? Number(sp.share) : undefined,
        percent: sp.percent != null && sp.percent !== "" ? Number(sp.percent) : undefined,
      })),
    };
  }

  async function handleAdd() {
    setLoading(true); setMsg("");
    try {
      if (!gid) throw new Error("No group selected");
      if (!payer) throw new Error("Choose a payer");
      if (!amount || Number(amount) <= 0) throw new Error("Amount must be > 0");

      const payload = ensureNumbers({
        payer_id: payer,
        amount,
        description: desc || null,
        date,
        split_type: type,
        splits,
      });
      const data = await jsonFetch(`${API_BASE}/groups/${Number(gid)}/expenses`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMsg(`Added expense #${data.id}`);
      setAmount(""); setDesc("");
    } catch (e) { setMsg(String(e.message || e)); }
    finally { setLoading(false); }
  }

  return (
    <Card title="Add Expense">
      <div style={{ display: "grid", gap: 12 }}>
        <div style={styles.row3}>
          <Field label="Payer">
            <select style={styles.select} value={payer} onChange={(e) => setPayer(e.target.value)}>
              <option value="">Select member</option>
              {group?.members?.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </Field>
          <Field label="Amount">
            <input style={styles.input} type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" />
          </Field>
          <Field label="Date">
            <input style={styles.input} type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </Field>
        </div>
        <div style={styles.row}>
          <Field label="Description">
            <input style={styles.input} value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="Dinner" />
          </Field>
          <Field label="Split Type">
            <select style={styles.select} value={type} onChange={(e) => setType(e.target.value)}>
              <option value="equal">equal</option>
              <option value="shares">shares</option>
              <option value="percent">percent</option>
              <option value="exact">exact</option>
            </select>
          </Field>
        </div>

        {/* Splits editor */}
        <Card title="Splits" extra={<button style={styles.buttonGhost} onClick={() => group?.members && setSplits(group.members.map((u) => ({ user_id: u })))}>Reset to members</button>}>
          <div style={{ overflowX: "auto" }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>User ID</th>
                  {type === "equal" && <th style={styles.th}>Included?</th>}
                  {type === "shares" && <th style={styles.th}>Shares</th>}
                  {type === "percent" && <th style={styles.th}>Percent</th>}
                  {type === "exact" && <th style={styles.th}>Amount</th>}
                </tr>
              </thead>
              <tbody>
                {splits.map((sp) => (
                  <tr key={sp.user_id}>
                    <td style={styles.td}><code>{sp.user_id}</code></td>
                    {type === "equal" && (
                      <td style={styles.td}>
                        <input type="checkbox"
                          checked={sp.include !== false}
                          onChange={(e) => updateSplit(sp.user_id, "include", e.target.checked)} />
                      </td>
                    )}
                    {type === "shares" && (
                      <td style={styles.td}>
                        <input style={{ ...styles.input, maxWidth: 140 }} type="number" step="1"
                          value={sp.share ?? ""}
                          onChange={(e) => updateSplit(sp.user_id, "share", e.target.value)} />
                      </td>
                    )}
                    {type === "percent" && (
                      <td style={styles.td}>
                        <input style={{ ...styles.input, maxWidth: 140 }} type="number" step="0.01"
                          value={sp.percent ?? ""}
                          onChange={(e) => updateSplit(sp.user_id, "percent", e.target.value)} />
                      </td>
                    )}
                    {type === "exact" && (
                      <td style={styles.td}>
                        <input style={{ ...styles.input, maxWidth: 140 }} type="number" step="0.01"
                          value={sp.amount ?? ""}
                          onChange={(e) => updateSplit(sp.user_id, "amount", e.target.value)} />
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ ...styles.help, marginTop: 8 }}>
            Equal: tick who participates. Shares/Percent/Exact: fill respective numbers.
          </div>
        </Card>

        <div style={{ display: "flex", gap: 8 }}>
          <button style={styles.button} onClick={handleAdd} disabled={loading}>{loading ? "Adding…" : "Add Expense"}</button>
          {msg && <div style={{ ...styles.help, alignSelf: "center", color: msg.startsWith("Added") ? "#16a34a" : "#b91c1c" }}>{msg}</div>}
        </div>
      </div>
    </Card>
  );
}

function ExpensesPanel({ gid }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!gid) return;
    setLoading(true); setErr("");
    jsonFetch(`${API_BASE}/groups/${Number(gid)}/expenses`)
      .then((arr) => setItems(arr || []))
      .catch((e) => setErr(String(e.message || e)))
      .finally(() => setLoading(false));
  }, [gid, refreshKey]);

  return (
    <Card title="Expenses" extra={<button style={styles.buttonGhost} onClick={() => setRefreshKey((k) => k + 1)}>Refresh</button>}>
      {loading && <div style={styles.help}>Loading…</div>}
      {err && <div style={{ ...styles.help, color: "#b91c1c" }}>{err}</div>}
      {!loading && items.length === 0 && <div style={styles.help}>No expenses yet.</div>}
      {items.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Date</th>
                <th style={styles.th}>Payer</th>
                <th style={styles.th}>Amount</th>
                <th style={styles.th}>Type</th>
                <th style={styles.th}>Description</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id}>
                  <td style={styles.td}>#{r.id}</td>
                  <td style={styles.td}>{r.date}</td>
                  <td style={styles.td}>{r.payer_id}</td>
                  <td style={styles.td}>€ {Number(r.amount).toFixed(2)}</td>
                  <td style={styles.td}><span style={styles.badge("#f1f5f9")}>{r.split_type}</span></td>
                  <td style={styles.td}>{r.description || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

function BalancePanel({ gid }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function load() {
    setLoading(true); setErr("");
    try { setData(await jsonFetch(`${API_BASE}/groups/${Number(gid)}/balance`)); }
    catch (e) { setErr(String(e.message || e)); }
    finally { setLoading(false); }
  }

  useEffect(() => { if (gid) load(); }, [gid]);

  return (
    <Card title="Balance & Suggestions" extra={<button style={styles.buttonGhost} onClick={load}>Recalculate</button>}>
      {loading && <div style={styles.help}>Computing…</div>}
      {err && <div style={{ ...styles.help, color: "#b91c1c" }}>{err}</div>}
      {data && (
        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <h4 style={{ margin: "8px 0" }}>Net Balances</h4>
            <div style={{ overflowX: "auto" }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>User</th>
                    <th style={styles.th}>Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.balances || {}).map(([uid, bal]) => (
                    <tr key={uid}>
                      <td style={styles.td}>{uid}</td>
                      <td style={{ ...styles.td, color: Number(bal) >= 0 ? "#16a34a" : "#b91c1c" }}>
                        € {Number(bal).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h4 style={{ margin: "8px 0" }}>Payout Suggestions</h4>
            {(!data.suggestions || data.suggestions.length === 0) ? (
              <div style={styles.help}>No suggestions. Everyone is settled ✨</div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>From</th>
                      <th style={styles.th}>To</th>
                      <th style={styles.th}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.suggestions.map((s, i) => (
                      <tr key={i}>
                        <td style={styles.td}>{s.from}</td>
                        <td style={styles.td}>{s.to}</td>
                        <td style={styles.td}>€ {Number(s.amount).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
