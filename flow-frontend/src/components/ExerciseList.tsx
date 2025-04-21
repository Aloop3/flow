import { useState } from 'react';
import type { Exercise } from '../services/api';
import ExerciseCompletion from './ExerciseCompletion';
import Modal from './Modal';

interface ExerciseListProps {
  exercises: Exercise[];
  onExerciseComplete: () => void;
  readOnly?: boolean;
}

const ExerciseList = ({ exercises, onExerciseComplete, readOnly = false }: ExerciseListProps) => {
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'skipped':
        return 'bg-gray-100 text-gray-800';
      case 'planned':
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const handleExerciseClick = (exercise: Exercise) => {
    if (!readOnly && exercise.status !== 'completed') {
      setSelectedExercise(exercise);
    }
  };

  const handleComplete = () => {
    setSelectedExercise(null);
    onExerciseComplete();
  };

  return (
    <>
      <ul className="divide-y">
        {exercises.map((exercise) => (
          <li 
            key={exercise.exercise_id} 
            className={`py-3 flex justify-between items-center ${
              !readOnly && exercise.status !== 'completed' ? 'cursor-pointer hover:bg-gray-50' : ''
            }`}
            onClick={() => handleExerciseClick(exercise)}
          >
            <div>
              <h3 className="font-medium">{exercise.exercise_type}</h3>
              <p className="text-sm text-gray-600">
                {exercise.sets} sets × {exercise.reps} reps @ {exercise.weight} lbs
                {exercise.rpe && ` @ RPE ${exercise.rpe}`}
              </p>
              {exercise.notes && (
                <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>
              )}
            </div>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(exercise.status)}`}>
              {exercise.status || 'planned'}
            </span>
          </li>
        ))}
      </ul>

      <Modal
        isOpen={!!selectedExercise}
        onClose={() => setSelectedExercise(null)}
        title="Complete Exercise"
      >
        {selectedExercise && (
          <ExerciseCompletion
            exercise={selectedExercise}
            onComplete={handleComplete}
            onCancel={() => setSelectedExercise(null)}
          />
        )}
      </Modal>
    </>
  );
};

export default ExerciseList;