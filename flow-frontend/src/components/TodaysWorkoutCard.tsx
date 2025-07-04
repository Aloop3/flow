import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getWeeks, getDays, getWorkoutByDay, Block, Day, Workout } from '../services/api';

interface TodaysWorkoutCardProps {
  activeBlock: Block | null;
  userId: string;
}

const TodaysWorkoutCard: React.FC<TodaysWorkoutCardProps> = ({ activeBlock, userId }) => {
  const [todaysWorkout, setTodaysWorkout] = useState<{
    day: Day;
    workout: Workout | null;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTodaysWorkout = async () => {
      if (!activeBlock) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);

        // Get today's date
        const today = new Date().toISOString().split('T')[0];
        
        // Get all weeks for the active block
        const weeks = await getWeeks(activeBlock.block_id);
        
        // Get all days for each week and find today's day
        let todaysDay: Day | null = null;
        for (const week of weeks) {
          const days = await getDays(week.week_id);
          const foundDay = days.find(day => day.date === today);
          if (foundDay) {
            todaysDay = foundDay;
            break;
          }
        }
        
        if (!todaysDay) {
          setTodaysWorkout(null);
          setIsLoading(false);
          return;
        }

        // Try to get existing workout for today
        let workout = null;
        try {
          workout = await getWorkoutByDay(userId, todaysDay.day_id);
        } catch (workoutError) {
          // No workout exists yet - that's okay
          console.log('No workout found for today:', workoutError);
        }

        setTodaysWorkout({
          day: todaysDay,
          workout: workout
        });
      } catch (err) {
        console.error('Error fetching today\'s workout:', err);
        setError('Failed to load today\'s workout');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTodaysWorkout();
  }, [activeBlock, userId]);

  if (isLoading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          <p className="text-sm text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!activeBlock) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Today's Workout</h2>
        <p className="text-gray-500 mb-4">Create a training program to see today's workout</p>
        <Link
          to="/blocks/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          Create Program
        </Link>
      </div>
    );
  }

  if (!todaysWorkout) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Today's Workout</h2>
        <p className="text-gray-500 mb-4">No workout scheduled for today</p>
        <div className="text-sm text-gray-400">
          Rest day or outside program schedule
        </div>
      </div>
    );
  }

  const { day, workout } = todaysWorkout;

  const getWorkoutStatus = (): Workout['status'] => {
    if (!workout) return 'not_started';
    return workout.status;
  };

  const getStatusColor = (status: Workout['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'skipped':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusText = (status: Workout['status']) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'skipped':
        return 'Skipped';
      default:
        return 'Planned';
    }
  };

  const getActionButtonText = (status: Workout['status']) => {
    switch (status) {
      case 'completed':
        return 'View Workout';
      case 'in_progress':
        return 'Continue Workout';
      case 'skipped':
        return 'View Day';
      default:
        return 'Start Workout';
    }
  };

  const workoutStatus = getWorkoutStatus();
  const hasExercises = workout?.exercises?.length && workout.exercises.length > 0;

  return (
    <div className="bg-white shadow rounded-lg p-6 border-l-4 border-blue-500">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Today's Workout</h2>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(workoutStatus)}`}>
          {getStatusText(workoutStatus)}
        </span>
      </div>

      <div className="space-y-3">
        {day.focus && (
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-700">
              {day.focus.charAt(0).toUpperCase() + day.focus.slice(1)} Focus
            </span>
          </div>
        )}

        <p className="text-sm text-gray-600">{day.notes}</p>

        {hasExercises && (
          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-sm font-medium text-gray-700 mb-1">
              {workout!.exercises.length} exercises planned
            </p>
            <div className="text-xs text-gray-500">
              {workout!.exercises.slice(0, 3).map((exercise, index) => (
                <span key={index}>
                  {exercise.exercise_type}
                  {index < Math.min(workout!.exercises.length - 1, 2) ? ', ' : ''}
                </span>
              ))}
              {workout!.exercises.length > 3 && '...'}
            </div>
          </div>
        )}

        <div className="pt-2">
          <Link
            to={`/days/${day.day_id}`}
            className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            {getActionButtonText(workoutStatus)}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default TodaysWorkoutCard;