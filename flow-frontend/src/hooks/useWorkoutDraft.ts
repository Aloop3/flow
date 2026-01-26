import { useState, useEffect, useCallback } from 'react';
import { workoutStorage, type SetData, type WorkoutDraft } from '../services/workoutStorage';
import { workoutSync, type SyncStatus } from '../services/workoutSync';
import type { Exercise } from '../services/api';

interface UseWorkoutDraftReturn {
  // Data
  draft: WorkoutDraft | null;
  isLoading: boolean;

  // Getters
  getSetData: (exerciseId: string, setNumber: number) => SetData | undefined;
  getExerciseSets: (exerciseId: string) => Record<number, SetData>;
  getExerciseCompletion: (exerciseId: string, totalSets: number) => { completed: number; total: number };

  // Actions
  updateSet: (exerciseId: string, setNumber: number, data: Partial<SetData>) => void;
  toggleCompletion: (exerciseId: string, setNumber: number) => void;
  removeSet: (exerciseId: string, setNumber: number) => void;

  // Sync
  syncStatus: SyncStatus;
  syncNow: () => Promise<void>;

  // Lifecycle
  finishWorkout: () => Promise<void>;
  clearDraft: () => void;
}

export function useWorkoutDraft(
  dayId: string,
  serverExercises: Exercise[] | undefined
): UseWorkoutDraftReturn {
  const [draft, setDraft] = useState<WorkoutDraft | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');

  // Initialize draft from localStorage or server data
  useEffect(() => {
    if (!dayId) {
      setIsLoading(false);
      return;
    }

    // Only initialize when we have server exercises
    if (serverExercises && serverExercises.length > 0) {
      const existingDraft = workoutStorage.loadDraft(dayId, serverExercises);
      setDraft(existingDraft);
      setIsLoading(false);

      // Start background sync
      workoutSync.startSync(dayId);

      // Subscribe to sync status
      const unsubscribe = workoutSync.onStatusChange(setSyncStatus);

      return () => {
        unsubscribe();
        // Don't stop sync on unmount - let it continue if user navigates briefly
        // workoutSync.stopSync() will be called explicitly on finishWorkout
      };
    }
  }, [dayId, serverExercises]);

  // Reload draft from localStorage (triggers re-render with fresh data)
  const reloadDraft = useCallback(() => {
    if (!dayId) return;
    const updated = workoutStorage.loadDraft(dayId);
    setDraft(updated);
  }, [dayId]);

  // Get data for a specific set
  const getSetData = useCallback((exerciseId: string, setNumber: number): SetData | undefined => {
    return draft?.setsData[exerciseId]?.[setNumber];
  }, [draft]);

  // Get all sets for an exercise
  const getExerciseSets = useCallback((exerciseId: string): Record<number, SetData> => {
    return draft?.setsData[exerciseId] || {};
  }, [draft]);

  // Get completion stats for an exercise
  const getExerciseCompletion = useCallback((exerciseId: string, totalSets: number) => {
    const sets = draft?.setsData[exerciseId] || {};
    // Only count completed sets up to totalSets (handles stale localStorage data)
    let completed = 0;
    for (let i = 1; i <= totalSets; i++) {
      if (sets[i]?.completed) completed++;
    }
    return { completed, total: totalSets };
  }, [draft]);

  // Update a set's data
  const updateSet = useCallback((exerciseId: string, setNumber: number, data: Partial<SetData>) => {
    if (!dayId) return;
    workoutStorage.updateSet(dayId, exerciseId, setNumber, data);
    reloadDraft();
  }, [dayId, reloadDraft]);

  // Toggle completion for a set
  const toggleCompletion = useCallback((exerciseId: string, setNumber: number) => {
    if (!dayId) return;
    workoutStorage.toggleSetCompletion(dayId, exerciseId, setNumber);
    reloadDraft();
  }, [dayId, reloadDraft]);

  // Remove a set from localStorage (used when deleting a set via API)
  const removeSet = useCallback((exerciseId: string, setNumber: number) => {
    if (!dayId) return;
    workoutStorage.removeSet(dayId, exerciseId, setNumber);
    reloadDraft();
  }, [dayId, reloadDraft]);

  // Force sync now
  const syncNow = useCallback(async () => {
    await workoutSync.syncNow();
  }, []);

  // Finish workout - final sync and cleanup
  const finishWorkout = useCallback(async () => {
    if (!dayId) return;

    // Force final sync to ensure all data is saved
    await workoutSync.syncNow();

    // Clear local draft
    workoutStorage.clearDraft(dayId);

    // Stop background sync
    workoutSync.stopSync();

    // Clear local state
    setDraft(null);
  }, [dayId]);

  // Clear draft without syncing (for cancellation)
  const clearDraft = useCallback(() => {
    if (!dayId) return;
    workoutStorage.clearDraft(dayId);
    workoutSync.stopSync();
    setDraft(null);
  }, [dayId]);

  return {
    draft,
    isLoading,
    getSetData,
    getExerciseSets,
    getExerciseCompletion,
    updateSet,
    toggleCompletion,
    removeSet,
    syncStatus,
    syncNow,
    finishWorkout,
    clearDraft,
  };
}
