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
        { path: "/students", label: "Students", Icon: StudentIcon },
        { path: "/teachers", label: "Teachers", Icon: TeacherIcon },
        { path: "/schools", label: "Schools", Icon: SchoolsIcon },
        { path: "/allocation", label: "Allocation", Icon: AllocationIcon }, 
        { path: "/settings", label: "Settings", Icon: SettingsIcon },
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