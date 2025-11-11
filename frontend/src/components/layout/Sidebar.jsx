import React from "react";
import { NavLink } from "react-router-dom";
import Icon from "../utils/Icon";
import {
    dashboardIcon,
    studentsIcon,
    teachersIcon,
    schoolsIcon,
    settingsIcon, LogoutIcon,
} from "../utils/icons";
import "./Sidebar.css";

function Sidebar() {
    const navItems = [
        { path: "/", label: "Dashboard", icon: dashboardIcon },
        { path: "/students", label: "Students", icon: studentsIcon },
        { path: "/teachers", label: "Teachers", icon: teachersIcon },
        { path: "/schools", label: "Schools", icon: schoolsIcon },
        { path: "/settings", label: "Settings", icon: settingsIcon },
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
                        <Icon svg={item.icon} size={20} />
                        <span className="sidebar-label">{item.label}</span>
                    </NavLink>
                ))}
                <button
                    className="sidebar-link sidebar-logout"
                    onClick={handleLogout}
                >
                    <Icon svg={LogoutIcon} size={20} />
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
