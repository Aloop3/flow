import { useState } from 'react';
import Layout from '../components/Layout';
import CoachInviteSection from '../components/CoachInviteSection';
import AthleteAcceptSection from '../components/AthleteAcceptSection';
import RelationshipsList from '../components/RelationshipsList';
import { useWeightUnit } from '../contexts/UserContext';
import { updateUser } from '../services/api';


interface ProfileProps {
  user: any;
  signOut: () => void;
}

const Profile = ({ user, signOut }: ProfileProps) => {
  const [activeTab, setActiveTab] = useState('info');
  const [refreshKey, setRefreshKey] = useState(0);
  const { weightPreference, updateWeightPreference } = useWeightUnit();
  const [isUpdatingPreference, setIsUpdatingPreference] = useState(false);

  const handleWeightPreferenceChange = async (newPreference: 'auto' | 'kg' | 'lb') => {
    setIsUpdatingPreference(true);
    try {
      await updateUser(user.user_id, { weight_unit_preference: newPreference });
      updateWeightPreference(newPreference);
    } catch (error) {
      console.error('Error updating weight preference:', error);
    } finally {
      setIsUpdatingPreference(false);
    }
  };
  
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('info')}
              className={`${
                activeTab === 'info'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              User Information
            </button>
            <button
              onClick={() => setActiveTab('connections')}
              className={`${
                activeTab === 'connections'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Connections
            </button>
          </nav>
        </div>
        
        {/* Tab Content */}
        {activeTab === 'info' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">User Information</h2>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{user.email || 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{user.name || user.username || 'N/A'}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Role</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">{user.role || 'N/A'}</dd>
              </div>
            </dl>
          </div>
        )}
        
        {activeTab === 'connections' && (
          <div className="space-y-6">
            {/* Show different sections based on user role */}
            {user.role === 'coach' && (
              <CoachInviteSection user={user} onGenerateCode={handleRefresh} />
            )}
            
            {user.role === 'athlete' && (
              <AthleteAcceptSection user={user} onAcceptCode={handleRefresh} />
            )}
            
            {/* Show relationships for both roles */}
            <RelationshipsList key={refreshKey} user={user} onRelationshipChange={handleRefresh} />
          </div>
        )}

        <div>
          <dt className="text-sm font-medium text-gray-500">Weight Units</dt>
          <dd className="mt-1">
            <select
              value={weightPreference}
              onChange={(e) => handleWeightPreferenceChange(e.target.value as 'auto' | 'kg' | 'lb')}
              disabled={isUpdatingPreference}
              className="text-sm border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="auto">Smart defaults (SBD→kg)</option>
              <option value="kg">kg</option>
              <option value="lb">lb</option>
            </select>
          </dd>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;