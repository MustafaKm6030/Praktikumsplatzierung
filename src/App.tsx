import React from "react";
import { Routes, Route, Navigate, NavLink } from "react-router-dom";
import PlManagementListPage from "./pages/PLManagementListPage";
import StudentListPage from "./pages/StudentManagementListView";

function App() {
  return (
    <div>
      {/* Simple top nav */}
      <nav
        style={{
          display: "flex",
          gap: "16px",
          padding: "12px 24px",
          borderBottom: "1px solid #e5e7eb",
          marginBottom: "8px",
        }}
      >
        <NavLink
          to="/"
          end
          style={({ isActive }) => ({
            textDecoration: "none",
            fontSize: "14px",
            color: isActive ? "#111827" : "#6b7280",
            fontWeight: isActive ? 600 : 400,
          })}
        >
          Studenten
        </NavLink>

        <NavLink
          to="/pls"
          style={({ isActive }) => ({
            textDecoration: "none",
            fontSize: "14px",
            color: isActive ? "#111827" : "#6b7280",
            fontWeight: isActive ? 600 : 400,
          })}
        >
          Praktikumslehrkräfte
        </NavLink>
      </nav>

      <Routes>
        <Route path="/" element={<StudentListPage />} />
        <Route path="/pls" element={<PlManagementListPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

export default App;
