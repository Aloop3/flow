import React from 'react';

// Simple exercise selector skeleton
export const ExerciseSelectorSkeleton: React.FC = () => (
  <div className="space-y-4">
    <div className="h-10 bg-gray-200 rounded animate-pulse"></div>
    <div className="flex space-x-2">
      <div className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
      <div className="h-8 w-20 bg-gray-200 rounded animate-pulse"></div>
      <div className="h-8 w-16 bg-gray-200 rounded animate-pulse"></div>
    </div>
    <div className="h-40 bg-gray-200 rounded animate-pulse"></div>
  </div>
);

// Day detail skeleton
export const WorkoutDetailSkeleton: React.FC = () => (
  <div className="space-y-6">
    <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
    <div className="h-6 bg-gray-200 rounded animate-pulse w-1/2"></div>
    <div className="space-y-4">
      <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
      <div className="h-32 bg-gray-200 rounded animate-pulse"></div>
    </div>
  </div>
);

// Analytics skeleton (matches your existing Analytics component)
export const AnalyticsSkeleton: React.FC = () => (
  <div className="animate-pulse space-y-6">
    <div className="h-8 bg-gray-200 rounded w-1/3"></div>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="h-64 bg-gray-200 rounded-lg"></div>
      <div className="h-64 bg-gray-200 rounded-lg"></div>
      <div className="h-64 bg-gray-200 rounded-lg"></div>
      <div className="h-64 bg-gray-200 rounded-lg"></div>
    </div>
  </div>
);

// Block detail skeleton (matches your existing BlockDetail component)
export const BlockDetailSkeleton: React.FC = () => (
  <div className="space-y-6">
    {/* Block Header Skeleton */}
    <div className="flex justify-between items-center">
      <div className="h-8 bg-gray-200 rounded w-64 animate-pulse"></div>
      <div className="h-9 bg-gray-200 rounded w-24 animate-pulse"></div>
    </div>
    
    {/* Horizontal Block Info Card Skeleton */}
    <div className="bg-white shadow rounded-lg p-4">
      <div className="mb-3">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-1 animate-pulse"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-20 animate-pulse"></div>
        </div>
        <div className="h-5 bg-gray-200 rounded w-12 animate-pulse"></div>
      </div>
    </div>
    
    {/* Week Tabs Skeleton */}
    <div className="bg-white shadow rounded-lg overflow-visible">
      <div className="border-b border-gray-200">
        <nav className="flex">
          <div className="py-4 px-6">
            <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          </div>
          <div className="py-4 px-6">
            <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          </div>
          <div className="py-4 px-6">
            <div className="h-4 bg-gray-200 rounded w-16 animate-pulse"></div>
          </div>
        </nav>
      </div>
      
      {/* Days Table Skeleton */}
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <div className="h-6 bg-gray-200 rounded w-20 mb-2 animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-40 animate-pulse"></div>
          </div>
          <div className="h-9 bg-gray-200 rounded w-32 animate-pulse"></div>
        </div>
        
        <div className="overflow-visible border border-gray-200 rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-gray-600">Day</th>
                <th className="px-3 py-2 text-left font-medium text-gray-600">Date</th>
                <th className="px-3 py-2 text-left font-medium text-gray-600">Focus</th>
                <th className="px-3 py-2 text-center font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              <tr className="animate-pulse">
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-12"></div></td>
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-20"></div></td>
                <td className="px-3 py-2"><div className="h-5 bg-gray-200 rounded w-16"></div></td>
                <td className="px-3 py-2"><div className="flex justify-center"><div className="h-6 bg-gray-200 rounded w-16"></div></div></td>
              </tr>
              <tr className="animate-pulse">
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-12"></div></td>
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-20"></div></td>
                <td className="px-3 py-2"><div className="h-5 bg-gray-200 rounded w-16"></div></td>
                <td className="px-3 py-2"><div className="flex justify-center"><div className="h-6 bg-gray-200 rounded w-16"></div></div></td>
              </tr>
              <tr className="animate-pulse">
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-12"></div></td>
                <td className="px-3 py-2"><div className="h-4 bg-gray-200 rounded w-20"></div></td>
                <td className="px-3 py-2"><div className="h-5 bg-gray-200 rounded w-16"></div></td>
                <td className="px-3 py-2"><div className="flex justify-center"><div className="h-6 bg-gray-200 rounded w-16"></div></div></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
);