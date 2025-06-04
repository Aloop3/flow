import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getUser } from '../services/api';

interface UserContextType {
  weightPreference: 'auto' | 'kg' | 'lb';
  updateWeightPreference: (preference: 'auto' | 'kg' | 'lb') => void;
  getDisplayUnit: (exerciseType: string) => 'kg' | 'lb';
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
  user: any; // From Cognito
}

export const UserProvider: React.FC<UserProviderProps> = ({ children, user }) => {
  const [weightPreference, setWeightPreference] = useState<'auto' | 'kg' | 'lb'>('auto');

  useEffect(() => {
    const fetchUserPreference = async () => {
      try {
        const userData = await getUser(user.user_id);
        if (userData?.weight_unit_preference) {
          setWeightPreference(userData.weight_unit_preference);
        }
      } catch (error) {
        console.error('Error fetching user preference:', error);
        // Fallback to auto behavior
        setWeightPreference('auto');
      }
    };

    if (user?.user_id) {
      fetchUserPreference();
    }
  }, [user.user_id]);

  const updateWeightPreference = (preference: 'auto' | 'kg' | 'lb') => {
    setWeightPreference(preference);
  };

  const getDisplayUnit = (exerciseType: string): 'kg' | 'lb' => {
    if (weightPreference === 'kg') return 'kg';
    if (weightPreference === 'lb') return 'lb';
    
    // Auto behavior - SBD default to kg, accessories to lb
    const bigThree = ['squat', 'bench press', 'deadlift'];
    const isBigThree = bigThree.some(lift => 
      exerciseType.toLowerCase().includes(lift)
    );
    
    return isBigThree ? 'kg' : 'lb';
  };

  return (
    <UserContext.Provider value={{
      weightPreference,
      updateWeightPreference,
      getDisplayUnit
    }}>
      {children}
    </UserContext.Provider>
  );
};

export const useWeightUnit = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useWeightUnit must be used within a UserProvider');
  }
  return context;
};