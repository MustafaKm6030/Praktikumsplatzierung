import React from 'react';
import TextField from '../ui/TextField';
import Select from '../ui/Select';

export default function StudentsToolbar({
  searchTerm,
  onSearchChange,
  programFilter,
  onProgramChange,
  regionFilter,
  onRegionChange,
  regionOptions,
}) {
  return (
    <div className="filters-wrap">
      <div className="filters-row">
        <div className="filters-search">
          <TextField
            placeholder="Search by Student Name, ID, or Email..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        <Select
          value={programFilter}
          onChange={(e) => onProgramChange(e.target.value)}
          className="filters-select"
        >
          <option value="">All Programs</option>
          <option value="GS">Grundschule (GS)</option>
          <option value="MS">Mittelschule (MS)</option>
        </Select>

        <Select
          value={regionFilter}
          onChange={(e) => onRegionChange(e.target.value)}
          className="filters-select"
        >
          <option value="">All Regions</option>
          {regionOptions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </Select>
      </div>
    </div>
  );
}
