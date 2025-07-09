import React from 'react';
import type { Workout } from '../services/api';

interface WorkoutCompletionProps {
  workout: Workout;
  onClose?: () => void;
}

// Volume calculation utility
const calculateVolume = (workout: Workout, useActual: boolean = false): { lb: number; kg: number } => {
  let totalInDisplayUnit = 0;
  
  workout.exercises.forEach((exercise) => {
    let exerciseVolume: number;
    
    if (useActual && exercise.sets_data && exercise.sets_data.length > 0) {
      // Calculate actual volume from completed sets
      exerciseVolume = exercise.sets_data
        .filter(set => set.completed)
        .reduce((setTotal, set) => {
          return setTotal + (set.reps || 0) * (set.weight || 0);
        }, 0);
    } else {
      // Calculate planned volume using planned_sets_data if available
      if (exercise.planned_sets_data && exercise.planned_sets_data.length > 0) {
        exerciseVolume = exercise.planned_sets_data.reduce((total, set) => {
          return total + (set.reps || 0) * (set.weight || 0);
        }, 0);
      } else {
        // Fallback to legacy calculation for backward compatibility
        exerciseVolume = (exercise.sets || 0) * (exercise.reps || 0) * (exercise.weight || 0);
      }
    }
    
    totalInDisplayUnit += exerciseVolume;
  });
  
  // Check display unit from first exercise (backend sets this consistently)
  const displayUnit = workout.exercises[0]?.display_unit || 'lb';
  
  if (displayUnit === 'kg') {
    // Backend provided kg, convert to lb for display
    return {
      kg: Math.round(totalInDisplayUnit * 10) / 10,
      lb: Math.round(totalInDisplayUnit * 2.20462)
    };
  } else {
    // Backend provided lb, convert to kg for display
    return {
      lb: Math.round(totalInDisplayUnit),
      kg: Math.round(totalInDisplayUnit * 0.453592 * 10) / 10
    };
  }
};

// RPE calculation utility with fixed planned vs actual logic
const getHighestRPE = (workout: Workout, useActual: boolean = false): number => {
  let rpeValues: number[] = [];
  
  if (useActual) {
    // Get RPE from completed sets or exercise RPE if completed
    workout.exercises.forEach(exercise => {
      if (exercise.status === 'completed') {
        if (exercise.sets_data && exercise.sets_data.length > 0) {
          // Get RPE from individual sets
          const setRPEs = exercise.sets_data
            .filter(set => set.completed && set.rpe)
            .map(set => set.rpe!);
          rpeValues.push(...setRPEs);
        } else if (exercise.rpe) {
          // Fallback to exercise-level RPE
          rpeValues.push(exercise.rpe);
        }
      }
    });
  } else {
    // Get planned RPE using planned_sets_data if available
    workout.exercises.forEach(exercise => {
      if (exercise.planned_sets_data && exercise.planned_sets_data.length > 0) {
        // Get RPE from planned sets
        const plannedRPEs = exercise.planned_sets_data
          .filter(set => set.rpe)
          .map(set => set.rpe!);
        rpeValues.push(...plannedRPEs);
      } else if (exercise.rpe) {
        // Fallback to exercise-level RPE for backward compatibility
        rpeValues.push(exercise.rpe);
      }
    });
  }
  
  return rpeValues.length > 0 ? Math.max(...rpeValues) : 0;
};

// Format volume display
const formatVolume = (volume: { lb: number; kg: number }): string => {
  return `${volume.lb.toLocaleString()} lb | ${volume.kg.toLocaleString()} kg`;
};

// Calculate duration from workout timing
const formatDuration = (workout: Workout): string => {
  if (!workout.start_time || !workout.finish_time) {
    return 'N/A';
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
  } catch (error) {
    return 'N/A';
  }
};

// Get difference indicator
const getDifferenceIndicator = (planned: number, actual: number): string => {
  const diff = actual - planned;
  if (diff === 0) return '';
  if (diff > 0) return `(+${diff})`;
  return `(${diff})`;
};

// Collect all notes from workout and sets
const collectAllNotes = (workout: Workout): string[] => {
  const notes: string[] = [];
  
  // Add workout notes
  if (workout.notes && workout.notes.trim()) {
    notes.push(`Workout Notes: ${workout.notes.trim()}`);
  }
  
  // Add exercise set notes
  workout.exercises.forEach((exercise) => {
    if (exercise.sets_data && exercise.sets_data.length > 0) {
      exercise.sets_data.forEach((set, setIndex) => {
        if (set.notes && set.notes.trim()) {
          notes.push(`${exercise.exercise_type} Set ${setIndex + 1}: ${set.notes.trim()}`);
        }
      });
    }
  });
  
  return notes;
};

const WorkoutCompletion: React.FC<WorkoutCompletionProps> = ({ workout }) => {
  const plannedVolume = calculateVolume(workout, false);
  const actualVolume = calculateVolume(workout, true);
  const plannedRPE = getHighestRPE(workout, false);
  const actualRPE = getHighestRPE(workout, true);
  const totalExercises = workout.exercises.length;
  const completedExercises = workout.exercises.filter(ex => ex.status === 'completed').length;
  const duration = formatDuration(workout);
  const allNotes = collectAllNotes(workout);

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6 mt-4">
      {/* Centered title - no close button */}
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-green-900">🎉 Workout Completed!</h3>
      </div>

      {/* Session Duration */}
      <div className="mb-6 text-center">
        <div className="text-sm text-green-700 font-medium">Session Duration</div>
        <div className="text-2xl font-bold text-green-900">{duration}</div>
      </div>

      {/* Planned vs Actual Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Volume Comparison */}
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="text-sm font-medium text-green-800 mb-3">Volume</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Planned:</span>
              <span className="font-medium">{formatVolume(plannedVolume)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Actual:</span>
              <span className="font-medium text-green-700">
                {formatVolume(actualVolume)}
                {actualVolume.lb !== plannedVolume.lb && (
                  <span className="ml-1 text-xs">
                    {getDifferenceIndicator(plannedVolume.lb, actualVolume.lb)} lb
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* RPE Comparison */}
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="text-sm font-medium text-green-800 mb-3">Highest RPE</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Planned:</span>
              <span className="font-medium">{plannedRPE || 'N/A'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Actual:</span>
              <span className="font-medium text-green-700">
                {actualRPE || 'N/A'}
                {actualRPE && plannedRPE && actualRPE !== plannedRPE && (
                  <span className="ml-1 text-xs">
                    {getDifferenceIndicator(plannedRPE, actualRPE)}
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Exercise Completion */}
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="text-sm font-medium text-green-800 mb-3">Exercises</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Total:</span>
              <span className="font-medium">{totalExercises}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Completed:</span>
              <span className="font-medium text-green-700">
                {completedExercises}/{totalExercises}
                {completedExercises === totalExercises && (
                  <span className="ml-1 text-xs">✅</span>
                )}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Notes Section */}
      {allNotes.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="text-sm font-medium text-green-800 mb-3">Notes</h4>
          <div className="space-y-2">
            {allNotes.map((note, index) => (
              <div key={index} className="text-sm text-gray-700 bg-gray-50 rounded p-2">
                {note}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkoutCompletion;