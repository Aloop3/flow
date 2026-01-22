import { useState, useEffect } from 'react';
import { getExerciseTypes, createCustomExercise, ExerciseTypeLibrary } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

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

  // Loading skeleton
  const ExerciseSelectorSkeleton = () => (
    <div className="space-y-4">
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map(i => (
          <Skeleton key={i} className="h-8 w-20" />
        ))}
      </div>
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map(i => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    </div>
  );

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg">Exercise Library</CardTitle>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setShowCustomModal(true)}
            className="bg-green-600 text-white hover:bg-green-700"
          >
            + Custom Exercise
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Search input */}
        <div className="mb-4">
          <Input
            type="text"
            placeholder="Search exercises..."
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
                <Button
                  key={category}
                  size="sm"
                  variant={activeCategory === category ? "default" : "outline"}
                  onClick={() => setActiveCategory(category)}
                  className="whitespace-nowrap"
                >
                  {formatCategoryName(category)}
                </Button>
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
                        className={`w-full text-left px-4 py-2 hover:bg-muted ${
                          selectedExercise === exercise ? 'bg-blue-50' : ''
                        }`}
                      >
                        {exercise}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="p-4 text-center text-muted-foreground">
                  No exercises found. Try a different search or category.
                </p>
              )}
            </div>
          </>
        )}

        {/* Custom Exercise Dialog */}
        <Dialog open={showCustomModal} onOpenChange={setShowCustomModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Custom Exercise</DialogTitle>
            </DialogHeader>

            {customError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
                {customError}
              </div>
            )}

            <form onSubmit={handleCreateCustomExercise} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Exercise Name
                </label>
                <Input
                  type="text"
                  value={customExerciseName}
                  onChange={(e) => setCustomExerciseName(e.target.value)}
                  placeholder="e.g., Bulgarian Split Squat"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <Select
                  value={customExerciseCategory}
                  onValueChange={setCustomExerciseCategory}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {validCategories.map(category => (
                      <SelectItem key={category} value={category}>
                        {formatCategoryName(category)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCustomModal(false);
                    setCustomExerciseName('');
                    setCustomExerciseCategory('barbell');
                    setCustomError(null);
                  }}
                  disabled={isCreatingCustom}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isCreatingCustom || !customExerciseName.trim()}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {isCreatingCustom ? 'Creating...' : 'Create Exercise'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default ExerciseSelector;
