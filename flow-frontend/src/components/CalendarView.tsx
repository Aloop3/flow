import { useState, useMemo } from 'react';
import type { Day } from '../services/api';
import FocusTag from './FocusTag';
import { parseFocusTags } from '../constants/focusOptions';

interface CalendarViewProps {
  daysMap: { [weekId: string]: Day[] };
  onDayClick: (day: Day) => void;
  excludeDayId?: string;
}

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTH_NAMES = ['January','February','March','April','May','June',
  'July','August','September','October','November','December'];

const CalendarView = ({ daysMap, onDayClick, excludeDayId }: CalendarViewProps) => {
  const [monthIndex, setMonthIndex] = useState(0);
  const [selectedDay, setSelectedDay] = useState<Day | null>(null);

  // Build date → Day lookup, excluding the excluded day
  const dateLookup = useMemo(() => {
    const lookup: { [date: string]: Day } = {};
    Object.values(daysMap).forEach(days =>
      days.forEach(day => {
        if (day.date && day.day_id !== excludeDayId) lookup[day.date] = day;
      })
    );
    return lookup;
  }, [daysMap, excludeDayId]);

  // Derive month list from the dates present in daysMap
  const months = useMemo(() => {
    const allDates = Object.keys(dateLookup).sort();
    if (allDates.length === 0) return [];
    const start = new Date(`${allDates[0]}T00:00:00Z`);
    const end = new Date(`${allDates[allDates.length - 1]}T00:00:00Z`);
    const result: { year: number; month: number }[] = [];
    const curr = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), 1));
    while (curr <= end) {
      result.push({ year: curr.getUTCFullYear(), month: curr.getUTCMonth() });
      curr.setUTCMonth(curr.getUTCMonth() + 1);
    }
    return result;
  }, [dateLookup]);

  // C1: clamp monthIndex so it never exceeds available months
  const safeMonthIndex = Math.min(monthIndex, Math.max(0, months.length - 1));

  if (months.length === 0) return <p className="text-sm text-gray-500 p-4">No days scheduled.</p>;

  const { year, month } = months[safeMonthIndex];

  // M3: memoize cell building
  const cells = useMemo(() => buildCells(year, month), [year, month]);

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setMonthIndex(i => i - 1)}
          disabled={monthIndex === 0}
          className="p-2 rounded disabled:opacity-30 hover:bg-ocean-mist"
          aria-label="Previous month"
        >‹</button>
        <span className="font-semibold">{MONTH_NAMES[month]} {year}</span>
        <button
          onClick={() => setMonthIndex(i => i + 1)}
          disabled={monthIndex === months.length - 1}
          className="p-2 rounded disabled:opacity-30 hover:bg-ocean-mist"
          aria-label="Next month"
        >›</button>
      </div>

      <div className="grid grid-cols-7 gap-1 mb-1">
        {DAYS_OF_WEEK.map(d => (
          <div key={d} className="text-center text-xs font-medium text-gray-500 py-1">{d}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {/* I1: render <button> for block days, <div> for non-block days */}
        {cells.map((dayNum, i) => {
          if (!dayNum) return <div key={`empty-${i}`} />;
          const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`;
          const blockDay = dateLookup[dateStr];
          if (blockDay) {
            return (
              <button
                key={dateStr}
                onClick={() => setSelectedDay(blockDay)}
                className="flex flex-col items-center justify-center rounded-md p-1 min-h-[44px] text-sm hover:bg-ocean-mist cursor-pointer"
                aria-label={`Day ${blockDay.day_number}: ${dateStr}`}
              >
                <span>{dayNum}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-ocean-teal mt-0.5" />
              </button>
            );
          }
          return (
            <div
              key={dateStr}
              className="flex flex-col items-center justify-center rounded-md p-1 min-h-[44px] text-sm opacity-50"
            >
              <span>{dayNum}</span>
            </div>
          );
        })}
      </div>

      {/* I2: modal with role="dialog", aria-modal, aria-labelledby, Escape handler */}
      {selectedDay && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/20"
          onClick={() => setSelectedDay(null)}
          onKeyDown={(e) => e.key === 'Escape' && setSelectedDay(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="day-popup-title"
            className="bg-white rounded-lg shadow-lg p-5 max-w-xs w-full mx-4"
            onClick={e => e.stopPropagation()}
          >
            <p id="day-popup-title" className="font-semibold text-gray-900">
              {new Date(`${selectedDay.date}T00:00:00Z`).toLocaleDateString(undefined, {
                timeZone: 'UTC', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
              })}
            </p>
            {selectedDay.focus && (
              <div className="flex flex-wrap gap-1 mt-2">
                {parseFocusTags(selectedDay.focus).map(tag => (
                  <FocusTag key={tag} focus={tag} size="sm" />
                ))}
              </div>
            )}
            <button
              autoFocus
              className="mt-4 w-full bg-ocean-teal text-white rounded-md py-2 text-sm font-medium hover:bg-ocean-navy"
              onClick={() => { onDayClick(selectedDay); setSelectedDay(null); }}
            >
              Open Workout
            </button>
            <button
              className="mt-2 w-full text-sm text-gray-500 hover:text-gray-700"
              onClick={() => setSelectedDay(null)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

function buildCells(year: number, month: number): (number | null)[] {
  const firstDayOfWeek = new Date(Date.UTC(year, month, 1)).getUTCDay();
  const daysInMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  const cells: (number | null)[] = Array(firstDayOfWeek).fill(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  return cells;
}

export default CalendarView;
