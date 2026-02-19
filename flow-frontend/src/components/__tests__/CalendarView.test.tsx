import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/jest-globals';
import CalendarView from '../CalendarView';
import type { Day } from '../../services/api';

const day1: Day = { day_id: 'd1', week_id: 'w1', day_number: 1, date: '2026-02-10', focus: 'Squat' };
const day2: Day = { day_id: 'd2', week_id: 'w1', day_number: 2, date: '2026-02-17', focus: null };
const day3: Day = { day_id: 'd3', week_id: 'w1', day_number: 3, date: '2026-03-03', focus: 'Bench' };
const daysMap = { w1: [day1, day2, day3] };
const mockOnDayClick = jest.fn();

beforeEach(() => { jest.clearAllMocks(); });

describe('CalendarView month header', () => {
  test('shows first month of block by default', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    expect(screen.getByText('February 2026')).toBeInTheDocument();
  });
});

describe('CalendarView day cells', () => {
  test('renders a dot for each block day', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    expect(screen.getByLabelText(/Day 1:.*2026-02-10/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Day 2:.*2026-02-17/)).toBeInTheDocument();
  });

  test('non-block days have no aria-label', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    expect(screen.queryByLabelText(/2026-02-11/)).not.toBeInTheDocument();
  });
});

describe('CalendarView popup', () => {
  test('clicking a block day opens popup with date and focus', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText(/Day 1:.*2026-02-10/));
    expect(screen.getByText(/Squat/)).toBeInTheDocument();
    expect(screen.getByText('Open Workout')).toBeInTheDocument();
  });

  test('clicking Open Workout calls onDayClick with correct day', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText(/Day 1:.*2026-02-10/));
    fireEvent.click(screen.getByText('Open Workout'));
    expect(mockOnDayClick).toHaveBeenCalledWith(day1);
  });

  test('popup closes when clicking Cancel', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText(/Day 1:.*2026-02-10/));
    expect(screen.getByText('Open Workout')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Cancel'));
    expect(screen.queryByText('Open Workout')).not.toBeInTheDocument();
  });

  test('popup omits focus line when day has no focus', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText(/Day 2:.*2026-02-17/));
    expect(screen.queryByText(/Focus:/)).not.toBeInTheDocument();
  });

  test('popup closes when clicking backdrop', () => {
    const { container } = render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText(/Day 1:.*2026-02-10/));
    expect(screen.getByText('Open Workout')).toBeInTheDocument();
    // Click the fixed overlay (backdrop)
    const backdrop = container.querySelector('.fixed.inset-0');
    fireEvent.click(backdrop!);
    expect(screen.queryByText('Open Workout')).not.toBeInTheDocument();
  });
});

describe('CalendarView month navigation', () => {
  test('prev arrow is disabled on first month', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    expect(screen.getByLabelText('Previous month')).toBeDisabled();
  });

  test('next arrow navigates to second month', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText('Next month'));
    expect(screen.getByText('March 2026')).toBeInTheDocument();
  });

  test('next arrow is disabled on last month', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText('Next month'));
    expect(screen.getByLabelText('Next month')).toBeDisabled();
  });

  test('prev arrow navigates back to first month', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} />);
    fireEvent.click(screen.getByLabelText('Next month'));
    fireEvent.click(screen.getByLabelText('Previous month'));
    expect(screen.getByText('February 2026')).toBeInTheDocument();
  });
});

describe('CalendarView excludeDayId', () => {
  test('excluded day has no dot and is not clickable', () => {
    render(<CalendarView daysMap={daysMap} onDayClick={mockOnDayClick} excludeDayId="d1" />);
    expect(screen.queryByLabelText(/Day 1:.*2026-02-10/)).not.toBeInTheDocument();
  });
});

describe('CalendarView empty state', () => {
  test('shows empty message when daysMap is empty', () => {
    render(<CalendarView daysMap={{}} onDayClick={mockOnDayClick} />);
    expect(screen.getByText('No days scheduled.')).toBeInTheDocument();
  });
});
