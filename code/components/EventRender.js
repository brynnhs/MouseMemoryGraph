import React from 'react';

const pastelColors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
];

const predefinedOption = {
    key: 'freezing',
    text: 'freezing',
    value: 'freezing',
    color: 'lightblue'
};

export default function DropdownSelection(props) {
    const { id, value, setProps, setOptions: setDashOptions, options = [] } = props;
    const [events, setEvents] = React.useState([predefinedOption]); // Initialize with "freezing" option
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    React.useEffect(() => {
        // Ensure "freezing" is always included and assign colors to other options
        const coloredOptions = options.map((option, index) => ({
            ...option,
            color: option.color || pastelColors[index % pastelColors.length] // Assign color if not provided
        }));
        const updatedEvents = [predefinedOption, ...coloredOptions.filter(option => option.value !== 'freezing')]; // Avoid duplicate "freezing"
        setEvents(updatedEvents);
    }, [options]);

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
                React.createElement('span', null, value || 'Freezing') // Default to "Freezing" if no value is selected
            ]),
            React.createElement('span', { style: { fontSize: '12px', color: '#888' } }, dropdownOpen ? '▲' : '▼'),
            dropdownOpen && React.createElement('div', {
                style: { position: 'absolute', top: 'calc(100% + 5px)', left: 0, right: 0, border: '1px solid #ccc', borderRadius: '5px', backgroundColor: 'white', zIndex: 1, minWidth: 'max-content', maxHeight: '200px', overflowY: 'auto' }
            }, [
                events.map(event =>
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
        ])
    ]);
}

DropdownSelection.defaultProps = {
    value: 'freezing', // Default to "freezing"
    options: [] // Default to an empty array if no options are provided
};