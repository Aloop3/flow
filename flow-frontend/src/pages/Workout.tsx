import Layout from '../components/Layout';

interface WorkoutProps {
  user: any;
  signOut: () => void;
}

const Workout = ({ user, signOut }: WorkoutProps) => {
  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Workout</h1>
        <p className="text-gray-500">Workout details will appear here</p>
      </div>
    </Layout>
  );
};

export default Workout;