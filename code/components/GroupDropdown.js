import React from 'react';

const options = [
    { key: 1, text: 'Group 1', value: 1, color: 'red' },
    { key: 2, text: 'Group 2', value: 2, color: 'blue' },
    { key: 3, text: 'Group 3', value: 3, color: 'green' },
    { key: 4, text: 'Group 4', value: 4, color: 'yellow' },
];

export default function GroupDropdown(props) {
    const { id, value, setProps } = props;

    function onChange(event) {
        setProps({ value: parseInt(event.target.value) });
    }

    return React.createElement('select', {
        id: id,
        value: value,
        onChange: onChange,
        style: { padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }
    }, options.map(option => 
        React.createElement('option', {
            key: option.key,
            value: option.value,
            style: { color: option.color }
        }, option.text)
    ));
}

GroupDropdown.defaultProps = {
    value: 1
};