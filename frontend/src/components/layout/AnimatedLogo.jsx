import React from 'react';
import './Animatedlogo.css';
import logoImage from './image-removebg-preview (1).png';
import {USER_ICON} from "../utils/icons";
import { UniversityLogo } from "../utils/UniversityLogo";


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

                    <div className="header-right">
                        <div className="header-user">
                            <span
                                className="header-user-icon"
                                dangerouslySetInnerHTML={{ __html: USER_ICON }}
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