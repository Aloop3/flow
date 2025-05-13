import { useState } from 'react';
import type { Exercise } from '../services/api';
import ExerciseTracker from './ExerciseTracker';
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
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'skipped':
        return 'bg-gray-100 text-gray-800';
      case 'planned':
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const handleExerciseClick = (exercise: Exercise) => {
    if (!readOnly) {
      setSelectedExercise(exercise);
    }
  };

  const handleComplete = () => {
    setSelectedExercise(null);
    onExerciseComplete();
  };

  // Calculate progress for sets
  const getSetProgress = (exercise: Exercise) => {
    // If the exercise doesn't have sets_data, return 0
    if (!exercise.sets_data || exercise.sets_data.length === 0) {
      return { completed: 0, total: exercise.sets };
    }

    // Count completed sets
    const completedSets = exercise.sets_data.filter((set) => set.completed).length;
    return {
      completed: completedSets,
      total: exercise.sets,
    };
  };

  return (
    <>
      <ul className="divide-y">
        {exercises.map((exercise) => {
          const setProgress = getSetProgress(exercise);
          const hasSetData = exercise.sets_data && exercise.sets_data.length > 0;

          return (
            <li
              key={exercise.exercise_id}
              className={`py-3 flex justify-between items-start ${
                !readOnly ? 'cursor-pointer hover:bg-gray-50' : ''
              }`}
              onClick={() => handleExerciseClick(exercise)}
            >
              <div className="flex-grow">
                <div className="flex justify-between items-center mb-1">
                  <h3 className="font-medium">{exercise.exercise_type}</h3>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(exercise.status)}`}
                  >
                    {exercise.status || 'planned'}
                  </span>
                </div>

                <p className="text-sm text-gray-600">
                  {exercise.sets} sets × {exercise.reps} reps
                  {exercise.rpe && ` @ RPE ${exercise.rpe}`}
                </p>

                {exercise.notes && <p className="mt-1 text-xs text-gray-500">{exercise.notes}</p>}

                {/* Set progress bar */}
                {hasSetData && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Set progress</span>
                      <span>
                        {setProgress.completed} / {setProgress.total} sets
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(setProgress.completed / setProgress.total) * 100}%` }}
                      ></div>
                    </div>

                    {/* Set numbers */}
                    {exercise.sets_data && exercise.sets_data.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {Array.from({ length: setProgress.total }, (_, i) => i + 1).map(
                          (setNum) => {
                            const setData = exercise.sets_data?.find(
                              (s) => s.set_number === setNum,
                            );
                            const isCompleted = setData?.completed;

                            return (
                              <div
                                key={setNum}
                                className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-medium ${
                                  isCompleted
                                    ? 'bg-green-100 text-green-800 border-2 border-green-300'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {setNum}
                              </div>
                            );
                          },
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ul>

      <Modal
        isOpen={!!selectedExercise}
        onClose={() => setSelectedExercise(null)}
        title={selectedExercise ? `${selectedExercise.exercise_type}` : 'Exercise Details'}
      >
        {selectedExercise && (
          <ExerciseTracker
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
