import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Authenticator } from '@aws-amplify/ui-react';
import { getCurrentUser } from 'aws-amplify/auth';
import '@aws-amplify/ui-react/styles.css';

// Import components
import RoleSelector from './components/RoleSelector';
import Dashboard from './pages/Dashboard';
import Blocks from './pages/Blocks';
import BlockDetail from './pages/BlockDetail';
import Workout from './pages/Workout';
import Profile from './pages/Profile';
import { getUser } from './services/api';

function App() {
  const [userSetupComplete, setUserSetupComplete] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const validRoles = ['athlete', 'coach'];

  // Add debugging useEffect
  useEffect(() => {
    console.log("Auth state check");
    getCurrentUser()
      .then(user => console.log("Current user exists:", user))
      .catch(err => console.log("No current user:", err));
  }, []);

  useEffect(() => {
    const initializeUser = async () => {
      setIsLoading(true);
  
      try {
        const cognitoUser = await getCurrentUser();
        const userId = cognitoUser.userId;
        console.log("Checking user in DB with ID:", userId);
  
        // Get user data directly
        const userData = await getUser(userId);
        console.log("User data from DB:", userData);
  
        if (userData?.role && validRoles.includes(userData.role)) {
          console.log("Valid user role detected:", userData.role);
          setUserSetupComplete(true);
        } else {
          console.warn("Invalid or missing role. Got:", userData?.role);
          setUserSetupComplete(false);
        }
      } catch (error) {
        console.error("Error in user data fetch or no authenticated user:", error);
        setUserSetupComplete(false);
      } finally {
        setIsLoading(false);
      }
    };
  
    initializeUser();
  }, []);

  const handleRoleSelected = () => {
    setUserSetupComplete(true);
  };

  return (
    <Authenticator 
      signUpAttributes={['name']}
      // Force showing login first
      initialState="signIn"
    >
      {({ signOut, user }) => {
        // If not authenticated, let Authenticator handle it
        if (!user) {
          return null;
        }
        
        // Add a debug button (remove in production)
        const DebugButton = () => (
          <button 
            onClick={() => {
              console.log("Clearing auth state");
              signOut();
              localStorage.clear();
              sessionStorage.clear();
              window.location.reload();
            }}
            className="fixed bottom-4 right-4 px-3 py-2 bg-red-600 text-white text-xs rounded"
          >
            Reset Auth
          </button>
        );
        
        // If still checking user setup, show loading
        if (isLoading) {
          return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              <DebugButton />
            </div>
          );
        }

        // If user exists but hasn't completed setup, show role selector
        if (userSetupComplete === false) {
          return (
            <>
              <RoleSelector user={user} onRoleSelected={handleRoleSelected} />
              <DebugButton />
            </>
          );
        }

        // If user is set up, show the app
        return (
          <Router>
            <Routes>
              <Route path="/" element={<Dashboard user={user} signOut={signOut} />} />
              <Route path="/blocks" element={<Blocks user={user} signOut={signOut} />} />
              <Route path="/blocks/:blockId" element={<BlockDetail user={user} signOut={signOut} />} />
              <Route path="/workout/:workoutId" element={<Workout user={user} signOut={signOut} />} />
              <Route path="/profile" element={<Profile user={user} signOut={signOut} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <DebugButton />
          </Router>
        );
      }}
    </Authenticator>
  );
}

export default App;