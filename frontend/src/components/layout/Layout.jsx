import React from 'react';
import Sidebar from './Sidebar';
import './Layout.css';

function Layout({ children }) {
    return (
        <div className="layout">
            <Sidebar />
            <div className="layout-main">
                {/* No Header component - AnimatedLogo from App.js is the header */}
                <main className="layout-content">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default Layout;