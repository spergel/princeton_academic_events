'use client';

import React, { useState } from 'react';
import { Department, META_CATEGORIES } from '@/types/events';

interface DepartmentFilterProps {
  departments: Department[];
  selectedDepartments: string[];
  onDepartmentChange: (departments: string[]) => void;
}

const DepartmentFilter: React.FC<DepartmentFilterProps> = ({
  departments,
  selectedDepartments,
  onDepartmentChange
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(META_CATEGORIES.map(cat => cat.name))
  );

  // Group departments by meta category
  const departmentsByCategory = departments.reduce((acc, dept) => {
    if (!acc[dept.meta_category]) {
      acc[dept.meta_category] = [];
    }
    acc[dept.meta_category].push(dept);
    return acc;
  }, {} as Record<string, Department[]>);

  const toggleCategory = (categoryName: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryName)) {
      newExpanded.delete(categoryName);
    } else {
      newExpanded.add(categoryName);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleDepartment = (departmentName: string) => {
    const newSelected = selectedDepartments.includes(departmentName)
      ? selectedDepartments.filter(d => d !== departmentName)
      : [...selectedDepartments, departmentName];
    onDepartmentChange(newSelected);
  };

  const toggleCategorySelection = (categoryName: string) => {
    const categoryDepartments = departmentsByCategory[categoryName] || [];
    const categoryDeptNames = categoryDepartments.map(d => d.name);
    
    const allSelected = categoryDeptNames.every(name => 
      selectedDepartments.includes(name)
    );
    
    if (allSelected) {
      // Deselect all in category
      onDepartmentChange(
        selectedDepartments.filter(name => !categoryDeptNames.includes(name))
      );
    } else {
      // Select all in category
      const newSelected = [...selectedDepartments];
      categoryDeptNames.forEach(name => {
        if (!newSelected.includes(name)) {
          newSelected.push(name);
        }
      });
      onDepartmentChange(newSelected);
    }
  };

  const selectAll = () => {
    onDepartmentChange(departments.map(d => d.name));
  };

  const selectNone = () => {
    onDepartmentChange([]);
  };

  return (
    <div className="content-block">
      <div className="content-block-header">
        Department Filter
      </div>
      <div className="content-block-body">
        <div style={{ marginBottom: '15px' }}>
          <button 
            className="button" 
            onClick={selectAll}
            style={{ marginRight: '5px', fontSize: '12px' }}
          >
            All
          </button>
          <button 
            className="button" 
            onClick={selectNone}
            style={{ fontSize: '12px' }}
          >
            None
          </button>
        </div>

        <div className="separator"></div>

        {META_CATEGORIES.map(category => {
          const categoryDepartments = departmentsByCategory[category.name] || [];
          if (categoryDepartments.length === 0) return null;

          const isExpanded = expandedCategories.has(category.name);
          const categoryDeptNames = categoryDepartments.map(d => d.name);
          const selectedInCategory = categoryDeptNames.filter(name => 
            selectedDepartments.includes(name)
          ).length;
          const allSelected = selectedInCategory === categoryDeptNames.length;

          return (
            <div key={category.name} style={{ marginBottom: '15px' }}>
              <div 
                className="section-header"
                style={{ 
                  cursor: 'pointer',
                  fontSize: '14px',
                  padding: '6px 10px',
                  marginBottom: '8px'
                }}
                onClick={() => toggleCategory(category.name)}
              >
                <span style={{ marginRight: '8px' }}>
                  {isExpanded ? '▼' : '▶'}
                </span>
                {category.display_name}
                <span style={{ float: 'right', fontSize: '12px' }}>
                  ({selectedInCategory}/{categoryDeptNames.length})
                </span>
              </div>

              {isExpanded && (
                <div>
                  <div style={{ marginBottom: '8px' }}>
                    <label style={{ cursor: 'pointer', fontSize: '12px' }}>
                      <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={() => toggleCategorySelection(category.name)}
                        style={{ marginRight: '5px' }}
                      />
                      <span style={{ fontWeight: 'bold' }}>
                        {allSelected ? 'Deselect All' : 'Select All'}
                      </span>
                    </label>
                  </div>

                  <ul className="department-filter">
                    {categoryDepartments.map(dept => (
                      <li key={dept.name} className="department-item">
                        <label>
                          <input
                            type="checkbox"
                            checked={selectedDepartments.includes(dept.name)}
                            onChange={() => toggleDepartment(dept.name)}
                          />
                          <span>{dept.name}</span>
                          <span style={{ 
                            fontSize: '11px', 
                            color: '#666666',
                            marginLeft: '5px'
                          }}>
                            ({dept.event_count})
                          </span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}

        <div className="separator"></div>

        <div style={{ fontSize: '12px', color: '#666666' }}>
          <strong>Selected:</strong> {selectedDepartments.length} departments
        </div>
      </div>
    </div>
  );
};

export default DepartmentFilter;
