import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
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
      <Card>
        <CardContent className="pt-6 space-y-4">
          <Skeleton className="h-6 w-1/2" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!activeBlock) {
    return (
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Today's Workout</h2>
          <p className="text-muted-foreground mb-4">Create a training program to see today's workout</p>
          <Button asChild>
            <Link to="/blocks/new">Create Program</Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!todaysWorkout) {
    return (
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Today's Workout</h2>
          <p className="text-muted-foreground mb-4">No workout scheduled for today</p>
          <div className="text-sm text-muted-foreground/70">
            Rest day or outside program schedule
          </div>
        </CardContent>
      </Card>
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
    <Card className="border-l-4 border-l-blue-500">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Today's Workout</h2>
          <Badge className={getStatusColor(workoutStatus)}>
            {getStatusText(workoutStatus)}
          </Badge>
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

          <p className="text-sm text-muted-foreground">{day.notes}</p>

          {hasExercises && (
            <div className="bg-muted p-3 rounded-md">
              <p className="text-sm font-medium text-gray-700 mb-1">
                {workout!.exercises.length} exercises planned
              </p>
              <div className="text-xs text-muted-foreground">
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
            <Button asChild className="w-full">
              <Link to={`/days/${day.day_id}`}>
                {getActionButtonText(workoutStatus)}
              </Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TodaysWorkoutCard;