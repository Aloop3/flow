import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Authenticator } from '@aws-amplify/ui-react';
import { getCurrentUser } from 'aws-amplify/auth';
import '@aws-amplify/ui-react/styles.css';
import RoleSelector from './components/RoleSelector';
import Dashboard from './pages/Dashboard';
import Blocks from './pages/Blocks';
import BlockDetail from './pages/BlockDetail';
import Workout from './pages/Workout';
import Profile from './pages/Profile';
import { getUser } from './services/api';
import BlockCreate from './pages/BlockCreate';
import BlockEdit from './pages/BlockEdit';
import DayDetail from './pages/DayDetail';
import CoachAthleteBlocks from './pages/coach/CoachAthleteBlocks';
import CoachBlockCreate from './pages/coach/CoachBlockCreate';
import { UserProvider } from './contexts/UserContext';
import Analytics from './pages/coach/Analytics';
import BetaFeedback from './components/BetaFeedback';


//  AuthenticatedApp component extracted
const AuthenticatedApp = ({ user, signOut }: { user: any, signOut: () => void }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [userSetupComplete, setUserSetupComplete] = useState<boolean | null>(null);
  const [userData, setUserData] = useState<any>(null);
  const validRoles = ['athlete', 'coach'];

  // Effect to verify user record exists in DB and has a valid role
  useEffect(() => {
    const initializeUser = async () => {
      setIsLoading(true);
      try {
        console.log("Checking user in DB with ID:", user.userId);
        const fetchedUser = await getUser(user.userId);
        console.log("User data from DB:", fetchedUser);
        setUserData(fetchedUser);

        // Check if user has a valid role (athlete or coach)
        if (fetchedUser && validRoles.includes(fetchedUser.role)) {
          console.log("User role found:", fetchedUser.role);
          setUserSetupComplete(true);
        } else {
          console.log("Invalid or missing role. Got:", fetchedUser?.role);
          setUserSetupComplete(false);
        }
      } catch (error) {
        console.error("Error fetching user:", error);
        setUserSetupComplete(false);
      } finally {
        setIsLoading(false);
      }
    };

    initializeUser();
  }, [user]); // Re-run when user object changes

  const handleRoleSelected = async () => {
    setUserSetupComplete(true);
    try {
      // Refresh user data to get updated role
      const refreshedUser = await getUser(user.userId);
      setUserData(refreshedUser);
    } catch (err) {
      console.error("Error refreshing user after role selection:", err);
    }
  };


  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto p-6">
          <div className="h-8 bg-gray-200 rounded w-48 mb-8 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }


  // Show role selector if user needs to select a role
  if (userSetupComplete === false) {
    return (
      <>
        <RoleSelector user={user} onRoleSelected={handleRoleSelected} />
      </>
    );
  }

  const handleEnhancedSignOut = async () => {
    try {
      console.log('Starting enhanced logout process');
      
      // 1. Clear all cached data FIRST
      localStorage.clear();
      sessionStorage.clear();
      
      // 2. Reset React state that might persist
      setUserSetupComplete(null);
      setUserData(null);
      
      // 3. Call the original signOut function
      await signOut();
      
      // 4. Force navigation to root and reload
      window.location.href = '/';
      
    } catch (error) {
      console.error('Error during logout:', error);
      // Fallback: force reload to clear everything
      window.location.href = '/';
    }
  };

  // Show main application once user is fully set up
  if (userSetupComplete === true && userData) {
    return (
      <UserProvider user={userData}>
        <Router>
          <Routes>
            <Route path="/" element={<Dashboard user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/blocks" element={<Blocks user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/blocks/new" element={<BlockCreate user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/blocks/:blockId" element={<BlockDetail user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/blocks/:blockId/edit" element={<BlockEdit user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/workout/:workoutId" element={<Workout user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/days/:dayId" element={<DayDetail user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/profile" element={<Profile user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/coach/athletes/:athleteId/blocks" element={<CoachAthleteBlocks user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/coach/athletes/:athleteId/blocks/new" element={<CoachBlockCreate user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="/analytics" element={<Analytics user={userData} signOut={handleEnhancedSignOut} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <BetaFeedback />
        </Router>
      </UserProvider>
    );
  }

  return null;
};

// Thin wrapper App
function App() {
  useEffect(() => {
    console.log("Auth state check");
    getCurrentUser()
      .then(user => console.log("Current user exists:", user))
      .catch(err => console.log("No current user:", err));
  }, []);

  return (
    <Authenticator 
      signUpAttributes={['name']} 
      initialState="signIn"
      loginMechanisms={['email']}
    >
      {({ signOut, user }) => {
        const safeSignOut = signOut ?? (() => {});
        return (
          <>
            {user ? (
              <AuthenticatedApp user={user} signOut={safeSignOut} />
            ) : (
              <div>Loading...</div>
            )}
          </>
        );
      }}
    </Authenticator>
  );
}

export default App;