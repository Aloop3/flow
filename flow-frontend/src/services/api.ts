import { fetchAuthSession, signOut } from 'aws-amplify/auth';
import { get, post, put, del } from 'aws-amplify/api';

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public originalError?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';

    // Capture stack trace for better debugging
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  // Helper method to check if error is conflict
  static isConflict(error: unknown): boolean {
    return error instanceof ApiError && error.statusCode === 409;
  }

  // Helper method to check if error is not found
  static isNotFound(error: unknown): boolean {
    return error instanceof ApiError && error.statusCode === 404;
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
  status: 'planned' | 'completed' | 'skipped';
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

export interface Workout {
  workout_id: string;
  athlete_id: string;
  day_id: string;
  date: string;
  notes?: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'skipped';
  exercises: Exercise[];
  total_volume?: number;
}

export interface ExerciseSetData {
  set_number: number;
  reps: number;
  weight: number;
  rpe?: number;
  completed: boolean;
  timestamp?: string;
  notes?: string;
}

// Update Exercise interface
export interface Exercise {
  sets_data?: ExerciseSetData[];
}

console.log('API Config:', {
  apiName: 'flow-api',
  endpoint: import.meta.env.VITE_API_URL || 'API_URL_NOT_SET',
});

// Helper to get auth headers
export const getAuthHeaders = async () => {
  try {
    const { tokens } = await fetchAuthSession();
    return {
      Authorization: `Bearer ${tokens?.idToken?.toString()}`,
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
        body: userData,
      },
    });
    return response as unknown as User;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const getUser = async (user_id: string): Promise<User | null> => {
  try {
    const headers = await getAuthHeaders();

    // Make the API request
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/users/${user_id}`,
      options: { headers },
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

export const updateUser = async (
  user_id: string,
  newUserData: Partial<User>,
): Promise<User | null> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await put({
      apiName: 'flow-api',
      path: `/users/${user_id}`,
      options: {
        headers,
        body: newUserData,
      },
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

    console.log('Fetching blocks for user ID:', user_id);

    // Make the API request using the same pattern as getUser
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/athletes/${user_id}/blocks`,
      options: { headers },
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

export const getBlock = async (block_id: string): Promise<Block | null> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching block with ID:', block_id);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/blocks/${block_id}`,
      options: { headers },
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
      number_of_week: Number(blockData.number_of_weeks) || 4, // Default to 4 weeks if not provided
    };

    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/blocks',
      options: {
        headers,
        body: formattedData,
      },
    });
    return response as unknown as Block;
  } catch (error) {
    console.error('Error creating block (details):', error);
    throw error;
  }
};

export const updateBlock = async (block_id: string, blockData: Partial<Block>): Promise<Block> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/blocks/${block_id}`,
      options: {
        headers,
        body: blockData,
      },
    });
    return response as unknown as Block;
  } catch (error) {
    console.error('Error updating block:', error);
    throw error;
  }
};

export const deleteBlock = async (block_id: string): Promise<void> => {
  try {
    const headers = await getAuthHeaders();
    await del({
      apiName: 'flow-api',
      path: `/blocks/${block_id}`,
      options: { headers },
    });
  } catch (error) {
    console.error('Error deleting block:', error);
    throw error;
  }
};

// Week endpoints
export const getWeeks = async (block_id: string): Promise<Week[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching weeks for block ID:', block_id);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/blocks/${block_id}/weeks`,
      options: { headers },
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
        return Array.isArray(parsedData) ? (parsedData as unknown as Week[]) : [];
      } catch (e) {
        console.error('Failed to parse weeks data:', e);
        return [];
      }
    }

    console.log('No weeks data found in response');
    return [];
  } catch (error) {
    console.error('Error fetching weeks:', error);
    return [];
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
        body: weekData,
      },
    });
    return response as unknown as Week;
  } catch (error) {
    console.error('Error creating week:', error);
    throw error;
  }
};

// Day endpoints
export const getDays = async (week_id: string): Promise<Day[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching days for week ID:', week_id);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/weeks/${week_id}/days`,
      options: { headers },
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
        return Array.isArray(parsedData) ? (parsedData as unknown as Day[]) : [];
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

export const getDay = async (day_id: string): Promise<Day | null> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching day with ID:', day_id);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/days/${day_id}`,
      options: { headers },
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
export const getExercisesForDay = async (day_id: string): Promise<Exercise[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching exercises for day with ID:', day_id);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/days/${day_id}/exercises`,
      options: { headers },
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
        body: dayData,
      },
    });
    return response as unknown as Day;
  } catch (error) {
    console.error('Error creating day:', error);
    throw error;
  }
};

export const updateDay = async (day_id: string, dayData: Partial<Day>): Promise<Day> => {
  try {
    const headers = await getAuthHeaders();
    const response = await put({
      apiName: 'flow-api',
      path: `/days/${day_id}`,
      options: {
        headers,
        body: dayData,
      },
    });
    return response as unknown as Day;
  } catch (error) {
    console.error('Error updating day:', error);
    throw error;
  }
};

// Workout endpoints
export const getWorkout = async (workout_id: string): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const response = await get({
      apiName: 'flow-api',
      path: `/workouts/${workout_id}`,
      options: { headers },
    });
    return response as unknown as Workout;
  } catch (error) {
    console.error('Error fetching workout:', error);
    throw error;
  }
};

export const getWorkoutByDay = async (
  athlete_id: string,
  day_id: string,
): Promise<Workout | null> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/athletes/${athlete_id}/days/${day_id}/workout`,
      options: { headers },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        console.log('Successfully fetched workout data:', responseData);
        return responseData as unknown as Workout;
      } catch (e) {
        console.error('Failed to parse workout data:', e);
        return null;
      }
    }

    return null;
  } catch (error) {
    console.error('Error fetching workout by day:', error);
    return null;
  }
};

export const createWorkout = async (
  day_id: string,
  exercises: Array<{
    exerciseType: string;
    sets: number;
    reps: number;
    weight: number;
    rpe?: number;
    notes?: string;
    sets_data?: Array<{
      set_number: number;
      reps: number;
      weight: number;
      rpe?: number;
      completed: boolean;
      notes?: string;
    }>;
  }>,
): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await post({
      apiName: 'flow-api',
      path: `/days/${day_id}/workout`,
      options: {
        headers,
        body: { exercises },
      },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseText = await actualResponse.body.text();
        const data = JSON.parse(responseText);
        return data;
      } catch (e) {
        console.error('Failed to parse workout response:', e);
        throw new Error('Invalid response format');
      }
    }

    throw new Error('No response data');
  } catch (error) {
    console.error('Error creating workout:', error);
    throw error;
  }
};

export const updateWorkout = async (
  workout_id: string,
  workoutData: Partial<Workout>,
): Promise<Workout> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await put({
      apiName: 'flow-api',
      path: `/workouts/${workout_id}`,
      options: {
        headers,
        body: JSON.stringify(workoutData),
      },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        return responseData as unknown as Workout;
      } catch (e) {
        console.error('Failed to parse workout update response:', e);
        throw new Error('Invalid response format');
      }
    }

    throw new Error('No response data');
  } catch (error) {
    console.error('Error updating workout:', error);
    throw error;
  }
};

export const copyWorkout = async (sourceDayId: string, targetDayId: string): Promise<any> => {
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
          target_day_id: targetDayId,
        },
      },
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

    // Return true if successful but no detailed response
    return true;
  } catch (error) {
    // Check for specific status codes
    if (error instanceof ApiError && error.statusCode === 409) {
      throw new ApiError('Target day already has a workout. Please delete it first.', 409, error);
    }
    console.error('Error copying workout:', error);
    throw error;
  }
};

export const getWorkoutStatus = (
  exercises: Exercise[],
): 'not_started' | 'in_progress' | 'completed' | 'skipped' => {
  if (!exercises || exercises.length === 0) {
    return 'not_started';
  }

  const completedCount = exercises.filter((ex) => ex.status === 'completed').length;
  const totalCount = exercises.length;

  if (completedCount === 0) {
    return 'not_started';
  } else if (completedCount === totalCount) {
    return 'completed';
  } else {
    return 'in_progress';
  }
};

// Exercise endpoints
export const createExercise = async (
  exerciseData: {
    workout_id: string;
    exercise_type: string;
    sets: number;
    reps: number;
    weight: number;
    rpe?: number;
    status?: 'planned' | 'completed' | 'skipped';
    notes?: string;
  }
): Promise<Exercise> => {
  try {
    const headers = await getAuthHeaders();
    const response = await post({
      apiName: 'flow-api',
      path: '/exercises',
      options: {
        headers,
        body: exerciseData,
      },
    });
    const actualResponse = await response.response;
    
    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        return responseData as unknown as Exercise;
      } catch (e) {
        console.error('Failed to parse response in createExercise:', e);
        throw new Error('Invalid response format');
      }
    }
    
    throw new Error('No response data');
  } catch (error) {
    console.error('Error creating exercise:', error);
    throw error;
  }
};
 
export const deleteExercise = async (exerciseId: string): Promise<void> => {
  try {
    const headers = await getAuthHeaders();
    await del({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}`,
      options: { headers },
    });
  } catch (error) {
    console.error('Error deleting exercise:', error);
    throw error;
  }
};

export const getExercisesForWorkout = async (workout_id: string): Promise<Exercise[]> => {
  try {
    if (!workout_id) {
      console.error('Missing workout_id parameter in getExercisesForWorkout');
      return [];
    }

    console.log(`Fetching exercises for workout: ${workout_id}`);
    const headers = await getAuthHeaders();
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/workouts/${workout_id}/exercises`,
      options: { headers },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        return Array.isArray(responseData) ? (responseData as unknown as Exercise[]) : [];
      } catch (e) {
        console.error('Error parsing exercise response:', e);
        return [];
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
      options: { headers },
    });

    // For Amplify v6, we need to await the response and parse it
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const parsedData = await actualResponse.body.json();
        if (!parsedData) {
          throw new Error('No exercise data received');
        }
        return parsedData as ExerciseTypeLibrary;
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

export const updateExercise = async (
  exerciseId: string,
  updateData: Partial<Exercise>,
): Promise<Exercise> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await put({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}`,
      options: {
        headers,
        body: updateData as any,
      },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const result = await actualResponse.body.json();
        return result as unknown as Exercise;
      } catch (e) {
        console.error('Failed to parse response:', e);
        throw new Error('Invalid response format');
      }
    }

    throw new Error('No response data');
  } catch (error) {
    console.error('Error updating exercise:', error);
    throw error;
  }
};

export const completeExercise = async (
  exercise_id: string,
  completionData: {
    sets: number;
    reps: number;
    weight: number;
    rpe?: number;
    notes?: string;
  },
): Promise<Exercise> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await post({
      apiName: 'flow-api',
      path: `/exercises/${exercise_id}/complete`,
      options: {
        headers,
        body: completionData,
      },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        if (!responseData) {
          throw new Error('No exercise data returned');
        }
        return responseData as unknown as Exercise;
      } catch (e) {
        console.error('Failed to parse response in completeExercise:', e);
        throw new Error('Invalid response format');
      }
    }

    throw new Error('No response data');
  } catch (error) {
    console.error('Error completing exercise:', error);
    throw error;
  }
};

// Add function to track sets
export const trackExerciseSet = async (
  exerciseId: string,
  setNumber: number,
  setData: {
    reps: number;
    weight: number;
    rpe?: number;
    completed?: boolean;
    notes?: string;
  },
): Promise<Exercise> => {
  try {
    const headers = await getAuthHeaders();
    const apiResponse = await post({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}/sets/${setNumber}`,
      options: {
        headers,
        body: setData,
      },
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;

    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        return responseData as unknown as Exercise;
      } catch (e) {
        console.error('Failed to parse response in trackExerciseSet:', e);
        throw new Error('Invalid response format');
      }
    }

    throw new Error('No response data');
  } catch (error) {
    console.error('Error tracking exercise set:', error);
    throw error;
  }
};

export const deleteSet = async (exerciseId: string, setNumber: number): Promise<void> => {
  try {
    const headers = await getAuthHeaders();
    await del({
      apiName: 'flow-api',
      path: `/exercises/${exerciseId}/sets/${setNumber}`,
      options: { headers },
    });
  } catch (error) {
    console.error('Error deleting set:', error);
    throw error;
  }
};

// Relationship endpoints
export const getCoachRelationships = async (coachId: string, status: 'active' | 'pending' | 'ended' = 'active'): Promise<any[]> => {
  try {
    const headers = await getAuthHeaders();
    console.log('Fetching relationships for coach:', coachId);
    const apiResponse = await get({
      apiName: 'flow-api',
      path: `/coaches/${coachId}/relationships?status=${status}`,
      options: { headers }
    });

    // For Amplify v6, await the response
    const actualResponse = await apiResponse.response;
    
    if (actualResponse && actualResponse.body) {
      try {
        const responseData = await actualResponse.body.json();
        console.log('Coach relationships data:', responseData);
        return Array.isArray(responseData) ? responseData : [];
      } catch (e) {
        console.error('Failed to parse relationships data:', e);
        return [];
      }
    }
    
    return [];
  } catch (error) {
    console.error('Error fetching coach relationships:', error);
    return [];
  }
};