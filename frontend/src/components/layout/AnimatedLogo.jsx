import React from 'react';
import './Animatedlogo.css';
import logoImage from './image-removebg-preview (1).png';
import {LogoutIcon, UserIcon} from "../utils/icons";

const AnimatedLogo = ({ animationState = 'animating' }) => {
    const getContainerClass = () => {
        if (animationState === 'animating') return 'logo-container-animating';
        if (animationState === 'transitioning') return 'logo-container-transitioning';
        return 'logo-container-header';
    };

    const getSvgClass = () => {
        if (animationState === 'animating') return 'logo-svg-animating';
        if (animationState === 'transitioning') return 'logo-svg-transitioning';
        return 'logo-svg-header';
    };

    const getPathClass = () => {
        return animationState === 'animating' ? 'path-draw' : 'path-static';
    };

    const getImageClass = () => {
        return animationState === 'animating' ? 'falling-image' : 'image-static';
    };

    const getTextClass = () => {
        return animationState === 'animating' ? 'logo-text' : 'text-static';
    };

    return (
        <div className={getContainerClass()}>
            <div className="logo-wrapper">
                <svg
                    viewBox="-50 0 750 350"
                    xmlns="http://www.w3.org/2000/svg"
                    className={getSvgClass()}
                >
                    <g className="logo" transform="translate(200,100)">
                        <g fill="none" strokeLinejoin="round" strokeWidth="8">
                            <path className={getPathClass()} d="M-15,0 L-15,115" strokeLinecap="butt"/>
                            <path className={getPathClass()} d="M55,40 L55,100" strokeLinecap="butt"/>
                            <path className={getPathClass()} d="M65,80 L65,100" strokeWidth="23" strokeLinecap="butt"/>
                            <path className={getPathClass()} d="M75,40 L75,100" strokeLinecap="butt"/>
                            <path className={getPathClass()} d="M145,0 L145,150" strokeLinecap="butt"/>
                            <path className={getPathClass()} d="M-15,0 L55,40" strokeLinecap="round"/>
                            <path className={getPathClass()} d="M75,40 L145,0" strokeLinecap="round"/>
                        </g>

                        <a
                            href="https://www.uni-passau.de"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={getImageClass()}
                        >
                            <image href={logoImage} x="-110" y="0" width="266" height="266" />
                        </a>

                        <g className={getTextClass()} transform="translate(160,0)">
                            <text x="0" y="45" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#7D7D7D">
                                UNIVERSITÄT
                            </text>
                            <text x="0" y="95" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#AAAAAA">
                                PASSAU
                            </text>
                            {/* System title - shows during animation, fades out when transitioning */}
                            <text
                                x="0"
                                y="140"
                                fontFamily="Arial, sans-serif"
                                fontSize="28"
                                fontWeight="400"
                                fill="#666"
                                className={animationState === 'animating' ? 'system-title' : 'system-title-hidden'}
                            >
                                Praktikumsamt Management System
                            </text>
                        </g>
                    </g>
                </svg>
            </div>

            {/* Show header content only when in header state */}
            {animationState === 'done' && (
                <div className="header-content">
                    <h2 className="header-title">Praktikumsamt Management System</h2>

                    <div className="header-right">
                        <div className="header-user">
                            <span
                                className="header-user-icon"
                                dangerouslySetInnerHTML={{ __html: UserIcon }}
                            />
                            <div className="header-user-info">
                                <span className="header-user-name">Team 2 Admin</span>
                                <span className="header-user-role">Administrator</span>
                            </div>
                        </div>

                    </div>
                </div>
            )}
        </div>
    );
};

export default AnimatedLogo;