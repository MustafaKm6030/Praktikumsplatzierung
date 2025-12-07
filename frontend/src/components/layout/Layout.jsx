import React from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import './Layout.css';

function Layout({ children }) {
    const location = useLocation();
    const isDashboard = location.pathname === '/';

    return (
        <div className="layout">
            <Sidebar />
            <div className={`layout-main ${isDashboard ? 'layout-main-dashboard' : ''}`}>
                {isDashboard ? (
                    children
                ) : (
                    <main className="layout-content">
                        {children}
                    </main>
                )}
            </div>
        </div>
    );
}

export default Layout;