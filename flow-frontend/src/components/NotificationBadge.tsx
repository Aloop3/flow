import React, { useState, useEffect } from 'react';
import { getNotifications } from '../services/api';

interface NotificationBadgeProps {
  onClick: () => void;
}

const NotificationBadge: React.FC<NotificationBadgeProps> = ({ onClick }) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const fetchNotificationCount = async () => {
    try {
      setIsLoading(true);
      const notifications = await getNotifications();
      const unreadNotifications = notifications.filter(n => !n.is_read);
      setUnreadCount(unreadNotifications.length);
    } catch (error) {
      console.error('Error fetching notification count:', error);
      // Don't show error to user, just silently fail for badge
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchNotificationCount();
  }, []);

  // Set up 30-second polling
  useEffect(() => {
    const interval = setInterval(fetchNotificationCount, 30000); // 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Provide a way for parent components to manually refresh
  const refreshCount = () => {
    fetchNotificationCount();
  };

  // Expose refresh function via a custom method that can be called by parent
  React.useEffect(() => {
    // Type assertion to avoid TypeScript errors
    (window as any).notificationBadgeRefresh = refreshCount;
    return () => {
      delete (window as any).notificationBadgeRefresh;
    };
  }, []);

  return (
    <button
      onClick={onClick}
      className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md"
      aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ''}`}
    >
      {/* Bell icon */}
      <svg 
        className="w-6 h-6" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" 
        />
      </svg>
      
      {/* Badge with unread count */}
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
      
      {/* Loading indicator */}
      {isLoading && (
        <span className="absolute -top-1 -right-1 bg-blue-500 rounded-full h-3 w-3 animate-pulse" />
      )}
    </button>
  );
};

export default NotificationBadge;