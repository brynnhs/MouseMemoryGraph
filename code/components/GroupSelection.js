import React from 'react';

const pastelColors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
];

// Initial options
const initialOptions = [
    { key: 'Recent', text: 'Recent', value: 'Recent', color: pastelColors[0] },
    { key: 'Remote', text: 'Remote', value: 'Remote', color: pastelColors[1] },
    { key: 'Control', text: 'Control', value: 'Control', color: pastelColors[2] },
];

export default function MultiSelectDropdown(props) {
    const { id, value, setProps, options } = props;
    // Initialize selectedValues from the passed value (default to empty array)
    const [selectedValues, setSelectedValues] = React.useState(value || []);
    const [dropdownOpen, setDropdownOpen] = React.useState(false);

    // Combine initial options with dynamically passed options
    const combinedOptions = React.useMemo(() => {
        return [...initialOptions, ...(options || [])];
    }, [options]);

    // Ensure no duplicate options by filtering unique keys
    const uniqueOptions = React.useMemo(() => {
        const seenKeys = new Set();
        return combinedOptions.filter(option => {
            if (seenKeys.has(option.key)) {
                return false;
            }
            seenKeys.add(option.key);
            return true;
        });
    }, [combinedOptions]);

    function toggleOption(val) {
        let newSelected;
        if (selectedValues.includes(val)) {
            newSelected = selectedValues.filter(v => v !== val);
        } else {
            newSelected = [...selectedValues, val];
        }
        setSelectedValues(newSelected);
        if (setProps) {
            setProps({ value: newSelected });
        }
    }

    return React.createElement('div', { style: { position: 'relative', display: 'inline-block' } }, [
        React.createElement('div', {
            onClick: () => setDropdownOpen(!dropdownOpen),
            style: { padding: '10px', borderRadius: '5px', border: '1px solid #ccc', cursor: 'pointer' }
        }, dropdownOpen ? 'Select Options' : 'Selected Groups'),
        dropdownOpen && React.createElement('div', {
            style: { 
                position: 'absolute', 
                top: '100%', 
                left: 0, 
                right: 0, 
                border: '1px solid #ccc', 
                borderRadius: '5px', 
                backgroundColor: 'white', 
                zIndex: 1, 
                minWidth: 'max-content' 
            }
        }, uniqueOptions.map(option => 
            React.createElement('div', {
                key: option.key,
                onClick: () => toggleOption(option.value),
                style: { 
                    padding: '10px', 
                    cursor: 'pointer', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between' 
                }
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
                React.createElement('span', {
                    style: {
                        opacity: selectedValues.includes(option.value) ? 1 : 0.5
                    }
                }, option.text),
                React.createElement('input', {
                    type: 'checkbox',
                    checked: selectedValues.includes(option.value),
                    readOnly: true,
                    style: { marginLeft: 'auto', opacity: selectedValues.includes(option.value) ? 1 : 0.5 }
                })
            ])
        ))
    ]);
}

MultiSelectDropdown.defaultProps = {
    value: [],
    options: []
};