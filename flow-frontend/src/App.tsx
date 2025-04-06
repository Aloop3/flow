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

  const checkUserSetup = async (user: any) => {
    setIsLoading(true);
    try {
      // Try to get the user from our database
      const userData = await getUser(user.userId);
      // If we got user data back, the user is set up
      setUserSetupComplete(!!userData);
    } catch (error) {
      // If we got an error, the user likely doesn't exist in our database yet
      setUserSetupComplete(false);
    } finally {
      setIsLoading(false);
    }
  };

  // This effect will check user setup whenever the component renders
  // We'll need to check after login and after role selection
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const user = await getCurrentUser();
        await checkUserSetup(user);
      } catch (error) {
        // User is not logged in, which is fine
        setIsLoading(false);
      }
    };

    initializeUser();
  }, []);

  const handleRoleSelected = () => {
    setUserSetupComplete(true);
  };

  return (
    <Authenticator>
      {({ signOut, user }) => {
        // If still checking user setup, show loading
        if (isLoading) {
          return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          );
        }

        // If user exists but hasn't completed setup, show role selector
        if (userSetupComplete === false) {
          return <RoleSelector user={user} onRoleSelected={handleRoleSelected} />;
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
          </Router>
        );
      }}
    </Authenticator>
  );
}

export default App;