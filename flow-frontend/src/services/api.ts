import { fetchAuthSession, signOut } from 'aws-amplify/auth';
import { get, post, put, del } from 'aws-amplify/api';

export class ApiError extends Error {
    constructor(
        message: string,
        public statusCode?: number,
        public originalError?: unknown
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

// Types
export interface Block {
  block_id: string;
  athlete_id: string;
  coach_id?: string;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed';
  number_of_weeks?: number;
}

export interface Week {
  week_id: string;
  block_id: string;
  week_number: number;
  notes?: string;
}

export interface Day {
  day_id: string;
  week_id: string;
  day_number: number;
  date: string;
  focus?: string | null;
  notes?: string;
}

export interface Exercise {
  exercise_id: string;
  workout_id: string;
  exercise_type: string;
  sets: number;
  reps: number;
  weight: number;
  rpe?: number;
  notes?: string;
  order?: number;
  exercise_category?: string;
}

export interface ExerciseTypeLibrary {
  barbell: string[];
  dumbbell: string[];
  bodyweight: string[];
  machine: string[];
  cable: string[];
  custom: string[];
  all: string[];
  [key: string]: string[];
}

export interface User {
  user_id: string;
  email: string;
  name: string;
  role: 'athlete' | 'coach';
}

export interface CompletedExercise {
    completed_id: string;
    workout_id: string;
    exercise_id: string;
    notes?: string;
    sets: Set[];
  }
  
  export interface Workout {
    workout_id: string;
    athlete_id: string;
    day_id: string;
    date: string;
    notes?: string;
    status: 'completed' | 'partial' | 'skipped';
    exercises: CompletedExercise[]; // Now properly typed
  }

export interface Set {
  set_id: string;
  completed_exercise_id: string;
  workout_id: string;
  set_number: number;
  reps: number;
  weight: number;
  rpe?: number;
  notes?: string;
  completed?: boolean;
}

console.log('API Config:', {
  apiName: 'flow-api',
  endpoint: import.meta.env.VITE_API_URL || 'API_URL_NOT_SET'
});

// Helper to get auth headers
export const getAuthHeaders = async () => {
  try {
    const { tokens } = await fetchAuthSession();
    return {
      Authorization: `Bearer ${tokens?.idToken?.toString()}`
    };
  } catch (error) {
    console.error('Error getting auth session:', error);
    await signOut();
    throw new Error('Authentication required');
  }
};

// User endpoints
export const createUser = async (userData: Omit<User, 'user_id'>): Promise<User> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/users',
      options: {
        headers,
        body: userData
      }
    });
    return response.body as User;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const getUser = async (userId: string): Promise<User | null> => {
  try {
    const headers = await getAuthHeaders();
    
    // Make the API request
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/users/${userId}`,
      options: { headers }
    });
    
    // Log the full response for debugging
    console.log('Complete API response:', apiResponse);
    
    // In Amplify v6, we need to await the response promise
    const actualResponse = await apiResponse.response;
    console.log('Actual response after awaiting:', actualResponse);
    
    // Extract the body from the actual response
    if (actualResponse && actualResponse.body) {
      // Handle ReadableStream responses
      let objectData = actualResponse.body;
      let userData: any;
      try {
        userData = await objectData.json();
      } catch (e) {
        console.error('Failed to parse response body:', e);
      }
      
      return userData;
    }
    
    console.log('No user data found in response');
    return null;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
};

export const updateUser = async (userId: string, newUserData: Partial<User>): Promise<User | null> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await put({
      apiName: 'flow-api',
      path: `/users/${userId}`,
      options: {
        headers,
        body: newUserData
      }
    });
    
    // Await the response promise
    const actualResponse = await apiResponse.response;
    
    // Extract the body
    if (actualResponse && actualResponse.body) {
      let userData: any;
      try {
        userData = await actualResponse.body.json();
      } catch (e) {
        console.error('Failed to parse response body in updateUser:', e);
        return null;
      }

      console.log('Extracted user data after update:', userData);
      return userData;
    }

    console.log('No user data found in update response');
    return null;
  } catch (error) {
    console.error('Error updating user:', error);
    throw error;
  }
};

// Block endpoints
export const getBlocks = async (user_id: string): Promise<Block[]> => {
  try {
    const headers = await getAuthHeaders();
    
    console.log("Fetching blocks for user ID:", user_id);
    
    // Make the API request using the same pattern as getUser
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/athletes/${user_id}/blocks`,
      options: { headers }
    });
    
    // Log the full response for debugging
    console.log('Complete API response:', apiResponse);
    
    // Await the response promise as in getUser
    const actualResponse = await apiResponse.response;
    console.log('Actual response after awaiting:', actualResponse);
    
    // Extract the body from the actual response
    if (actualResponse && actualResponse.body) {
      // Handle ReadableStream responses
      let objectData = actualResponse.body;
      let blocksData: any;
      
      try {
        const parsedData = await objectData.json();
        console.log('Parsed blocks data:', parsedData);
        blocksData = Array.isArray(parsedData) ? parsedData : [];
      } catch (e) {
        console.error('Failed to parse response body:', e);
      }
      
      return blocksData;
    }
    
    console.log('No blocks data found in response');
    return [];
  } catch (error) {
    console.error('Error fetching blocks:', error);
    throw error;
  }
};


export const getBlock = async (blockId: string): Promise<Block | null> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching block with ID:', blockId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/blocks/${blockId}`,
      options: { headers }
    });

    console.log('Complete API response:', apiResponse);

    // Await the response promise
    const actualResponse = await apiResponse.response;
    console.log('Actual response after awaiting:', actualResponse);

    // Extract the body from the actual response
    if (actualResponse && actualResponse.body) {
      // Handle ReadableStream responses
      let objectData = actualResponse.body;
      let blockData: any;
      
      try {
        const parsedData = await objectData.json();
        console.log('Parsed block data:', parsedData);
        blockData = parsedData;
      } catch (e) {
        console.error('Failed to parse response body:', e);
        return null;
      }
      
      return blockData;
    }
    
    console.log('No block data found in response');
    return null;
  } catch (error) {
    console.error('Error fetching block:', error);
    throw error;
  }
};

export const createBlock = async (blockData: Omit<Block, 'block_id'>): Promise<Block> => {
  try {
    console.log('Sending block data:', JSON.stringify(blockData, null, 2));
    
    // Make sure the date format is correct (YYYY-MM-DD)
    const formattedData = {
      ...blockData,
      // Ensure dates are in correct format
      start_date: blockData.start_date.split('T')[0], // Remove any time component
      end_date: blockData.end_date.split('T')[0], // Remove any time component
      number_of_week: Number(blockData.number_of_weeks) || 4 // Default to 4 weeks if not provided
    };
    
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/blocks',
      options: {
        headers,
        body: formattedData
      }
    });
    return response.body as Block;
  } catch (error) {
    console.error('Error creating block (details):', error);
    throw error;
  }
};

export const updateBlock = async (blockId: string, blockData: Partial<Block>): Promise<Block> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/blocks/${blockId}`,
      options: {
        headers,
        body: blockData
      }
    });
    return response.body as Block;
  } catch (error) {
    console.error('Error updating block:', error);
    throw error;
  }
};

export const deleteBlock = async (blockId: string): Promise<void> => {
  try {
    const headers = await getAuthHeaders();
    await del({
      apiName: 'flow-api',
      path: `/blocks/${blockId}`,
      options: { headers }
    });
  } catch (error) {
    console.error('Error deleting block:', error);
    throw error;
  }
};

// Week endpoints
export const getWeeks = async (blockId: string): Promise<Week[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching weeks for block ID:', blockId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/blocks/${blockId}/weeks`,
      options: { headers }
    });

    // Debug the response structure
    console.log('Weeks API response:', apiResponse);
    
    // For Amplify v6, we need to await the response and parse it
    const actualResponse = await apiResponse.response;
    console.log('Weeks actual response after awaiting:', actualResponse);
    
    if (actualResponse && actualResponse.body) {
      // Handle ReadableStream responses
      let objectData = actualResponse.body;
      let parsedData;
      
      try {
        parsedData = await objectData.json();
        console.log('Parsed weeks data:', parsedData);
        return Array.isArray(parsedData) ? parsedData : [];
      } catch (e) {
        console.error('Failed to parse weeks data:', e);
        return [];
      }
    }
    
    console.log('No weeks data found in response');
    return [];
  } catch (error) {
    console.error('Error fetching weeks:', error);
    return []; // Return empty array instead of throwing
  }
};

export const createWeek = async (weekData: Omit<Week, 'week_id'>): Promise<Week> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/weeks',
      options: {
        headers,
        body: weekData
      }
    });
    return response.body as Week;
  } catch (error) {
    console.error('Error creating week:', error);
    throw error;
  }
};

// Day endpoints
export const getDays = async (weekId: string): Promise<Day[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching days for week ID:', weekId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/weeks/${weekId}/days`,
      options: { headers }
    });

    // Debug the response structure
    console.log('Days API response:', apiResponse);
    
    // For Amplify v6, we need to await the response and parse it
    const actualResponse = await apiResponse.response;
    console.log('Days actual response after awaiting:', actualResponse);
    
    if (actualResponse && actualResponse.body) {
      // Handle ReadableStream responses
      let objectData = actualResponse.body;
      let parsedData;
      
      try {
        parsedData = await objectData.json();
        console.log('Parsed days data:', parsedData);
        return Array.isArray(parsedData) ? parsedData : [];
      } catch (e) {
        console.error('Failed to parse days data:', e);
        return [];
      }
    }
    
    console.log('No days data found in response');
    return [];
  } catch (error) {
    console.error('Error fetching days:', error);
    return []; // Return empty array instead of throwing
  }
};

export const getDay = async (dayId: string): Promise<Day | null> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching day with ID:', dayId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/days/${dayId}`,
      options: { headers }
    });

    console.log('Complete API response:', apiResponse);

    // Await the response promise
    const actualResponse = await apiResponse.response;
    console.log('Actual response after awaiting:', actualResponse);

    // Extract the body from the actual response
    if (actualResponse && actualResponse.body) {
      let objectData = actualResponse.body;
      let dayData: any;

      try {
        const parsedData = await objectData.json();
        console.log('Parsed day data:', parsedData);
        dayData = parsedData;
      } catch (e) {
        console.error('Failed to parse response body:', e);
        return null;
      }

      return dayData;
    }

    console.log('No day data found in response');
    return null;
  } catch (error) {
    console.error('Error fetching day:', error);
    throw error;
  }
};

// Get exercises for a specific day
export const getExercisesForDay = async (dayId: string): Promise<Exercise[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching exercises for day with ID:', dayId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/days/${dayId}/exercises`,
      options: { headers }
    });

    console.log('Complete API response:', apiResponse);

    // Await the response promise
    const actualResponse = await apiResponse.response;
    console.log('Actual response after awaiting:', actualResponse);

    // Extract the body from the actual response
    if (actualResponse && actualResponse.body) {
      let objectData = actualResponse.body;
      let exercisesData: any;

      try {
        const parsedData = await objectData.json();
        console.log('Parsed exercises data:', parsedData);
        exercisesData = parsedData;
      } catch (e) {
        console.error('Failed to parse response body:', e);
        return [];
      }

      return Array.isArray(exercisesData) ? exercisesData : [];
    }

    console.log('No exercises data found in response');
    return [];
  } catch (error) {
    console.error('Error fetching exercises for day:', error);
    return [];
  }
};

export const createDay = async (dayData: Omit<Day, 'day_id'>): Promise<Day> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/days',
      options: {
        headers,
        body: dayData
      }
    });
    return response.body as Day;
  } catch (error) {
    console.error('Error creating day:', error);
    throw error;
  }
};

export const updateDay = async (dayId: string, dayData: Partial<Day>): Promise<Day> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/days/${dayId}`,
      options: {
        headers,
        body: dayData
      }
    });
    return response.body as Day;
  } catch (error) {
    console.error('Error updating day:', error);
    throw error;
  }
};

// Workout endpoints
export const getWorkout = async (workoutId: string): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/workouts/${workoutId}`,
      options: { headers }
    });
    return response.body as Workout;
  } catch (error) {
    console.error('Error fetching workout:', error);
    throw error;
  }
};

export const getWorkoutByDay = async (athleteId: string, dayId: string): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/athletes/${athleteId}/days/${dayId}/workout`,
      options: { headers }
    });
    return response.body as Workout;
  } catch (error) {
    console.error('Error fetching workout by day:', error);
    throw error;
  }
};

export const createWorkout = async (workoutData: Omit<Workout, 'workout_id'>): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/workouts',
      options: {
        headers,
        body: JSON.parse(JSON.stringify(workoutData))
      }
    });
    return response.body as Workout;
  } catch (error) {
    console.error('Error creating workout:', error);
    throw error;
  }
};

export const updateWorkout = async (workoutId: string, workoutData: Partial<Workout>): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/workouts/${workoutId}`,
      options: {
        headers,
        body: workoutData
      }
    });
    return response.body as Workout;
  } catch (error) {
    console.error('Error updating workout:', error);
    throw error;
  }
};

export const copyWorkout = async (
  sourceDayId: string, 
  targetDayId: string
): Promise<any> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Copying workout from day:', sourceDayId, 'to day:', targetDayId);
    const apiResponse = await post({
      apiName: 'flow-api',
      path: '/workouts/copy',
      options: {
        headers,
        body: {
          source_day_id: sourceDayId,
          target_day_id: targetDayId
        }
      }
    });
    
    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;
    
    if (actualResponse && actualResponse.body) {
      try {
        const result = await actualResponse.body.json();
        console.log('Copy workout result:', result);
        return result;
      } catch (e) {
        console.error('Failed to parse response:', e);
        throw new Error('Failed to copy workout');
      }
    }
    
    return true;
  } catch (error) {
    console.error('Error copying workout:', error);
    throw error;
  }
};

// Exercise endpoints
export const getExercisesForWorkout = async (workoutId: string): Promise<Exercise[]> => {
  try {
    if (!workoutId) {
      console.error('Missing workoutId parameter in getExercisesForWorkout');
      return [];
    }
    
    console.log(`Fetching exercises for workout: ${workoutId}`);
    const headers = await getAuthHeaders();
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/workouts/${workoutId}/exercises`,
      options: { headers }
    });
    
    console.log('Exercise API response:', apiResponse);
    
    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;
    console.log('Actual exercise response:', actualResponse);
    
    if (actualResponse && actualResponse.body) {
      try {
        const responseText = await actualResponse.body.text();
        console.log('Exercise response text:', responseText);
        
        if (responseText) {
          const data = JSON.parse(responseText);
          console.log('Parsed exercise data:', data);
          return Array.isArray(data) ? data : [];
        }
      } catch (e) {
        console.error('Error parsing exercise response:', e);
      }
    }
    
    return [];
  } catch (error) {
    console.error('Error fetching exercises for workout:', error);
    return [];
  }
};


export const getExerciseTypes = async (): Promise<ExerciseTypeLibrary> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await get({
      apiName: 'flow-api',
      path: '/exercises/types',
      options: { headers }
    });
    
    // For Amplify v6, we need to await the response and parse it
    const actualResponse = await apiResponse.response;
    
    if (actualResponse && actualResponse.body) {
      try {
        const parsedData = await actualResponse.body.json();
        return parsedData;
      } catch (e) {
        console.error('Failed to parse exercise types data:', e);
        throw new Error('Failed to parse exercise data');
      }
    }
    
    throw new Error('No exercise data received');
  } catch (error) {
    console.error('Error fetching exercise types:', error);
    throw error;
  }
};

// Set endpoints
export const getSetsForExercise = async (exerciseId: string): Promise<Set[]> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}/sets`,
      options: { headers }
    });
    return response.body as Set[];
  } catch (error) {
    console.error('Error fetching sets:', error);
    throw error;
  }
};

export const createSet = async (exerciseId: string, setData: Omit<Set, 'set_id'>): Promise<Set> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}/sets`,
      options: {
        headers,
        body: setData
      }
    });
    return response.body as Set;
  } catch (error) {
    console.error('Error creating set:', error);
    throw error;
  }
};

export const updateSet = async (setId: string, setData: Partial<Set>): Promise<Set> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/sets/${setId}`,
      options: {
        headers,
        body: setData
      }
    });
    return response.body as Set;
  } catch (error) {
    console.error('Error updating set:', error);
    throw error;
  }
};