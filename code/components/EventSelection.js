import React from 'react';

const pastelColors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
];

export default function EventSelection(props) {
    const { id, value, setProps, setOptions: setDashOptions, options = [] } = props; // Accept `options` prop
    const [events, setEvents] = React.useState([]); // Initialize with an empty array
    const [newEventName, setNewEventName] = React.useState(''); // Input for new event
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    React.useEffect(() => {
        // Assign colors iteratively to options if not already provided
        const coloredOptions = options.map((option, index) => ({
            ...option,
            color: option.color || pastelColors[index % pastelColors.length] // Assign color if not provided
        }));
        setEvents(coloredOptions);
    }, [options]);

    function handleNewEventChange(event) {
        setNewEventName(event.target.value);
    }

    function handleAddNewEvent() {
        if (!newEventName.trim()) return; // Prevent adding empty events
        const newEvent = {
            key: newEventName,
            text: newEventName,
            value: newEventName,
            color: pastelColors[events.length % pastelColors.length] // Assign color iteratively
        };
        const newEvents = [...events, newEvent];
        setEvents(newEvents);
        setNewEventName('');
        setProps({ value: newEvent.value });
        setDashOptions(newEvents); // Update Dash options
    }

    function onChange(eventValue) {
        setProps({ value: eventValue });
        setDropdownOpen(false);
    }

    return React.createElement('div', { style: { position: 'relative', display: 'inline-block', width: '400px' } }, [
        // Dropdown for selecting events
        React.createElement('div', {
            id: id,
            onClick: () => setDropdownOpen(!dropdownOpen),
            style: { padding: '10px', borderRadius: '5px', border: '1px solid #ccc', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }
        }, [
            React.createElement('div', { style: { display: 'flex', alignItems: 'center' } }, [
                React.createElement('span', {
                    style: {
                        display: 'inline-block',
                        width: '10px',
                        height: '10px',
                        backgroundColor: events.find(event => event.value === value)?.color || 'transparent',
                        borderRadius: '50%',
                        marginRight: '5px'
                    }
                }),
                React.createElement('span', null, value || 'No event selected')
            ]),
            React.createElement('span', { style: { fontSize: '12px', color: '#888' } }, dropdownOpen ? '▲' : '▼'),
            dropdownOpen && React.createElement('div', {
                style: { position: 'absolute', top: 'calc(100% + 5px)', left: 0, right: 0, border: '1px solid #ccc', borderRadius: '5px', backgroundColor: 'white', zIndex: 1, minWidth: 'max-content', maxHeight: '200px', overflowY: 'auto' }
            }, [
                events.length === 0
                    ? React.createElement('div', { style: { padding: '10px', color: '#888', textAlign: 'center' } }, 'No events registered')
                    : events.map(event =>
                        React.createElement('div', {
                            key: event.key,
                            onClick: () => onChange(event.value),
                            style: { padding: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', marginBottom: '5px' }
                        }, [
                            React.createElement('span', {
                                style: {
                                    display: 'inline-block',
                                    width: '10px',
                                    height: '10px',
                                    backgroundColor: event.color,
                                    borderRadius: '50%',
                                    marginRight: '5px'
                                }
                            }),
                            event.text
                        ])
                    )
            ])
        ]),
        // Input for adding a new event
        React.createElement('div', { style: { display: 'flex', alignItems: 'center', marginTop: '10px' } }, [
            React.createElement('input', {
                type: 'text',
                value: newEventName,
                onChange: handleNewEventChange,
                placeholder: 'Enter event name',
                style: { padding: '10px', width: 'calc(100% - 100px)', marginRight: '10px', borderRadius: '5px', border: '1px solid #ccc' }
            }),
            React.createElement('button', {
                onClick: handleAddNewEvent,
                style: { padding: '10px', borderRadius: '5px', border: '1px solid #ccc', backgroundColor: '#007bff', color: 'white', cursor: 'pointer', whiteSpace: 'nowrap' }
            }, 'Add Event')
        ])
    ]);
}

EventSelection.defaultProps = {
    value: '',
    options: [] // Default to an empty array if no options are provided
};