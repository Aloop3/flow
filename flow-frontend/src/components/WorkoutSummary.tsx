import React from 'react';
import type { Workout } from '../services/api';

interface WorkoutSummaryProps {
  workout: Workout;
}

// Utility function to calculate total volume
const calculateVolume = (workout: Workout): { lb: number; kg: number } => {
  const totalLb = workout.exercises.reduce((total, exercise) => {
    const exerciseVolume = (exercise.sets || 0) * (exercise.reps || 0) * (exercise.weight || 0);
    return total + exerciseVolume;
  }, 0);
  
  const totalKg = totalLb * 0.453592;
  
  return {
    lb: Math.round(totalLb),
    kg: Math.round(totalKg * 10) / 10 // Round to 1 decimal place
  };
};

// Utility function to find highest RPE
const getHighestRPE = (workout: Workout): number => {
  const rpeValues = workout.exercises
    .map(exercise => exercise.rpe || 0)
    .filter(rpe => rpe > 0);
  
  return rpeValues.length > 0 ? Math.max(...rpeValues) : 0;
};

// Utility function to format volume display
const formatVolume = (volume: { lb: number; kg: number }): string => {
  return `${volume.lb.toLocaleString()} lb | ${volume.kg.toLocaleString()} kg`;
};

const WorkoutSummary: React.FC<WorkoutSummaryProps> = ({ workout }) => {
  const volume = calculateVolume(workout);
  const highestRPE = getHighestRPE(workout);
  const totalExercises = workout.exercises.length;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
      <h3 className="text-sm font-medium text-blue-900 mb-3">Workout Overview</h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Total Volume */}
        <div className="text-center sm:text-left">
          <div className="text-xs text-blue-700 font-medium uppercase tracking-wide">
            Total Volume
          </div>
          <div className="text-lg font-bold text-blue-900 mt-1">
            {formatVolume(volume)}
          </div>
        </div>

        {/* Highest RPE */}
        <div className="text-center sm:text-left">
          <div className="text-xs text-blue-700 font-medium uppercase tracking-wide">
            Highest RPE
          </div>
          <div className="text-lg font-bold text-blue-900 mt-1">
            {highestRPE > 0 ? highestRPE : 'N/A'}
          </div>
        </div>

        {/* Total Exercises */}
        <div className="text-center sm:text-left">
          <div className="text-xs text-blue-700 font-medium uppercase tracking-wide">
            Total Exercises
          </div>
          <div className="text-lg font-bold text-blue-900 mt-1">
            {totalExercises}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkoutSummary;