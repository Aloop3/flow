import { useState, useEffect } from 'react';
import { getExerciseTypes, createCustomExercise, ExerciseTypeLibrary } from '../services/api';
import { ExerciseSelectorSkeleton } from './SkeletonLoader';



interface ExerciseSelectorProps {
  onSelect: (exerciseType: string) => void;
  selectedExercise?: string;
  userId?: string;
}

const ExerciseSelector = ({ onSelect, selectedExercise, userId }: ExerciseSelectorProps) => {
  const [exerciseTypes, setExerciseTypes] = useState<ExerciseTypeLibrary>({} as ExerciseTypeLibrary);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Custom exercise modal state
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [customExerciseName, setCustomExerciseName] = useState('');
  const [customExerciseCategory, setCustomExerciseCategory] = useState('barbell');
  const [isCreatingCustom, setIsCreatingCustom] = useState(false);
  const [customError, setCustomError] = useState<string | null>(null);
  
  // Valid categories for custom exercises
  const validCategories = ['barbell', 'dumbbell', 'bodyweight', 'machine', 'cable'];
  
  // Fetch exercise types on component mount
  useEffect(() => {
    const fetchExerciseTypes = async () => {
      setIsLoading(true);
      try {
        const data = await getExerciseTypes(userId);
        setExerciseTypes(data);
        setError(null);
      } catch (err) {
        setError('Failed to load exercise library');
        console.error('Error loading exercise library:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchExerciseTypes();
  }, [userId]);
  
  // Refresh exercise library after creating custom exercise
  const refreshExerciseLibrary = async () => {
    try {
      const data = await getExerciseTypes(userId);
      setExerciseTypes(data);
    } catch (err) {
      console.error('Error refreshing exercise library:', err);
    }
  };
  
  // Filter exercises based on search term
  const filteredExercises = searchTerm.trim() === '' 
    ? exerciseTypes[activeCategory] || [] 
    : (exerciseTypes[activeCategory] || []).filter(ex => 
        ex.toLowerCase().includes(searchTerm.toLowerCase())
      );
  
  // Display categories nicely
  const formatCategoryName = (category: string) => {
    return category.charAt(0).toUpperCase() + category.slice(1);
  };
  
  // Handle custom exercise creation
  const handleCreateCustomExercise = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userId) {
      setCustomError('User ID required to create custom exercises');
      return;
    }
    
    if (!customExerciseName.trim()) {
      setCustomError('Exercise name is required');
      return;
    }
    
    // Check for duplicates across all categories
    const allExercises = Object.values(exerciseTypes).flat();
    const exerciseExists = allExercises.some(
      exercise => exercise.toLowerCase() === customExerciseName.trim().toLowerCase()
    );
    
    if (exerciseExists) {
      setCustomError('This exercise already exists in the library');
      return;
    }
    
    setIsCreatingCustom(true);
    setCustomError(null);
    
    try {
      await createCustomExercise(userId, {
        name: customExerciseName.trim(),
        category: customExerciseCategory.toLowerCase()
      });
      
      // Reset form and close modal
      setCustomExerciseName('');
      setCustomExerciseCategory('barbell');
      setShowCustomModal(false);
      
      // Refresh the exercise library
      await refreshExerciseLibrary();
      
      // Auto-select the new exercise
      onSelect(customExerciseName.trim());
      
    } catch (err: any) {
      console.error('Error creating custom exercise:', err);
      setCustomError('Failed to create custom exercise. Please try again.');
    } finally {
      setIsCreatingCustom(false);
    }
  };
  
  return (
    <div className="border rounded-lg p-4 bg-white">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Exercise Library</h3>
        <button
          onClick={() => setShowCustomModal(true)}
          className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          + Custom Exercise
        </button>
      </div>
      
      {/* Search input */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search exercises..."
          className="w-full px-3 py-2 border rounded-md"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      {isLoading ? (
        <ExerciseSelectorSkeleton />
      ) : error ? (
        <div className="text-red-500 text-center py-4">
          {error}
        </div>
      ) : (
        <>
          {/* Category tabs */}
          <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
            {Object.keys(exerciseTypes).map(category => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`px-3 py-1 text-sm rounded-full whitespace-nowrap ${
                  activeCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {formatCategoryName(category)}
              </button>
            ))}
          </div>
          
          {/* Exercise list */}
          <div className="max-h-60 overflow-y-auto border rounded">
            {filteredExercises.length > 0 ? (
              <ul className="divide-y">
                {filteredExercises.map((exercise) => (
                  <li key={exercise}>
                    <button
                      onClick={() => onSelect(exercise)}
                      className={`w-full text-left px-4 py-2 hover:bg-gray-50 ${
                        selectedExercise === exercise ? 'bg-blue-50' : ''
                      }`}
                    >
                      {exercise}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="p-4 text-center text-gray-500">
                No exercises found. Try a different search or category.
              </p>
            )}
          </div>
        </>
      )}
      
      {/* Custom Exercise Modal */}
      {showCustomModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h4 className="text-lg font-medium mb-4">Create Custom Exercise</h4>
            
            {customError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded mb-4">
                {customError}
              </div>
            )}
            
            <form onSubmit={handleCreateCustomExercise} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Exercise Name
                </label>
                <input
                  type="text"
                  value={customExerciseName}
                  onChange={(e) => setCustomExerciseName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="e.g., Bulgarian Split Squat"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={customExerciseCategory}
                  onChange={(e) => setCustomExerciseCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  {validCategories.map(category => (
                    <option key={category} value={category}>
                      {formatCategoryName(category)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCustomModal(false);
                    setCustomExerciseName('');
                    setCustomExerciseCategory('barbell');
                    setCustomError(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                  disabled={isCreatingCustom}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingCustom || !customExerciseName.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isCreatingCustom ? 'Creating...' : 'Create Exercise'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseSelector;