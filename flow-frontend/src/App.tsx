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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        <DebugButton />
      </div>
    );
  }

  // Show role selector if user needs to select a role
  if (userSetupComplete === false) {
    return (
      <>
        <RoleSelector user={user} onRoleSelected={handleRoleSelected} />
        <DebugButton />
      </>
    );
  }

  // Show main application once user is fully set up
  if (userSetupComplete === true && userData) {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard user={userData} signOut={signOut} />} />
          <Route path="/blocks" element={<Blocks user={userData} signOut={signOut} />} />
          <Route path="/blocks/new" element={<BlockCreate user={userData} signOut={signOut} />} />
          <Route path="/blocks/:blockId" element={<BlockDetail user={userData} signOut={signOut} />} />
          <Route path="/blocks/:blockId/edit" element={<BlockEdit user={userData} signOut={signOut} />} />
          <Route path="/workout/:workoutId" element={<Workout user={userData} signOut={signOut} />} />
          <Route path="/days/:dayId" element={<DayDetail user={userData} signOut={signOut} />} />
          <Route path="/profile" element={<Profile user={userData} signOut={signOut} />} />
          <Route path="/coach/athletes/:athleteId/blocks" element={<CoachAthleteBlocks user={userData} signOut={signOut} />} />
          <Route path="/coach/athletes/:athleteId/blocks/new" element={<CoachBlockCreate user={userData} signOut={signOut} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <DebugButton />
      </Router>
    );
  }

  return null; // fallback
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