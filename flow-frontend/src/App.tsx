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

  // This effect will check user setup whenever the component renders
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const user = await getCurrentUser();
        setIsLoading(true);
        try {
          // Try to get the user from our database
          const userData = await getUser(user.userId);
          // Check if user exists AND has a role
          setUserSetupComplete(!!userData && !!userData.role);
        } catch (error) {
          // If we got an error, the user likely doesn't exist in our database yet
          setUserSetupComplete(false);
        } finally {
          setIsLoading(false);
        }
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
    <Authenticator 
      // Use signUpAttributes to include name in signup without customizing form
      signUpAttributes={['name']}
    >
      {({ signOut, user }) => {
        // If not authenticated, let Authenticator handle it
        if (!user) {
          return null;
        }
        
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