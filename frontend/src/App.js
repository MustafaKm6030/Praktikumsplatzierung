import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Teachers from './pages/Teachers';
import SchoolManagement from "./pages/SchoolManagement";
import Settings from './pages/Settings';
import AnimatedLogo from './components/layout/AnimatedLogo';
import axios from 'axios';
import './App.css';

function App() {
  // Fetch CSRF token on app load
  useEffect(() => {
    axios.get('/api/csrf/', { withCredentials: true })
      .catch(error => console.error('Failed to get CSRF token:', error));
  }, []);
  const [animationState, setAnimationState] = useState(() => {
    try {
      const hasShown = sessionStorage.getItem('animationShown');
      return hasShown ? 'done' : 'animating';
    } catch (error) {
      // If sessionStorage is blocked, still show animation (just won't remember it)
      console.warn('SessionStorage access denied, animation will show on every refresh');
      return 'animating';
    }
  });

  useEffect(() => {
    let timer;

    if (animationState === 'animating') {
      timer = setTimeout(() => setAnimationState('transitioning'), 3000);
    } else if (animationState === 'transitioning') {
      timer = setTimeout(() => {
        setAnimationState('done');
        try {
          sessionStorage.setItem('animationShown', 'true');
        } catch (error) {
          console.warn('SessionStorage access denied');
        }
      }, 800);
    }

    return () => clearTimeout(timer);
  }, [animationState]);

  if (animationState === 'animating') {
    return <AnimatedLogo animationState={animationState} />;
  }

  // --- MAIN APP CONTENT ---
  return (
      <>
        <AnimatedLogo animationState={animationState} />

        <Router>
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
      </>
  );
}

export default App;
