// Ensures consistent date handling across the application
export const parseDate = (dateString: string): Date => {
    // Force interpretation as UTC by appending time and Z suffix
    // This preserves the exact date regardless of user's timezone
    return new Date(`${dateString}T00:00:00Z`);
  };
  
  // Format a date string or Date object for display
  export const formatDate = (date: string | Date, options?: Intl.DateTimeFormatOptions): string => {
    const dateObj = typeof date === 'string' ? parseDate(date) : date;
    return dateObj.toLocaleDateString(undefined, {
      timeZone: 'UTC', // Important: display in UTC time
      ...options
    });
  };