"use client";
import { useState, useEffect } from "react";
import { FiChevronDown, FiCheck } from "react-icons/fi";

export default function Filter({
  // Dropdown props
  showDropdown = true,
  dropdownOptions = [],
  selectedOption = null,
  onOptionChange = () => {},
  dropdownLabel = "Filter",

  // Date props
  showDateFilter = false,
  startDate: initialStartDate = "",
  endDate: initialEndDate = "",
  minDate = "",
  maxDate = "",
  onDateChange = () => {},

  // Styling
  className = "",
}) {
  // Dropdown state
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Date state (local until applied)
  const [localStartDate, setLocalStartDate] = useState(initialStartDate);
  const [localEndDate, setLocalEndDate] = useState(initialEndDate);
  const [hasDateChanges, setHasDateChanges] = useState(false);

  // Sync local dates when props change
  useEffect(() => {
    setLocalStartDate(initialStartDate);
    setLocalEndDate(initialEndDate);
    setHasDateChanges(false);
  }, [initialStartDate, initialEndDate]);

  // Check if dates have changed from initial
  const checkDateChanges = (start, end) => {
    const changed = start !== initialStartDate || end !== initialEndDate;
    setHasDateChanges(changed);
  };

  const handleStartDateChange = (e) => {
    const newDate = e.target.value;
    if (minDate && newDate < minDate) return;
    setLocalStartDate(newDate);
    checkDateChanges(newDate, localEndDate);
  };

  const handleEndDateChange = (e) => {
    const newDate = e.target.value;
    if (maxDate && newDate > maxDate) return;
    setLocalEndDate(newDate);
    checkDateChanges(localStartDate, newDate);
  };

  const handleApplyDates = () => {
    onDateChange({
      startDate: localStartDate,
      endDate: localEndDate,
    });
    setHasDateChanges(false);
  };

  const handleOptionSelect = (option) => {
    onOptionChange(option);
    setDropdownOpen(false);
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* DATE FILTER */}
      {showDateFilter && (
        <div className="flex items-center gap-2">
          {/* Start Date */}
          <input
            type="date"
            value={localStartDate}
            min={minDate}
            max={localEndDate || maxDate}
            onChange={handleStartDateChange}
            className="border border-gray-300 px-2 py-1.5 rounded-lg text-sm text-gray-700 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <span className="text-gray-400 text-sm">to</span>

          {/* End Date */}
          <input
            type="date"
            value={localEndDate}
            min={localStartDate || minDate}
            max={maxDate}
            onChange={handleEndDateChange}
            className="border border-gray-300 px-2 py-1.5 rounded-lg text-sm text-gray-700 
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          {/* Apply Button - only show when dates changed */}
          {hasDateChanges && (
            <button
              onClick={handleApplyDates}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium 
                         text-white bg-blue-500 rounded-lg hover:bg-blue-600 
                         transition-all duration-200 shadow-sm"
            >
              <FiCheck className="w-4 h-4" />
              Apply
            </button>
          )}
        </div>
      )}

      {/* DROPDOWN FILTER */}
      {showDropdown && dropdownOptions.length > 0 && (
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium 
                       text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 
                       transition-all duration-200"
          >
            {selectedOption || dropdownLabel}
            <FiChevronDown
              className={`text-gray-500 transition-transform duration-200 
                          ${dropdownOpen ? "rotate-180" : ""}`}
            />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <>
              {/* Backdrop to close dropdown */}
              <div
                className="fixed inset-0 z-20"
                onClick={() => setDropdownOpen(false)}
              />

              <div
                className="absolute right-0 mt-2 z-30 bg-white shadow-lg border 
                           rounded-xl py-2 min-w-[160px] max-h-[240px] overflow-y-auto"
              >
                {dropdownOptions.map((option) => (
                  <button
                    key={option.value ?? option}
                    onClick={() =>
                      handleOptionSelect(option.label ?? option)
                    }
                    className={`w-full text-left px-4 py-2 text-sm transition-all duration-150
                                hover:bg-gray-100
                                ${
                                  (option.label ?? option) === selectedOption
                                    ? "bg-blue-50 text-blue-600 font-medium"
                                    : "text-gray-700"
                                }`}
                  >
                    {option.label ?? option}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
