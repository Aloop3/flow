import { useState } from 'react';
import { post } from 'aws-amplify/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Set {
  set_number: number;
  reps: number | null;
  weight: number | null;
  rpe?: number | null;
  notes?: string;
}

interface ExerciseFormProps {
  exerciseType: string;
  exerciseId: string;
  workoutId: string;
  onSetLogged: () => void;
}

export default function ExerciseForm({ exerciseType, exerciseId, workoutId, onSetLogged }: ExerciseFormProps) {
  const [sets, setSets] = useState<Set[]>([
    { set_number: 1, reps: null, weight: null }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addSet = () => {
    setSets([...sets, { set_number: sets.length + 1, reps: null, weight: null }]);
  };

  const updateSet = (index: number, field: keyof Set, value: number | string) => {
    const updatedSets = [...sets];

    // Handle empty string case specially
    const finalValue = typeof value === 'string' && value === ''
      ? null  // Store null when input is empty
      : typeof value === 'string'
        ? Number(value)
        : value;

    updatedSets[index] = { ...updatedSets[index], [field]: finalValue };
    setSets(updatedSets);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Convert null values to 0 before submission
      const setsToSubmit = sets.map(set => ({
        ...set,
        reps: set.reps ?? 0,
        weight: set.weight ?? 0,
        rpe: set.rpe === undefined ? null : set.rpe
      }));

      // Submit exercise with sets to API
      await post({
        apiName: 'flow-api',
        path: `/exercises/${exerciseId}/sets`,
        options: {
          body: {
            workout_id: workoutId,
            sets: setsToSubmit
          }
        }
      });
      onSetLogged();
    } catch (error) {
      console.error('Error logging exercise:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{exerciseType}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">Set</TableHead>
                <TableHead>Weight</TableHead>
                <TableHead>Reps</TableHead>
                <TableHead>RPE</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sets.map((set, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{set.set_number}</TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={set.weight === null ? '' : set.weight}
                      onChange={(e) => updateSet(index, 'weight', e.target.value)}
                      className="w-20"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={set.reps === null ? '' : set.reps}
                      onChange={(e) => updateSet(index, 'reps', e.target.value)}
                      className="w-16"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={set.rpe === null ? '' : (set.rpe || '')}
                      onChange={(e) => updateSet(index, 'rpe', e.target.value)}
                      className="w-16"
                      placeholder="1-10"
                      min={0}
                      max={10}
                      step={0.5}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="mt-4 flex justify-between">
          <Button variant="secondary" onClick={addSet}>
            Add Set
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Exercise'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
