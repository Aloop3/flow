import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import Modal from '../components/Modal';
import DayForm from '../components/DayForm';
import { getBlock, getWeeks, getDays, updateDay } from '../services/api';
import type { Block, Week, Day } from '../services/api';

interface BlockDetailProps {
  user: any;
  signOut: () => void;
}

const BlockDetail = ({ user, signOut }: BlockDetailProps) => {
  const { blockId } = useParams<{ blockId: string }>();
  const [block, setBlock] = useState<Block | null>(null);
  const [weeks, setWeeks] = useState<Week[]>([]);
  const [daysMap, setDaysMap] = useState<{[weekId: string]: Day[]}>({});
  const [isLoading, setIsLoading] = useState(true);
  const [activeWeek, setActiveWeek] = useState<string | null>(null);
  const [editingDay, setEditingDay] = useState<any>(null);
  

  useEffect(() => {
    const fetchBlockData = async () => {
      if (!blockId) return;
      
      setIsLoading(true);
      try {
        const blockData = await getBlock(blockId);
        console.log("Block data received:", blockData);
        setBlock(blockData);
        
        if (blockData) {
          const weeksData = await getWeeks(blockId);
          // Ensure weeksData is an array even if API returns undefined
          const safeWeeksData = Array.isArray(weeksData) ? weeksData : [];
          console.log("Weeks data received:", safeWeeksData);
          setWeeks(safeWeeksData);
          
          if (safeWeeksData.length > 0) {
            setActiveWeek(safeWeeksData[0].week_id);
            
            // Fetch days for all weeks
            const daysObj: {[weekId: string]: Day[]} = {};
            for (const week of safeWeeksData) {
              const daysData = await getDays(week.week_id);
              // Ensure daysData is an array
              const safeDaysData = Array.isArray(daysData) ? daysData : [];
              daysObj[week.week_id] = safeDaysData;
            }
            setDaysMap(daysObj);
          }
        }
      } catch (error) {
        console.error('Error fetching block data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchBlockData();
  }, [blockId]);

  const handleUpdateDay = async (dayData: any) => {
    try {
      // Call the updateDay API function
      await updateDay(dayData.day_id, {
        focus: dayData.focus,
        notes: dayData.notes
      });
      
      // Refresh the days data for the current week
      if (activeWeek) {
        const daysData = await getDays(activeWeek);
        setDaysMap(prev => ({
          ...prev,
          [activeWeek]: daysData
        }));
      }
      
      setEditingDay(null);
    } catch (error) {
      console.error('Error updating day:', error);
    }
  };
  
  return (
    <Layout user={user} signOut={signOut}>
      <div className="space-y-6">
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-gray-200 rounded w-1/4"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-40 bg-gray-200 rounded"></div>
          </div>
        ) : block ? (
          <>
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">{block.title}</h1>
              <Link
                to={`/blocks/${blockId}/edit`}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Edit Program
              </Link>
            </div>
            
            <div className="bg-white shadow rounded-lg p-6">
              <p className="mb-4 text-gray-600">{block.description}</p>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Start Date</h3>
                  <p className="mt-1 text-sm text-gray-900">{new Date(block.start_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">End Date</h3>
                  <p className="mt-1 text-sm text-gray-900">{new Date(block.end_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Status</h3>
                  <p className="mt-1 text-sm">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      block.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : block.status === 'completed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {block.status.charAt(0).toUpperCase() + block.status.slice(1)}
                    </span>
                  </p>
                </div>
              </div>
            </div>
            
            {/* Weeks and Days section */}
            {weeks && weeks.length > 0 ? (
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="border-b border-gray-200">
                  <nav className="flex">
                    {weeks.map((week) => (
                      <button
                        key={week.week_id}
                        onClick={() => setActiveWeek(week.week_id)}
                        className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                          activeWeek === week.week_id
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        Week {week.week_number}
                      </button>
                    ))}
                  </nav>
                </div>
                
                {activeWeek && daysMap[activeWeek] && (
                  <div className="p-6">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                      {daysMap[activeWeek].map((day) => (
                        <div key={day.day_id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <h3 className="text-lg font-medium text-gray-900">Day {day.day_number}</h3>
                        <p className="text-sm text-gray-500">{new Date(day.date).toLocaleDateString()}</p>
                        {day.focus && <p className="mt-2 text-sm font-medium text-gray-700">Focus: {day.focus}</p>}
                        {day.notes && <p className="mt-1 text-sm text-gray-500">{day.notes}</p>}
                        <div className="mt-4 flex justify-between">
                          <button
                            onClick={() => setEditingDay(day)}
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            Edit Details
                          </button>
                          <button
                            className="px-3 py-2 text-sm text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50"
                          >
                            View Exercises
                          </button>
                        </div>
                      </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white shadow rounded-lg p-6 text-center">
                <p className="text-gray-500 mb-4">The program structure should have been created automatically.</p>
                <p className="text-gray-500">If you don't see any weeks, please refresh the page or contact support.</p>
              </div>
            )}
          </>
        ) : (
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <p className="text-gray-500">Block not found or failed to load.</p>
            <p className="text-sm text-gray-400 mt-2">Block ID: {blockId}</p>
            <button 
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        )}
      </div>
      
      {/* Modals */}
      <Modal 
        isOpen={!!editingDay} 
        onClose={() => setEditingDay(null)}
        title="Edit Day"
      >
        {editingDay && (
          <DayForm 
            day={editingDay}
            onSubmit={handleUpdateDay} 
            isLoading={false}
            onCancel={() => setEditingDay(null)}
          />
        )}
      </Modal>
    </Layout>
  );
};

export default BlockDetail;