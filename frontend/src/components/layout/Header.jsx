import React from 'react';
import './Header.css';
import logoImage from './image-removebg-preview (1).png';

function Header({ showLogo = false }) {
    return (
        <header className="header">
            <div className="header-left">
                {/* Show logo when animation is complete */}
                {showLogo && (
                    <div className="header-logo">
                        <svg
                            viewBox="-50 0 750 350"
                            xmlns="http://www.w3.org/2000/svg"
                            className="header-logo-svg"
                        >
                            <g className="logo" transform="translate(200,30)">
                                <g fill="none" strokeLinejoin="round" strokeWidth="8">
                                    <path d="M-15,0 L-15,115" strokeLinecap="butt" stroke="#666"/>
                                    <path d="M55,40 L55,100" strokeLinecap="butt" stroke="#666"/>
                                    <path d="M65,80 L65,100" strokeWidth="23" strokeLinecap="butt" stroke="#666"/>
                                    <path d="M75,40 L75,100" strokeLinecap="butt" stroke="#666"/>
                                    <path d="M145,0 L145,150" strokeLinecap="butt" stroke="#666"/>
                                    <path d="M-15,0 L55,40" strokeLinecap="round" stroke="#666"/>
                                    <path d="M75,40 L145,0" strokeLinecap="round" stroke="#666"/>
                                </g>

                                <a
                                    href="https://www.uni-passau.de"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="header-logo-link"
                                >
                                    <image href={logoImage} x="-110" y="0" width="266" height="266" />
                                </a>

                                <g transform="translate(160,0)">
                                    <text x="0" y="45" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#7D7D7D">
                                        UNIVERSITÄT
                                    </text>
                                    <text x="0" y="95" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#AAAAAA">
                                        PASSAU
                                    </text>
                                </g>
                            </g>
                        </svg>
                    </div>
                )}

                <h2 className="header-title">Praktikumsamt Management System</h2>
            </div>

            <div className="header-right">
                <div className="header-user">
                    <span className="header-user-icon">👤</span>
                    <div className="header-user-info">
                        <span className="header-user-name">Team 2 Admin</span>
                        <span className="header-user-role">Administrator</span>
                    </div>
                </div>

                <button className="header-logout-btn" title="Logout">
                    🚪
                </button>
            </div>
        </header>
    );
}

export default Header;