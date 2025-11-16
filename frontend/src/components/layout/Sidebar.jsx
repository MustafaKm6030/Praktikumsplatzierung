import React from "react";
import { NavLink } from "react-router-dom";
import icon from "../utils/Icon";
import {
    DASHBOARD_ICON,
    STUDENT_ICON,
    TEACHER_ICON,
    SCHOOLS_ICON,
    SETTINGS_ICON, LOGOUT_ICON,
} from "../utils/icons";
import "./Sidebar.css";

function Sidebar() {
    const navItems = [
        { path: "/", label: "Dashboard", icon: DASHBOARD_ICON },
        { path: "/students", label: "Students", icon: STUDENT_ICON },
        { path: "/teachers", label: "Teachers", icon: TEACHER_ICON },
        { path: "/schools", label: "Schools", icon: SCHOOLS_ICON },
        { path: "/settings", label: "Settings", icon: SETTINGS_ICON },
    ];

    const handleLogout = () => {
        console.log("Logging out...");
    };

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            isActive ? "sidebar-link active" : "sidebar-link"
                        }
                        end={item.path === "/"}
                    >
                        <icon svg={item.icon} size={20} />
                        <span className="sidebar-label">{item.label}</span>
                    </NavLink>
                ))}
                <button
                    className="sidebar-link sidebar-logout"
                    onClick={handleLogout}
                >
                    <icon svg={LOGOUT_ICON} size={20} />
                    <span className="sidebar-label">Logout</span>
                </button>
            </nav>

            <div className="sidebar-footer">
                <p className="sidebar-footer-text">Team 2 - ASPD 2025</p>
            </div>
        </aside>
    );
}

export default Sidebar;
