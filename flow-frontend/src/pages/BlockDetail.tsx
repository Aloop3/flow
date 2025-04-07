import Layout from '../components/Layout';

interface BlockDetailProps {
  user: any;
  signOut: () => void;
}

const BlockDetail = ({ user, signOut }: BlockDetailProps) => {
  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Training Block Details</h1>
        <p className="text-gray-500">Block details will appear here</p>
      </div>
    </Layout>
  );
};

export default BlockDetail;