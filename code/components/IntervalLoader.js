import React from 'react';

export default function IntervalLoader(props) {
    const { id, data = [], setProps } = props; // `data` holds the intervals passed from Dash

    let startTime = '';
    let endTime = '';

    function handleStartTimeChange(event) {
        startTime = event.target.value;
    }

    function handleEndTimeChange(event) {
        endTime = event.target.value;
    }

    function handleAddInterval() {
        if (!startTime || !endTime || isNaN(startTime) || isNaN(endTime)) return;
        const newInterval = { start: parseFloat(startTime), end: parseFloat(endTime) };
        const updatedIntervals = [...data, newInterval];
        setProps({ data: updatedIntervals }); // Update intervals in Dash
        startTime = '';
        endTime = '';
    }

    return React.createElement('div', { style: { width: '100%' } }, [
        React.createElement('div', { style: { display: 'flex', alignItems: 'center', marginBottom: '10px' } }, [
            React.createElement('input', {
                type: 'number',
                placeholder: 'Start time (s)',
                onChange: handleStartTimeChange,
                style: { padding: '10px', marginRight: '10px', borderRadius: '5px', border: '1px solid #ccc', width: 'calc(50% - 20px)' }
            }),
            React.createElement('input', {
                type: 'number',
                placeholder: 'End time (s)',
                onChange: handleEndTimeChange,
                style: { padding: '10px', marginRight: '10px', borderRadius: '5px', border: '1px solid #ccc', width: 'calc(50% - 20px)' }
            }),
            React.createElement('button', {
                onClick: handleAddInterval,
                style: { padding: '10px 20px', borderRadius: '5px', border: '1px solid #ccc', backgroundColor: '#007bff', color: 'white', cursor: 'pointer' }
            }, 'Add Interval')
        ]),
        React.createElement('div', null, data.map((interval, index) =>
            React.createElement('div', {
                key: index,
                style: { padding: '10px', border: '1px solid #ccc', borderRadius: '5px', marginBottom: '5px', backgroundColor: '#f9f9f9' }
            }, `Start: ${interval.start}s, End: ${interval.end}s`)
        ))
    ]);
}