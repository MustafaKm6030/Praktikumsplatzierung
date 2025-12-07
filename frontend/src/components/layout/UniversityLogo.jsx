import React from "react";

export const UniversityLogo = ({
                                   svgClass,
                                   pathClass,
                                   imageClass,
                                   textClass,
                                   animationState,
                                   logoImage,
                               }) => (
    <div className="logo-wrapper">
        <svg
            viewBox="-50 0 750 350"
            xmlns="http://www.w3.org/2000/svg"
            className={svgClass}
        >
            <g className="logo" transform="translate(200,100)">
                <g fill="none" strokeLinejoin="round" strokeWidth="8">
                    <path className={pathClass} d="M-15,0 L-15,115" strokeLinecap="butt"/>
                    <path className={pathClass} d="M55,40 L55,100" strokeLinecap="butt"/>
                    <path className={pathClass} d="M65,80 L65,100" strokeWidth="23" strokeLinecap="butt"/>
                    <path className={pathClass} d="M75,40 L75,100" strokeLinecap="butt"/>
                    <path className={pathClass} d="M145,0 L145,150" strokeLinecap="butt"/>
                    <path className={pathClass} d="M-15,0 L55,40" strokeLinecap="round"/>
                    <path className={pathClass} d="M75,40 L145,0" strokeLinecap="round"/>
                </g>

                <a
                    href="https://www.uni-passau.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={imageClass}
                >
                    <image href={logoImage} x="-110" y="0" width="266" height="266" />
                </a>

                <g className={textClass} transform="translate(160,0)">
                    <text x="0" y="45" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#7D7D7D">
                        UNIVERSITÄT
                    </text>
                    <text x="0" y="95" fontFamily="Arial, sans-serif" fontSize="42" fontWeight="300" fill="#AAAAAA">
                        PASSAU
                    </text>
                    <text
                        x="0"
                        y="140"
                        fontFamily="Arial, sans-serif"
                        fontSize="28"
                        fontWeight="400"
                        fill="#666"
                        className={animationState === 'animating' ? 'system-title' : 'system-title-hidden'}
                    >
                        Praktikumsamt-Verwaltungssystem
                    </text>
                </g>
            </g>
        </svg>
    </div>
);
