import React from 'react';
import type { Workout } from '../services/api';
import { useWeightUnit } from '../contexts/UserContext';

interface WorkoutSummaryProps {
  workout: Workout;
}

// Utility function to calculate total volume using sets_data
const calculateVolume = (workout: Workout, getDisplayUnit: (exerciseType: string) => 'kg' | 'lb'): { lb: number; kg: number } => {
  let totalKg = 0;
  let totalLb = 0;

  workout.exercises.forEach(exercise => {
    const displayUnit = exercise.display_unit || getDisplayUnit(exercise.exercise_type);
    
    if (exercise.sets_data && exercise.sets_data.length > 0) {
      // Use detailed sets_data for accurate calculation
      exercise.sets_data.forEach(set => {
        const setVolume = (set.weight || 0) * (set.reps || 0);
        
        if (displayUnit === 'kg') {
          totalKg += setVolume;
          totalLb += setVolume * 2.20462; // Convert kg to lb
        } else {
          totalLb += setVolume;
          totalKg += setVolume * 0.453592; // Convert lb to kg
        }
      });
    } else {
      // Fallback to exercise-level data if sets_data is not available
      const exerciseVolume = (exercise.sets || 0) * (exercise.reps || 0) * (exercise.weight || 0);
      
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
    kg: Math.round(totalKg * 10) / 10 // Round to 1 decimal place
  };
};

// Utility function to find highest RPE using sets_data
const getHighestRPE = (workout: Workout): number => {
  const rpeValues: number[] = [];
  
  workout.exercises.forEach(exercise => {
    if (exercise.sets_data && exercise.sets_data.length > 0) {
      // Use detailed sets_data for accurate RPE calculation
      exercise.sets_data.forEach(set => {
        if (set.rpe && set.rpe > 0) {
          rpeValues.push(set.rpe);
        }
      });
    } else {
      // Fallback to exercise-level RPE if sets_data is not available
      if (exercise.rpe && exercise.rpe > 0) {
        rpeValues.push(exercise.rpe);
      }
    }
  });
  
  return rpeValues.length > 0 ? Math.max(...rpeValues) : 0;
};

const WorkoutSummary: React.FC<WorkoutSummaryProps> = ({ workout }) => {
  const { getDisplayUnit } = useWeightUnit();
  const volume = calculateVolume(workout, getDisplayUnit);
  const highestRPE = getHighestRPE(workout);
  const totalExercises = workout.exercises.length;

  return (
    <div className="flex items-center justify-around bg-ocean-mist border border-ocean-teal/30 rounded-lg py-2 px-4 mb-4">
      <div className="text-center">
        <div className="text-xs text-ocean-slate uppercase tracking-wide">Volume</div>
        <div className="text-sm font-semibold text-ocean-navy-dark">{volume.lb.toLocaleString()} lb / {volume.kg.toLocaleString()} kg</div>
      </div>
      <div className="w-px h-6 bg-ocean-teal/20" />
      <div className="text-center">
        <div className="text-xs text-ocean-slate uppercase tracking-wide">Highest RPE</div>
        <div className="text-sm font-semibold text-ocean-navy-dark">{highestRPE > 0 ? highestRPE : '—'}</div>
      </div>
      <div className="w-px h-6 bg-ocean-teal/20" />
      <div className="text-center">
        <div className="text-xs text-ocean-slate uppercase tracking-wide">Exercises</div>
        <div className="text-sm font-semibold text-ocean-navy-dark">{totalExercises}</div>
      </div>
    </div>
  );
};

export default WorkoutSummary;