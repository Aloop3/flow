import { useState, useEffect } from 'react';
import { getExerciseTypes, ExerciseTypeLibrary } from '../services/api';
import LoadingSpinner from './LoadingSpinner';


interface ExerciseSelectorProps {
  onSelect: (exerciseType: string) => void;
  selectedExercise?: string;
}

const ExerciseSelector = ({ onSelect, selectedExercise }: ExerciseSelectorProps) => {
  const [exerciseTypes, setExerciseTypes] = useState<ExerciseTypeLibrary>({} as ExerciseTypeLibrary);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Fetch exercise types on component mount
  useEffect(() => {
    const fetchExerciseTypes = async () => {
      setIsLoading(true);
      try {
        const data = await getExerciseTypes();
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
  }, []);
  
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
  
  return (
    <div className="border rounded-lg p-4 bg-white">
      <h3 className="text-lg font-medium mb-4">Exercise Library</h3>
      
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
        <div className="flex justify-center py-4">
          <LoadingSpinner />
        </div>
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
    </div>
  );
};

export default ExerciseSelector;