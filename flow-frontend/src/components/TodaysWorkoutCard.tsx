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
      <div className="py-6">
        <h2 className="text-2xl font-bold font-display text-ocean-navy-dark mb-2">Today's Workout</h2>
        <p className="text-ocean-slate mb-4">Start by creating a training program.</p>
        <Button asChild>
          <Link to="/blocks/new">Create Program</Link>
        </Button>
      </div>
    );
  }

  if (!todaysWorkout) {
    return (
      <div className="py-6">
        <h2 className="text-2xl font-bold font-display text-ocean-navy-dark mb-2">Today's Workout</h2>
        <p className="text-ocean-slate">Rest day</p>
        <p className="text-sm text-ocean-slate-light mt-1">No workout scheduled — enjoy the recovery.</p>
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
        return 'bg-ocean-seafoam-light text-ocean-seafoam';
      case 'in_progress':
        return 'bg-ocean-teal/10 text-ocean-teal';
      case 'skipped':
        return 'bg-ocean-mist text-ocean-slate';
      default:
        return 'bg-ocean-mist text-ocean-navy';
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
    <Card className="border-l-4 border-l-ocean-teal shadow-md">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold font-display text-ocean-navy-dark">Today's Workout</h2>
          <Badge className={getStatusColor(workoutStatus)}>
            {getStatusText(workoutStatus)}
          </Badge>
        </div>

        <div className="space-y-3">
          {day.focus && (
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-ocean-teal rounded-full"></div>
              <span className="text-sm font-medium text-ocean-navy">
                {day.focus.charAt(0).toUpperCase() + day.focus.slice(1)} Focus
              </span>
            </div>
          )}

          <p className="text-sm text-muted-foreground">{day.notes}</p>

          {hasExercises && (
            <div className="bg-ocean-mist p-3 rounded-md">
              <p className="text-sm font-medium text-ocean-navy mb-1">
                {workout!.exercises.length} exercises planned
              </p>
              <div className="text-xs text-ocean-slate">
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