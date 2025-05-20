import { useState, useEffect } from 'react';
import { getCoachRelationships, getAthleteRelationships, endRelationship, getUser } from '../services/api';
import FormButton from './FormButton';

interface RelationshipsListProps {
  user: any;
  onRelationshipChange: () => void;
}

const RelationshipsList = ({ user, onRelationshipChange }: RelationshipsListProps) => {
  const [relationships, setRelationships] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEnding, setIsEnding] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRelationships = async () => {
      setIsLoading(true);
      try {
        let relationshipsData: any[] = [];
        
        if (user.role === 'coach') {
          relationshipsData = await getCoachRelationships(user.user_id, 'active');
        } else if (user.role === 'athlete') {
          relationshipsData = await getAthleteRelationships(user.user_id, 'active');
        }
        
        // Fetch names for related users
        const enhancedRelationships = await Promise.all(
          relationshipsData.map(async (rel) => {
            try {
              const targetId = user.role === 'coach' ? rel.athlete_id : rel.coach_id;
              if (targetId) {
                const targetUser = await getUser(targetId);
                return {
                  ...rel,
                  targetName: targetUser?.name || 'Unknown User'
                };
              }
              return rel;
            } catch (err) {
              console.error('Error fetching related user:', err);
              return {
                ...rel,
                targetName: 'Unknown User'
              };
            }
          })
        );
        
        setRelationships(enhancedRelationships);
      } catch (err) {
        console.error('Error fetching relationships:', err);
        setError('Failed to load relationships');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRelationships();
  }, [user]);

  const handleEndRelationship = async (relationshipId: string) => {
    if (!confirm('Are you sure you want to end this relationship?')) {
      return;
    }
    
    setIsEnding(relationshipId);
    setError(null);
    
    try {
      await endRelationship(relationshipId);
      
      // Update the list
      setRelationships(prev => prev.filter(r => r.relationship_id !== relationshipId));
      
      if (onRelationshipChange) {
        onRelationshipChange();
      }
    } catch (err) {
      console.error('Error ending relationship:', err);
      setError('Failed to end relationship');
    } finally {
      setIsEnding(null);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-lg font-medium mb-4">
        {user.role === 'coach' ? 'Your Athletes' : 'Your Coach'}
      </h2>
      
      {error && (
        <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-md border border-red-200">
          {error}
        </div>
      )}
      
      {isLoading ? (
        <div className="py-4 text-center text-gray-500">Loading relationships...</div>
      ) : relationships.length === 0 ? (
        <div className="py-4 text-center text-gray-500">
          {user.role === 'coach'
            ? 'You are not connected with any athletes yet.'
            : 'You are not connected with any coach yet.'}
        </div>
      ) : (
        <ul className="divide-y">
          {relationships.map(rel => (
            <li key={rel.relationship_id} className="py-4 flex justify-between items-center">
              <div>
                <p className="font-medium">{rel.targetName}</p>
                <p className="text-sm text-gray-500">
                  {new Date(rel.created_at).toLocaleDateString()}
                </p>
              </div>
              <FormButton
                type="button"
                variant="danger"
                size="sm"
                onClick={() => handleEndRelationship(rel.relationship_id)}
                isLoading={isEnding === rel.relationship_id}
              >
                End Relationship
              </FormButton>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RelationshipsList;