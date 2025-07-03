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

  const getDisplayUnit = (exerciseType?: string): 'kg' | 'lb' => {
    if (weightPreference === 'kg') return 'kg';
    if (weightPreference === 'lb') return 'lb';
    
    if (!exerciseType) {
      return 'lb';
    }
    
    const exerciseLower = exerciseType.toLowerCase();
    
    // Check for Big 3 movements FIRST (before equipment check)
    const bigThree = ['squat', 'bench press', 'deadlift'];
    const isBigThree = bigThree.some(lift => 
      exerciseLower.includes(lift)
    );
    
    if (isBigThree) {
      return 'kg';
    }
    
    // Check for equipment type (dumbbell/machine → lb)
    const equipmentKeywords = ['dumbbell', 'machine', 'cable'];
    const isEquipmentBased = equipmentKeywords.some(keyword => 
      exerciseLower.includes(keyword)
    );
    
    if (isEquipmentBased) {
      return 'lb';
    }
    
    return 'lb';
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