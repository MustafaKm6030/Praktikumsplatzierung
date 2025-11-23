import React from 'react';
import './Animatedlogo.css';
import logoImage from './header-logo.png';
import { UniversityLogo } from "./UniversityLogo";

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

    const getPathClass = () => animationState === 'animating' ? 'path-draw' : 'path-static';
    const getImageClass = () => animationState === 'animating' ? 'falling-image' : 'image-static';
    const getTextClass = () => animationState === 'animating' ? 'logo-text' : 'text-static';

    return (
        <div className={getContainerClass()}>
            <UniversityLogo
                svgClass={getSvgClass()}
                pathClass={getPathClass()}
                imageClass={getImageClass()}
                textClass={getTextClass()}
                animationState={animationState}
                logoImage={logoImage}
            />

            {/* Show header content only when in header state */}
            {animationState === 'done' && (
                <div className="header-content">
                    <h2 className="header-title">Praktikumsamt Management System</h2>
                </div>
            )}
        </div>
    );
};

export default AnimatedLogo;