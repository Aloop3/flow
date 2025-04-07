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
  focus?: string;
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

export interface User {
  user_id: string;
  email: string;
  name: string;
  role: 'athlete' | 'coach' | 'both';
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

export const getUser = async (userId: string): Promise<User> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/users/${userId}`,
      options: { headers }
    });
    return response.body as User;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
};

export const updateUser = async (userId: string, userData: Partial<User>): Promise<User> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/users/${userId}`,
      options: {
        headers,
        body: userData
      }
    });
    return response.body as User;
  } catch (error) {
    console.error('Error updating user:', error);
    throw error;
  }
};

// Block endpoints
export const getBlocks = async (athleteId: string): Promise<Block[]> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/athletes/${athleteId}/blocks`,
      options: { headers }
    });
    return response.body as Block[];
  } catch (error) {
    console.error('Error fetching blocks:', error);
    throw error;
  }
};

export const getBlock = async (blockId: string): Promise<Block> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/blocks/${blockId}`,
      options: { headers }
    });
    return response.body as Block;
  } catch (error) {
    console.error('Error fetching block:', error);
    throw error;
  }
};

export const createBlock = async (blockData: Omit<Block, 'block_id'>): Promise<Block> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/blocks',
      options: {
        headers,
        body: blockData
      }
    });
    return response.body as Block;
  } catch (error) {
    console.error('Error creating block:', error);
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
    const response = await get({
      apiName: 'flow-api',
      path: `/blocks/${blockId}/weeks`,
      options: { headers }
    });
    return response.body as Week[];
  } catch (error) {
    console.error('Error fetching weeks:', error);
    throw error;
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
    const response = await get({
      apiName: 'flow-api',
      path: `/weeks/${weekId}/days`,
      options: { headers }
    });
    return response.body as Day[];
  } catch (error) {
    console.error('Error fetching days:', error);
    throw error;
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

// Exercise endpoints
export const getExercisesForWorkout = async (workoutId: string): Promise<Exercise[]> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/workouts/${workoutId}/exercises`,
      options: { headers }
    });
    return response.body as Exercise[];
  } catch (error) {
    console.error('Error fetching exercises:', error);
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