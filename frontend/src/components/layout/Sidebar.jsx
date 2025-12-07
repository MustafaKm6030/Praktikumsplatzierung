import React from "react";
import { NavLink } from "react-router-dom";
import {
    DashboardIcon,
    StudentIcon,
    TeacherIcon,
    SchoolsIcon,
    SettingsIcon,
    AllocationIcon,
} from "../ui/Icons"; // Importing new components directly
import "./Sidebar.css";

function Sidebar() {
    const navItems = [
        { path: "/", label: "Dashboard", Icon: DashboardIcon },
        { path: "/students", label: "Studierende", Icon: StudentIcon },
        { path: "/teachers", label: "Lehrkräfte", Icon: TeacherIcon },
        { path: "/schools", label: "Schulen", Icon: SchoolsIcon },
        { path: "/allocation", label: "Zuteilung", Icon: AllocationIcon }, 
        { path: "/settings", label: "Einstellungen", Icon: SettingsIcon },
    ];

    return (
        <aside className="sidebar">
            <nav className="sidebar-nav">
                {navItems.map(({ path, label, Icon }) => (
                    <NavLink
                        key={path}
                        to={path}
                        className={({ isActive }) =>
                            isActive ? "sidebar-link active" : "sidebar-link"
                        }
                        end={path === "/"}
                    >
                        {/* Render the Icon component directly */}
                        <Icon size={20} />
                        <span className="sidebar-label">{label}</span>
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
}

export default Sidebar;