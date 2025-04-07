import Layout from '../components/Layout';

interface ProfileProps {
  user: any;
  signOut: () => void;
}

const Profile = ({ user, signOut }: ProfileProps) => {
  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">User Information</h2>
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{user.attributes?.email || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{user.attributes?.name || user.username || 'N/A'}</dd>
            </div>
          </dl>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;