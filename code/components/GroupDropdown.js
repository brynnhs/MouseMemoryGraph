import React from 'react';

const pastelColors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
];

const initialOptions = [
    { key: 'Recent', text: 'Recent', value: 'Recent', color: pastelColors[0] },
    { key: 'Remote', text: 'Remote', value: 'Remote', color: pastelColors[1] },
    { key: 'Control', text: 'Control', value: 'Control', color: pastelColors[2] },
];

export default function GroupDropdown(props) {
    const { id, value, setProps, options: dashOptions = [], currentColor, setCurrentColor } = props;
    const [options, setOptions] = React.useState([...initialOptions, ...dashOptions]);
    const [newGroupName, setNewGroupName] = React.useState('');
    const [showTextbox, setShowTextbox] = React.useState(false);
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    // Update internal options state whenever the Dash-provided options change
    React.useEffect(() => {
        const mergedOptions = [...initialOptions, ...dashOptions];
        const uniqueOptions = mergedOptions.filter(
            (option, index, self) =>
                index === self.findIndex((o) => o.value === option.value)
        );
        setOptions(uniqueOptions);
    }, [dashOptions]);

    function onChange(optionValue) {
        if (optionValue === 'new') {
            setShowTextbox(true);
        } else if (optionValue !== '000000') { // Exclude 'loading' option
            const selectedOption = options.find(option => option.value === optionValue);
            setProps({ value: optionValue, currentColor: selectedOption?.color || pastelColors[0] }); // Update currentColor externally
            setCurrentColor(selectedOption?.color || pastelColors[0]); // Update currentColor internally
            setDropdownOpen(false);
        }
    }

    function handleNewGroupChange(event) {
        setNewGroupName(event.target.value);
    }

    function handleAddNewGroup() {
        const newGroup = {
            key: newGroupName,
            text: newGroupName,
            value: newGroupName,
            color: pastelColors[options.length % pastelColors.length] // Assign color iteratively
        };
        const newOptions = [...options, newGroup];
        setOptions(newOptions);
        setNewGroupName('');
        setShowTextbox(false);
        setProps({ value: newGroup.value, currentColor: newGroup.color }); // Update currentColor externally
        setCurrentColor(newGroup.color); // Update currentColor internally
        setDropdownOpen(false);
    }

    return React.createElement('div', { style: { position: 'relative', display: 'inline-block' } }, [
        React.createElement('div', {
            id: id,
            onClick: () => value !== '000000' && setDropdownOpen(!dropdownOpen), // Disable dropdown if 'loading'
            style: { 
                padding: '10px', 
                borderRadius: '5px', 
                border: '1px solid #ccc', 
                cursor: value === '000000' ? 'not-allowed' : 'pointer', // Disable cursor if 'loading'
                display: 'flex', 
                alignItems: 'center', 
                backgroundColor: value === '000000' ? '#f0f0f0' : 'white' // Gray out if 'loading'
            }
        }, [
            React.createElement('span', {
                style: {
                    display: 'inline-block',
                    width: '10px',
                    height: '10px',
                    backgroundColor: value === '000000' ? 'transparent' : options.find(option => option.value === value)?.color,
                    borderRadius: '50%',
                    marginRight: '5px'
                }
            }),
            value === '000000' ? 'Loading...' : (options.find(option => option.value === value)?.text || 'Select Group') // Show 'Loading...' if 'loading'
        ]),
        dropdownOpen && React.createElement('div', {
            style: { position: 'absolute', top: '100%', left: 0, right: 0, border: '1px solid #ccc', borderRadius: '5px', backgroundColor: 'white', zIndex: 1, minWidth: 'max-content' }
        }, [
            ...options.map(option => 
                React.createElement('div', {
                    key: option.key,
                    onClick: () => onChange(option.value),
                    style: { padding: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', marginBottom: '5px' }
                }, [
                    React.createElement('span', {
                        style: {
                            display: 'inline-block',
                            width: '10px',
                            height: '10px',
                            backgroundColor: option.color,
                            borderRadius: '50%',
                            marginRight: '5px'
                        }
                    }),
                    option.text
                ])
            ),
            React.createElement('div', {
                key: 'new',
                onClick: () => onChange('new'),
                style: { padding: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', marginBottom: '5px', backgroundColor: '#f0f0f0' }
            }, [
                React.createElement('span', {
                    style: {
                        display: 'inline-block',
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        marginRight: '5px',
                        textAlign: 'center',
                        lineHeight: '10px',
                        fontWeight: 'bold'
                    }
                }, '+'),
                'Create New Group'
            ])
        ]),
        showTextbox && React.createElement('div', { style: { marginTop: '10px' } }, [
            React.createElement('input', {
                type: 'text',
                value: newGroupName,
                onChange: handleNewGroupChange,
                placeholder: 'Enter group name',
                style: { padding: '5px', margin: '10px 0', borderRadius: '5px', border: '1px solid #ccc' }
            }),
            React.createElement('button', {
                onClick: handleAddNewGroup,
                style: { padding: '5px 10px', borderRadius: '5px', border: '1px solid #ccc', backgroundColor: '#007bff', color: 'white' }
            }, 'OK')
        ])
    ]);
}

GroupDropdown.defaultProps = {
    value: 'Recent',
    currentColor: '#FFB3BA', // Default color
    options: [] // Default to an empty array
};