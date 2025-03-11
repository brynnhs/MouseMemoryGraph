import React from 'react';

const pastelColors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
];

const initialOptions = [
    { key: 1, text: 'Recent', value: 1, color: pastelColors[0] },
    { key: 2, text: 'Remote', value: 2, color: pastelColors[1] },
    { key: 3, text: 'Control', value: 3, color: pastelColors[2] },
];

export default function GroupDropdown(props) {
    const { id, value, setProps } = props;
    const [options, setOptions] = React.useState(initialOptions);
    const [newGroupName, setNewGroupName] = React.useState('');
    const [showTextbox, setShowTextbox] = React.useState(false);
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    function onChange(optionValue) {
        if (optionValue === 'new') {
            setShowTextbox(true);
        } else {
            setProps({ value: optionValue });
            setDropdownOpen(false);
        }
    }

    function handleNewGroupChange(event) {
        setNewGroupName(event.target.value);
    }

    function handleAddNewGroup() {
        const newGroup = {
            key: options.length + 1,
            text: newGroupName,
            value: options.length + 1,
            color: pastelColors[options.length % pastelColors.length] // Assign color iteratively
        };
        setOptions([...options, newGroup]);
        setNewGroupName('');
        setShowTextbox(false);
        setProps({ value: newGroup.value });
        setDropdownOpen(false);
    }

    return React.createElement('div', { style: { position: 'relative', display: 'inline-block' } }, [
        React.createElement('div', {
            id: id,
            onClick: () => setDropdownOpen(!dropdownOpen),
            style: { padding: '10px', borderRadius: '5px', border: '1px solid #ccc', cursor: 'pointer', display: 'flex', alignItems: 'center' }
        }, [
            React.createElement('span', {
                style: {
                    display: 'inline-block',
                    width: '10px',
                    height: '10px',
                    backgroundColor: options.find(option => option.value === value)?.color,
                    borderRadius: '50%',
                    marginRight: '5px'
                }
            }),
            options.find(option => option.value === value)?.text || 'Select Group'
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
    value: 1
};