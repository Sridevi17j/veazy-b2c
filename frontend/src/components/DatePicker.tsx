'use client';

import { useState, useEffect } from 'react';
import DatePicker from 'react-date-picker';
import 'react-date-picker/dist/DatePicker.css';
import 'react-calendar/dist/Calendar.css';

type ValuePiece = Date | null;
type Value = ValuePiece | [ValuePiece, ValuePiece];

interface CustomDatePickerProps {
  /** The selected date */
  selected?: Date;
  /** Callback when date is selected */
  onSelect?: (date: Date | undefined) => void;
  /** Callback when date is selected and calendar has closed */
  onDateSelectedAndClosed?: () => void;
  /** Input placeholder text */
  placeholder?: string;
  /** Label for the input field */
  label?: string;
  /** Minimum selectable date */
  fromDate?: Date;
  /** Maximum selectable date */
  toDate?: Date;
  /** Additional CSS classes for the input */
  className?: string;
  /** Disable the input */
  disabled?: boolean;
  /** Error state */
  error?: boolean;
  /** Error message */
  errorMessage?: string;
  /** Control to open calendar programmatically */
  shouldOpen?: boolean;
  /** Callback when calendar opens */
  onCalendarOpened?: () => void;
}

export default function CustomDatePicker({
  selected,
  onSelect,
  onDateSelectedAndClosed,
  placeholder = 'Select date',
  label,
  fromDate,
  toDate,
  className = '',
  disabled = false,
  error = false,
  errorMessage,
  shouldOpen = false,
  onCalendarOpened
}: CustomDatePickerProps) {
  const [value, setValue] = useState<Value>(selected || null);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  // Update internal value when selected prop changes
  useEffect(() => {
    setValue(selected || null);
  }, [selected]);

  // Handle programmatic open
  useEffect(() => {
    if (shouldOpen && !isCalendarOpen) {
      setIsCalendarOpen(true);
      setIsClosing(false);
    }
  }, [shouldOpen]);

  const handleDateChange = (date: Value) => {
    // Immediately update internal state for instant visual feedback
    setValue(date);

    // Start closing process
    setIsClosing(true);

    // Show the selection change for a brief moment, then close
    setTimeout(() => {
      setIsCalendarOpen(false);
      setIsClosing(false);
      // Call the callback after calendar is closed
      onDateSelectedAndClosed?.();
    }, 400); // 400ms delay to see the selection change

    // Convert Value type to Date | undefined for our callback
    if (Array.isArray(date)) {
      onSelect?.(date[0] || undefined);
    } else {
      onSelect?.(date || undefined);
    }
  };

  const handleCalendarOpen = () => {
    setIsCalendarOpen(true);
    setIsClosing(false);
    onCalendarOpened?.();
  };

  const handleCalendarClose = () => {
    if (!isClosing) {
      setIsCalendarOpen(false);
    }
  };

  const shouldCloseCalendar = ({ reason }: { reason: string }) => {
    // Don't close immediately on date selection
    if (reason === 'select') {
      return false;
    }
    return !isClosing;
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-xs text-gray-600 mb-1 font-medium">
          {label}
        </label>
      )}
      
      <div className="relative">
        <DatePicker
          value={value}
          onChange={handleDateChange}
          disabled={disabled}
          minDate={fromDate}
          maxDate={toDate}
          isOpen={isCalendarOpen}
          onCalendarOpen={handleCalendarOpen}
          onCalendarClose={handleCalendarClose}
          shouldCloseCalendar={shouldCloseCalendar}
          clearIcon={null}
          calendarIcon={
            <svg 
              className="w-4 h-4 text-gray-500" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" 
              />
            </svg>
          }
          className={`
            react-date-picker w-full
            ${error ? 'border-red-300' : 'border-gray-300'}
            ${disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
          `}
          dayPlaceholder="dd"
          monthPlaceholder="mm"
          yearPlaceholder="yyyy"
        />
      </div>

      {/* Error message */}
      {error && errorMessage && (
        <p className="mt-1 text-xs text-red-600" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}