import React, { useState, useEffect } from 'react';
import { getNotifications, markNotificationAsRead } from '../services/api';
import type { Notification } from '../services/api';
import WorkoutCompletion from './WorkoutCompletion';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

interface NotificationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const NotificationModal: React.FC<NotificationModalProps> = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [groupBy, setGroupBy] = useState<'date' | 'athlete'>('date');

  const fetchNotifications = async () => {
    try {
      setIsLoading(true);
      const notificationData = await getNotifications();
      setNotifications(notificationData);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  const handleMarkAsRead = async (notification: Notification) => {
    if (notification.is_read) return;

    try {
      await markNotificationAsRead(notification.notification_id);
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => 
          n.notification_id === notification.notification_id 
            ? { ...n, is_read: true }
            : n
        )
      );

      // Refresh the notification badge count
      if ((window as any).notificationBadgeRefresh) {
        (window as any).notificationBadgeRefresh();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleNotificationClick = async (notification: Notification) => {
    await handleMarkAsRead(notification);
    setSelectedNotification(notification);
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      if (date.toDateString() === today.toDateString()) {
        return 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString();
      }
    } catch {
      return 'Unknown date';
    }
  };

  const formatTime = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return 'Unknown time';
    }
  };

  const groupNotifications = () => {
    if (groupBy === 'date') {
      const grouped = notifications.reduce((acc, notification) => {
        const date = formatDate(notification.created_at);
        if (!acc[date]) acc[date] = [];
        acc[date].push(notification);
        return acc;
      }, {} as Record<string, Notification[]>);

      // Sort by date (newest first)
      return Object.entries(grouped).sort(([a], [b]) => {
        if (a === 'Today') return -1;
        if (b === 'Today') return 1;
        if (a === 'Yesterday') return -1;
        if (b === 'Yesterday') return 1;
        return new Date(b).getTime() - new Date(a).getTime();
      });
    } else {
      const grouped = notifications.reduce((acc, notification) => {
        const athlete = notification.athlete_name;
        if (!acc[athlete]) acc[athlete] = [];
        acc[athlete].push(notification);
        return acc;
      }, {} as Record<string, Notification[]>);

      return Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b));
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl h-[90vh] flex flex-col p-0">
        {/* Header */}
        <DialogHeader className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <DialogTitle>Athlete Notifications</DialogTitle>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setGroupBy('date')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  groupBy === 'date'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                By Date
              </button>
              <button
                onClick={() => setGroupBy('athlete')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  groupBy === 'athlete'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                By Athlete
              </button>
            </div>
          </div>
        </DialogHeader>

        <div className="flex flex-1 overflow-hidden">
          {/* Notification List */}
          <ScrollArea className="w-1/2 border-r border-gray-200">
            {isLoading ? (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center p-8 text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                No notifications yet
              </div>
            ) : (
              <div className="p-4 space-y-6">
                {groupNotifications().map(([groupName, groupNotifications]) => (
                  <div key={groupName}>
                    <h3 className="text-sm font-medium text-gray-500 mb-3">{groupName}</h3>
                    <div className="space-y-2">
                      {groupNotifications.map((notification) => (
                        <button
                          key={notification.notification_id}
                          onClick={() => handleNotificationClick(notification)}
                          className={`w-full text-left p-3 rounded-lg border transition-all ${
                            selectedNotification?.notification_id === notification.notification_id
                              ? 'border-blue-300 bg-blue-50'
                              : notification.is_read
                              ? 'border-gray-200 bg-white hover:bg-gray-50'
                              : 'border-blue-200 bg-blue-25 hover:bg-blue-50'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <span className={`font-medium ${
                                  notification.is_read ? 'text-gray-700' : 'text-gray-900'
                                }`}>
                                  {notification.athlete_name}
                                </span>
                                {!notification.is_read && (
                                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                                )}
                              </div>
                              <p className={`text-sm mt-1 ${
                                notification.is_read ? 'text-gray-500' : 'text-gray-700'
                              }`}>
                                Completed {notification.day_info}
                              </p>
                            </div>
                            <span className="text-xs text-gray-400 ml-2">
                              {formatTime(notification.created_at)}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>

          {/* Workout Detail Panel */}
          <ScrollArea className="w-1/2">
            {selectedNotification ? (
              <div className="p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {selectedNotification.athlete_name}'s Workout
                  </h3>
                  <p className="text-sm text-gray-600 mb-1">
                    Completed at {formatTime(selectedNotification.created_at)} on{' '}
                    {formatDate(selectedNotification.created_at)}
                  </p>
                  <p className="text-sm text-gray-500">
                    Completed {selectedNotification.day_info}
                  </p>
                </div>

                {/* Use WorkoutCompletion component to display workout details */}
                <WorkoutCompletion
                  workout={selectedNotification.workout_data}
                  onClose={undefined} // Don't show close button in modal context
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p>Select a notification to view workout details</p>
                </div>
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {notifications.length > 0 && (
                <>
                  {notifications.filter(n => !n.is_read).length} unread of {notifications.length} total
                </>
              )}
            </div>
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default NotificationModal;