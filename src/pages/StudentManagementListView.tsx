import React, { useEffect, useMemo, useRef, useState } from "react";

// ---------- Types ----------
type Program = "GS" | "MS";
type PraktikumType = "PDP I" | "PDP II" | "SFP" | "ZSP";
type PlacementStatus = "Placed" | "Unplaced" | "In Review";

interface Student {
  id: string;
  name: string;
  program: Program;
  declaredTypes: PraktikumType[];
  subjects: string[];
  status: PlacementStatus;
}

const ALL = "ALL" as const;

// ---------- Mock Data ----------
const MOCK_STUDENTS: Student[] = [
  { id: "ST-2024-001", name: "Anna Schmidt", program: "GS", declaredTypes: ["PDP II", "SFP"], subjects: ["Deutsch", "Mathematik"], status: "Placed" },
  { id: "ST-2024-002", name: "Max Müller", program: "MS", declaredTypes: ["PDP I"], subjects: ["Englisch", "Geschichte"], status: "Unplaced" },
  { id: "ST-2024-003", name: "Sophie Weber", program: "GS", declaredTypes: ["ZSP", "PDP II"], subjects: ["Mathematik", "Sport"], status: "In Review" },
  { id: "ST-2024-004", name: "Lukas Fischer", program: "GS", declaredTypes: ["PDP II"], subjects: ["Deutsch", "Kunst"], status: "Placed" },
  { id: "ST-2024-005", name: "Emma Becker", program: "MS", declaredTypes: ["SFP"], subjects: ["Biologie", "Chemie"], status: "Unplaced" },
  { id: "ST-2024-006", name: "Jonas Hoffmann", program: "GS", declaredTypes: ["PDP I", "PDP II"], subjects: ["Mathematik", "Musik"], status: "Placed" },
  { id: "ST-2024-007", name: "Lena Koch", program: "MS", declaredTypes: ["ZSP"], subjects: ["Deutsch", "Englisch"], status: "In Review" },
  { id: "ST-2024-008", name: "Tim Richter", program: "GS", declaredTypes: ["PDP II"], subjects: ["Sport", "Sachunterricht"], status: "Unplaced" },
  { id: "ST-2024-009", name: "Marie Klein", program: "MS", declaredTypes: ["PDP I", "SFP"], subjects: ["Mathematik", "Physik"], status: "Placed" },
  { id: "ST-2024-010", name: "Felix Wagner", program: "GS", declaredTypes: ["PDP II"], subjects: ["Deutsch", "Englisch"], status: "In Review" },
  { id: "ST-2024-011", name: "Hannah Schulz", program: "MS", declaredTypes: ["ZSP", "SFP"], subjects: ["Geschichte", "Geographie"], status: "Unplaced" },
  { id: "ST-2024-012", name: "Paul Zimmermann", program: "GS", declaredTypes: ["PDP I"], subjects: ["Mathematik", "Sport"], status: "Placed" },
];

const programs: Program[] = ["GS", "MS"];
const praktikums: PraktikumType[] = ["PDP I", "PDP II", "SFP", "ZSP"];
const statuses: PlacementStatus[] = ["Placed", "Unplaced", "In Review"];

// ---------- CSV Export ----------
function exportCSV(rows: Student[], filename = "students.csv") {
  const header = [
    "Student ID",
    "Name",
    "Program",
    "Praktikum Types",
    "Subjects",
    "Placement Status",
  ];

  const body = rows.map((s) => [
    s.id,
    s.name,
    s.program,
    s.declaredTypes.join("; "),
    s.subjects.join("; "),
    s.status,
  ]);

  const csvRows = [header, ...body].map((r) =>
    r
      .map((x) => {
        const value = String(x).replace(/"/g, '""');
        return `"${value}"`;
      })
      .join(",")
  );

  const blob = new Blob([csvRows.join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ---------- Component ----------
export default function StudentManagementListView() {
  const [rows, setRows] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  const [program, setProgram] = useState<typeof ALL | Program>(ALL);
  const [type, setType] = useState<typeof ALL | PraktikumType>(ALL);
  const [status, setStatus] = useState<typeof ALL | PlacementStatus>(ALL);
  const [subject, setSubject] = useState<typeof ALL | string>(ALL);
  const [q, setQ] = useState("");

  const fileRef = useRef<HTMLInputElement | null>(null);

  // Fetch from /api/students, fallback to mock
  useEffect(() => {
    let alive = true;

    (async () => {
      try {
        const resp = await fetch("https://gitlab.infosun.fim.uni-passau.de/aspd/2025/team-2/implementation.git");

        if (!resp.ok) throw new Error("API not available");
        const data = (await resp.json()) as Student[];
        if (alive) setRows(data);
      } catch {
        if (alive) setRows(MOCK_STUDENTS);
      } finally {
        if (alive) setLoading(false);
      }
    })();

    return () => {
      alive = false;
    };
  }, []);

  const subjectOptions = useMemo(() => {
    const set = new Set<string>();
    rows.forEach((r) => r.subjects.forEach((s) => set.add(s)));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [rows]);

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      const byProgram = program === ALL || r.program === program;
      const byType = type === ALL || r.declaredTypes.includes(type);
      const byStatus = status === ALL || r.status === status;
      const bySubject = subject === ALL || r.subjects.includes(subject);
      const bySearch =
        q.trim() === "" ||
        [r.id, r.name].some((f) =>
          f.toLowerCase().includes(q.toLowerCase())
        );

      return byProgram && byType && byStatus && bySubject && bySearch;
    });
  }, [rows, program, type, status, subject, q]);

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <div style={{ marginBottom: "16px" }}>
        <h1 style={{ fontSize: "24px", margin: 0 }}>Student Management</h1>
        <p style={{ color: "#666", fontSize: "14px" }}>
          View, filter, and manage student placement status.
        </p>
      </div>

      {/* Actions + Filters */}
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "16px",
          marginBottom: "16px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        }}
      >
        {/* Buttons */}
        <div
          style={{
            display: "flex",
            gap: "8px",
            alignItems: "center",
            marginBottom: "12px",
          }}
        >
          <button
            style={{
              padding: "8px 12px",
              borderRadius: "999px",
              border: "1px solid #111",
              backgroundColor: "#111",
              color: "white",
              fontSize: "14px",
              cursor: "pointer",
            }}
            onClick={() => console.log("add-new-student")}
          >
            Add New Student
          </button>

          <input
            ref={fileRef}
            type="file"
            accept=".csv,application/vnd.ms-excel"
            style={{ display: "none" }}
            onChange={(e) =>
              console.log("import file selected", e.target.files?.[0])
            }
          />

          <button
            style={{
              padding: "8px 12px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              backgroundColor: "#f5f5f5",
              fontSize: "14px",
              cursor: "pointer",
            }}
            onClick={() => fileRef.current?.click()}
          >
            Import Students
          </button>

          <div style={{ marginLeft: "auto" }}>
            <button
              style={{
                padding: "8px 12px",
                borderRadius: "999px",
                border: "1px solid #ccc",
                backgroundColor: "white",
                fontSize: "14px",
                cursor: "pointer",
              }}
              onClick={() => exportCSV(filtered)}
            >
              Export List
            </button>
          </div>
        </div>

        {/* Filters */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "8px",
            alignItems: "center",
          }}
        >
          {/* Program */}
          <select
            value={program}
            onChange={(e) =>
              setProgram(
                e.target.value === ALL ? ALL : (e.target.value as Program)
              )
            }
            style={{
              padding: "6px 8px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              fontSize: "14px",
            }}
          >
            <option value={ALL}>All Programs</option>
            {programs.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          {/* Type */}
          <select
            value={type}
            onChange={(e) =>
              setType(
                e.target.value === ALL ? ALL : (e.target.value as PraktikumType)
              )
            }
            style={{
              padding: "6px 8px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              fontSize: "14px",
            }}
          >
            <option value={ALL}>All Types</option>
            {praktikums.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          {/* Status */}
          <select
            value={status}
            onChange={(e) =>
              setStatus(
                e.target.value === ALL
                  ? ALL
                  : (e.target.value as PlacementStatus)
              )
            }
            style={{
              padding: "6px 8px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              fontSize: "14px",
            }}
          >
            <option value={ALL}>All Statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          {/* Subject */}
          <select
            value={subject}
            onChange={(e) =>
              setSubject(e.target.value === ALL ? ALL : e.target.value)
            }
            style={{
              padding: "6px 8px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              fontSize: "14px",
            }}
          >
            <option value={ALL}>All Subjects</option>
            {subjectOptions.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          {/* Search */}
          <input
            type="text"
            placeholder="Search by Name, ID..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{
              marginLeft: "auto",
              padding: "6px 8px",
              borderRadius: "999px",
              border: "1px solid #ccc",
              fontSize: "14px",
              minWidth: "220px",
            }}
          />
        </div>
      </div>

      {/* Table */}
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "16px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
        }}
      >
        <div
          style={{
            marginBottom: "8px",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          <span>Students</span>
          <span style={{ color: "#777", fontWeight: 400 }}>
            Showing {filtered.length} of {rows.length}
          </span>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr
                style={{
                  textAlign: "left",
                  borderBottom: "1px solid #eee",
                  fontSize: "12px",
                  color: "#666",
                }}
              >
                <th style={{ padding: "8px" }}>Student ID</th>
                <th style={{ padding: "8px" }}>Name</th>
                <th style={{ padding: "8px" }}>Program</th>
                <th style={{ padding: "8px" }}>Praktikum Type Declared</th>
                <th style={{ padding: "8px" }}>Subjects</th>
                <th style={{ padding: "8px" }}>Placement Status</th>
                <th style={{ padding: "8px", textAlign: "center" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ padding: "16px", textAlign: "center" }}>
                    Loading students...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ padding: "16px", textAlign: "center" }}>
                    No students match the current filters.
                  </td>
                </tr>
              ) : (
                filtered.map((s) => (
                  <tr
                    key={s.id}
                    style={{
                      borderBottom: "1px solid #f1f1f1",
                      fontSize: "14px",
                    }}
                  >
                    <td style={{ padding: "8px", fontFamily: "monospace" }}>{s.id}</td>
                    <td style={{ padding: "8px" }}>{s.name}</td>
                    <td style={{ padding: "8px" }}>{s.program}</td>
                    <td style={{ padding: "8px" }}>
                      {s.declaredTypes.join(", ")}
                    </td>
                    <td style={{ padding: "8px" }}>
                      {s.subjects.join(", ")}
                    </td>
                    <td style={{ padding: "8px" }}>{s.status}</td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      <button
                        style={{
                          padding: "4px 8px",
                          marginRight: "4px",
                          fontSize: "12px",
                          cursor: "pointer",
                        }}
                        onClick={() => console.log("view", s.id)}
                      >
                        View
                      </button>
                      <button
                        style={{
                          padding: "4px 8px",
                          marginRight: "4px",
                          fontSize: "12px",
                          cursor: "pointer",
                        }}
                        onClick={() => console.log("edit", s.id)}
                      >
                        Edit
                      </button>
                      <button
                        style={{
                          padding: "4px 8px",
                          fontSize: "12px",
                          cursor: "pointer",
                        }}
                        onClick={() => console.log("delete", s.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div
          style={{
            marginTop: "8px",
            fontSize: "12px",
            color: "#777",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <span>Showing {filtered.length} students</span>
          <span>{new Date().toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}
