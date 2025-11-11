import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Teachers from './pages/Teachers';
import SchoolManagement from "./pages/SchoolManagement";
import Settings from './pages/Settings';
import AnimatedLogo from './components/layout/AnimatedLogo';
import './App.css';

function App() {
  const [animationState, setAnimationState] = useState(() => {
    const hasShown = sessionStorage.getItem('animationShown');
    return hasShown ? 'done' : 'animating';
  });

  useEffect(() => {
    if (animationState === 'animating') {
      // Wait for falling animation to complete (3 seconds)
      const timer = setTimeout(() => setAnimationState('transitioning'), 3000);
      return () => clearTimeout(timer);
    } else if (animationState === 'transitioning') {
      // Wait for transition to header (0.8 seconds)
      const timer = setTimeout(() => {
        setAnimationState('done');
        sessionStorage.setItem('animationShown', 'true');
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [animationState]);

  return (
      <>
        {/* AnimatedLogo is the NEW header - replaces old Header.js */}
        <AnimatedLogo animationState={animationState} />

        {/* Main app content - visible after animation starts transitioning */}
        {animationState !== 'animating' && (
            <Router>
              {/* Pass AnimatedLogo as the header component */}
              <Layout CustomHeader={null}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/students" element={<Students />} />
                  <Route path="/teachers" element={<Teachers />} />
                  <Route path="/schools" element={<SchoolManagement />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Layout>
            </Router>
        )}
      </>
  );
}

export default App;