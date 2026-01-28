import React from 'react';
import type { Workout } from '../services/api';

interface WorkoutCompletionProps {
  workout: Workout;
}

// Volume calculation utility
const calculateVolume = (workout: Workout): { lb: number; kg: number } => {
  let totalLb = 0;
  let totalKg = 0;

  workout.exercises.forEach((exercise) => {
    const displayUnit = exercise.display_unit || 'lb';

    if (exercise.sets_data && exercise.sets_data.length > 0) {
      const exerciseVolume = exercise.sets_data
        .filter(set => set.completed)
        .reduce((setTotal, set) => {
          return setTotal + (set.reps || 0) * (set.weight || 0);
        }, 0);

      if (displayUnit === 'kg') {
        totalKg += exerciseVolume;
        totalLb += exerciseVolume * 2.20462;
      } else {
        totalLb += exerciseVolume;
        totalKg += exerciseVolume * 0.453592;
      }
    }
  });

  return {
    lb: Math.round(totalLb),
    kg: Math.round(totalKg * 10) / 10
  };
};

// RPE calculation utility
const getHighestRPE = (workout: Workout): number => {
  const rpeValues: number[] = [];

  workout.exercises.forEach(exercise => {
    if (exercise.sets_data && exercise.sets_data.length > 0) {
      exercise.sets_data
        .filter(set => set.completed && set.rpe)
        .forEach(set => rpeValues.push(set.rpe!));
    }
  });

  return rpeValues.length > 0 ? Math.max(...rpeValues) : 0;
};

// Calculate duration from workout timing
const formatDuration = (workout: Workout): string => {
  if (!workout.start_time || !workout.finish_time) {
    return '—';
  }

  try {
    const start = new Date(workout.start_time);
    const finish = new Date(workout.finish_time);
    const durationMs = finish.getTime() - start.getTime();
    const durationMinutes = Math.floor(durationMs / (1000 * 60));

    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  } catch {
    return '—';
  }
};

const WorkoutCompletion: React.FC<WorkoutCompletionProps> = ({ workout }) => {
  const volume = calculateVolume(workout);
  const highestRPE = getHighestRPE(workout);
  const completedExercises = workout.exercises.filter(ex => ex.status === 'completed').length;
  const duration = formatDuration(workout);

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg pt-3 pb-2 px-4 mb-2 text-center">
      <h3 className="text-base font-semibold text-green-900">🎉 Workout Completed!</h3>
      <div className="text-xs text-green-700 mb-2">Duration: {duration}</div>

      <div className="flex items-center justify-around py-2">
        <div>
          <div className="text-xs text-green-700 uppercase tracking-wide">Volume</div>
          <div className="text-sm font-semibold text-green-900">{volume.lb.toLocaleString()} lb / {volume.kg.toLocaleString()} kg</div>
        </div>
        <div className="w-px h-6 bg-green-200" />
        <div>
          <div className="text-xs text-green-700 uppercase tracking-wide">Top RPE</div>
          <div className="text-sm font-semibold text-green-900">{highestRPE > 0 ? highestRPE : '—'}</div>
        </div>
        <div className="w-px h-6 bg-green-200" />
        <div>
          <div className="text-xs text-green-700 uppercase tracking-wide">Exercises</div>
          <div className="text-sm font-semibold text-green-900">{completedExercises}</div>
        </div>
      </div>
    </div>
  );
};

export default WorkoutCompletion;
