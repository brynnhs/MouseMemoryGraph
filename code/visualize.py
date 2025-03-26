import plotly.graph_objs as go
import numpy as np
from utils import hex_to_rgba


pastel_colors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
]

def generate_average_plot(sensor, epochs_on, epochs_off, avg_on, avg_off, before, after, fps, color_map, event_color=None, color_overrides=None):
    """
    Generate average plots for ON and OFF epochs.
    
    If epochs_on (or epochs_off) is a dictionary, then:
      - For each key (group), a trace is added showing that group's average.
      - An overall average (mean and std) across all groups is computed and added as a separate trace.
    If epochs_on is a list, the function behaves as before.
    """
    print('color overrides in generate_average_plot:', color_overrides)
    # Create common x-axis based on the epoch window and fps.
    x = np.arange(-before, after, 1 / fps)

    if color_overrides is None:
        color_overrides = {}
    
    # ----- Onset Plot -----
    fig_on = go.Figure()
    
    # Check if epochs_on is a dictionary (grouped data)
    if isinstance(epochs_on, dict):
        overall_on = []
        # Add a trace for each group's average
        for group, group_epochs in epochs_on.items():
            if not group_epochs:
                continue
            arr = np.array(group_epochs)  # shape: (n_epochs, len(x))
            mean_on = np.mean(arr, axis=0)
            std_on = np.std(arr, axis=0)

            
            # Collect data for overall average
            overall_on.extend(group_epochs)


            # Use overridden color if available
            trace_name = f'Group {group}'
            line_color = color_overrides.get(trace_name, color_map.get(group, '#000000'))

            fig_on.add_trace(go.Scatter(
                x=x, y=mean_on, mode='lines',
                name=trace_name,
                line=dict(color=line_color)
            ))
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_on + std_on,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_on - std_on,
                mode='lines',
                fill='tonexty',
                fillcolor=hex_to_rgba(line_color, 0.3),
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))

        # Now add the overall average trace (if any epochs were collected)
        if overall_on:
            line_color = color_overrides.get('Overall Average', None)
            line_color = hex_to_rgba(line_color, 1) if line_color else None

            arr_overall = np.array(overall_on)
            mean_overall = np.mean(arr_overall, axis=0)
            std_overall = np.std(arr_overall, axis=0)
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_overall, mode='lines',
                name='Overall Average',
                line=dict(width=3, dash='dash', color='rgba(128,128,128,0.8)' if not line_color else line_color),
            ))
    
    fig_on.update_layout(
        title=f'{sensor} Onset Average Epoch',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig_on.add_vrect(x0=0, x1=after, fillcolor=event_color if event_color else 'lightblue', opacity=0.3, layer='below', line_width=0)
    
    # ----- Offset Plot -----
    fig_off = go.Figure()
    
    if isinstance(epochs_off, dict):
        overall_off = []
        for group, group_epochs in epochs_off.items():
            if not group_epochs:
                continue
            arr = np.array(group_epochs)
            mean_off = np.mean(arr, axis=0)
            std_off = np.std(arr, axis=0)
            overall_off.extend(group_epochs)

            trace_name = f'Group {group}'
            line_color = color_overrides.get(trace_name, color_map.get(group, '#000000'))

            fig_off.add_trace(go.Scatter(
                x=x, y=mean_off, mode='lines',
                name=trace_name,
                line=dict(color=line_color)
            ))
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_off + std_off,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_off - std_off,
                mode='lines',
                fill='tonexty',
                fillcolor=hex_to_rgba(line_color, 0.3),
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
        if overall_off:
            line_color = color_overrides.get('Overall Average', None)
            line_color = hex_to_rgba(line_color, 1) if line_color else None
        
            arr_overall = np.array(overall_off)
            mean_overall = np.mean(arr_overall, axis=0)
            std_overall = np.std(arr_overall, axis=0)
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_overall, mode='lines',
                name='Overall Average',
                line=dict(width=3, dash='dash', color='rgba(128,128,128,0.8)'  if not line_color else line_color),
            ))
            
    fig_off.update_layout(
        title=f'{sensor} Offset Average Epoch',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig_off.add_vrect(x0=-before, x1=0, fillcolor=event_color if event_color else 'lightblue', opacity=0.3, layer='below', line_width=0)

    # average change plot
    avg_change_on = go.Figure(layout_yaxis_range=[-2, 2])

    for group, group_avg in avg_on.items():
        bar_color = color_overrides.get(f"{group} bar plot", None)
        scatter_color = color_overrides.get(f"{group} scatter plot", None)
        avg_change_on.add_trace(go.Scatter(
            x=[group] * len(group_avg),
            y=group_avg,
            mode='markers',
            marker_color=scatter_color if scatter_color else color_map[group],
            name=f"{group} scatter plot")
        )
        avg_change_on.add_trace(go.Bar(
            x=[group],
            y=[np.mean(group_avg)],
            marker_color=[bar_color if bar_color else color_map[group]],
            opacity=0.3,
            name=f"{group} bar plot",
            error_y=dict(type='data', array=[np.std(group_avg)], visible=True)
        ))
    avg_change_on.update_layout(
        title=f'zdFF Change onset', 
        xaxis_title='Event', 
        yaxis_title='zdFF',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)',
        bargap=0.8,
        showlegend=False
    )

    avg_change_off = go.Figure(layout_yaxis_range=[-2, 2])
    for group, group_avg in avg_off.items():
        bar_color = color_overrides.get(f"{group} bar plot", color_map.get(group, '#000000'))
        scatter_color = color_overrides.get(f"{group} scatter plot", color_map.get(group, '#000000'))
        avg_change_off.add_trace(go.Scatter(
            x=[group] * len(group_avg),
            y=group_avg,
            mode='markers',
            name=f"{group} scatter plot",
            marker_color=scatter_color if scatter_color else color_map[group])
        )
        avg_change_off.add_trace(go.Bar(
            x=[group],
            y=[np.mean(group_avg)],
            marker_color=[bar_color if bar_color else color_map[group]],
            opacity=0.3,
            name=f"{group} bar plot",
            error_y=dict(type='data', array=[np.std(group_avg)], visible=True)
        ))
    avg_change_off.update_layout(
        title=f'zdFF Change offset', 
        xaxis_title='Event', 
        yaxis_title='zdFF',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)',
        bargap=0.8,
        showlegend=False
    )
    
    return fig_on, fig_off, avg_change_on, avg_change_off

def generate_plots(object, mergeddataset, freezing_intervals, fps, before, after, epochs_acc_on, epochs_acc_off, avg_on, avg_off, event, event_colors, name='ACC'):
    """
    Generate detailed plots for the given sensor:
      - The full signals figure 
      - The interval_on figure (with multiple onsets + mean) 
      - The interval_off figure (with multiple offsets + mean)
    """
    # [Original code remains unchanged...]
    fig = go.Figure(layout_yaxis_range=[-5, 5])
    interval_on = go.Figure(layout_yaxis_range=[-4, 4])
    interval_off = go.Figure(layout_yaxis_range=[-4, 4])
    avg_change = go.Figure(layout_yaxis_range=[-2, 2])
    x = np.arange(0, len(mergeddataset) / fps, 1 / fps)
    
    # Full signals
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.signal'], 
        mode='lines', 
        name=f'{name} Signal', 
        line=dict(color='gray', width=1, dash='solid'), 
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.control'], 
        mode='lines', 
        name=f'{name} Control', 
        line=dict(color='gray', width=1, dash='solid'), 
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=x, 
        y=mergeddataset[f'{name}.zdFF'], 
        mode='lines', 
        name=f'{name} zdFF', 
        line=dict(color='blue', width=2, dash='solid')
    ))
    fig.update_layout(title=f'{name} Signal, Control, and zdFF', xaxis_title='Time (s)', yaxis_title='Value')
    
    
    # Highlight all freezing intervals
    for on, off in freezing_intervals:
        on_sec = on / fps
        off_sec = off / fps
        fig.add_vrect(name='freezing bouts', x0=on_sec, x1=off_sec, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0,
                      showlegend=True)

    for i, e in enumerate(object.events):
        if e != 'freezing':
            event_intervals = object.get_freezing_intervals(0, e)
            for on, off in event_intervals:
                on_sec = on / fps
                off_sec = off / fps
                fig.add_vrect(name=f'{e}', x0=on_sec, x1=off_sec, fillcolor=event_colors[e], opacity=0.2, layer='below', line_width=0,
                              showlegend=True)
    
    # Build the interval_on and interval_off figures
    aggregate_on = []
    aggregate_off = []
    
    for i, inter in enumerate(epochs_acc_on):
        x_epoch = np.arange(-before, after, 1 / fps)
        y_epoch = inter[2]
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'onset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_on.append(y_epoch)
        fig.add_vrect(
            x0=inter[1][0] / fps, x1=inter[1][1] / fps, fillcolor='blue' if event=='freezing' else event_colors[event], 
            opacity=0.2, layer='below', line_width=0,
            name=f'{event} bouts in analysis',
            showlegend=True
        )
    
    for i, inter in enumerate(epochs_acc_off):
        x_epoch = np.arange(-before, after, 1 / fps)
        y_epoch = inter[2]
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=y_epoch, name=f'offset {i+1}', mode='lines', 
            line=dict(color='gray', width=1, dash='solid'), opacity=0.5
        ))
        aggregate_off.append(y_epoch)
    
    # Compute mean & std for onsets
    aggregate_on = np.array(aggregate_on)
    if len(aggregate_on) > 0:
        mean_on = np.mean(aggregate_on, axis=0)
        std_on = np.std(aggregate_on, axis=0)
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=mean_on, mode='lines', name='mean signal', 
            line=dict(color='blue', width=2, dash='solid')
        ))
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=mean_on + std_on, hoverinfo="skip", fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False
        ))
        interval_on.add_trace(go.Scatter(
            x=x_epoch, y=mean_on - std_on, fill='tonexty', hoverinfo="skip",
            fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), showlegend=False
        ))
        interval_on.add_vrect(x0=0, x1=after, fillcolor='lightblue' if event=='freezing' else event_colors[event], 
                              opacity=0.3, layer='below', line_width=0)
    
    # Compute mean & std for offsets
    aggregate_off = np.array(aggregate_off)
    if len(aggregate_off) > 0:
        mean_off = np.mean(aggregate_off, axis=0)
        std_off = np.std(aggregate_off, axis=0)
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=mean_off, mode='lines', name='mean signal', 
            line=dict(color='blue', width=2, dash='solid')
        ))
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=mean_off + std_off, hoverinfo="skip", fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False
        ))
        interval_off.add_trace(go.Scatter(
            x=x_epoch, y=mean_off - std_off, fill='tonexty', hoverinfo="skip",
            fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color='rgba(255,255,255,0)'), showlegend=False
        ))
        interval_off.add_vrect(x0=-before, x1=0, fillcolor='lightblue' if event=='freezing' else event_colors[event],
                               opacity=0.3, layer='below', line_width=0)
    
    # Bar plot for the zdFF change
    if avg_on and avg_off:
        avg_on = np.array(avg_on)
        avg_off = np.array(avg_off)
        avg_change.add_trace(go.Scatter(
            x=['Onset'] * len(avg_on[:, 2]),
            y=avg_on[:, 2],
            mode='markers',
            name='Onset scatter',
            marker_color='blue'
        ))
        avg_change.add_trace(go.Scatter(
            x=['Offset'] * len(avg_off[:, 2]),
            y=avg_off[:, 2],
            mode='markers',
            name='Offset scatter',
            marker_color='lightblue'
        ))
        avg_change.add_trace(go.Bar(
            x=['Onset'],
            y=[np.mean(avg_on[:, 2])],
            marker_color=['blue'],
            opacity=0.3,
            error_y=dict(type='data', array=[np.std(avg_on[:, 2])], visible=True),
            name='Onset bar'
        ))
        avg_change.add_trace(go.Bar(
            x=['Offset'],
            y=[np.mean(avg_off[:, 2])],
            marker_color=['lightblue'],
            opacity=0.3,
            error_y=dict(type='data', array=[np.std(avg_off[:, 2])], visible=True),
            name='Offset bar'
        ))
        avg_change.update_layout(title=f'{name} zdFF Change', xaxis_title='Event', yaxis_title='zdFF')
    
    interval_on.update_layout(
        title='Signal around event onset',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    interval_off.update_layout(
        title='Signal around event offset',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)'
    )
    avg_change.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)',
        bargap=0.8,
        showlegend=False
    )
    
    return fig, interval_on, interval_off, avg_change

def generate_separated_plot(object, sensor, offset, epochs_on, mergeddataset, fps, freezing_intervals, seconds_after, event, event_colors):
    """
    Generate a separated plot for a given sensor (e.g., 'ACC' or 'ADN').

    - `offset`: fixed value to subtract from the control channel.
    - `epochs_on`: the onset epoch data (used to add additional shading).
    - `mergeddataset`: the merged dataframe containing the sensor data.
    - `fps`: frames per second.
    - `intervals`: freezing intervals.
    - `seconds_after`: used for legend text.
    
    The function converts the sensor signal and control into a percentage of the maximum absolute zdFF,
    subtracts the offset from the control, adds traces, and replicates the freezing shading logic:
    (A) Shades all intervals with lightblue (opacity 0.3),
    (B) Shades onset epochs with blue (opacity 0.2),
    and adds dummy legend traces. The background is set to white.
    """
    fig = go.Figure()
    x_vals = np.arange(0, len(mergeddataset) / fps, 1 / fps)
    
    zdff = mergeddataset[f'{sensor}.zdFF']
    max_z = np.max(np.abs(zdff)) if np.max(np.abs(zdff)) != 0 else 1
    signal = mergeddataset[f'{sensor}.signal']
    control = mergeddataset[f'{sensor}.control']
    
    signal_percent = 100 * (signal / max_z)
    control_percent = 100 * (control / max_z)
    
    # Subtract the fixed offset from the control channel
    control_percent = control_percent - offset
     
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=signal_percent,
        mode='lines',
        name=f'{sensor} Signal',
        line=dict(color='blue', width=1, dash='solid'),

    ))
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=control_percent,
        mode='lines',
        name=f'{sensor} Control',
        line=dict(color='gray', width=1, dash='solid'), 
        opacity=0.5
    ))


    for i, e in enumerate(object.events):
        if e != 'freezing':
            event_intervals = object.get_freezing_intervals(0, e)
            for on, off in event_intervals:
                on_sec = on / fps
                off_sec = off / fps
                fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor=event_colors[e], opacity=0.2, layer='below', line_width=0,
                              showlegend=True, name=f'{e}')
     
    # (A) Shade all freezing intervals with lightblue (opacity 0.3)
    for on_time, off_time in freezing_intervals:
        fig.add_vrect(
            x0=on_time / fps,
            x1=off_time / fps,
            fillcolor='lightblue',
            opacity=0.3,
            layer='below',
            line_width=0,
            showlegend=True,
            name='freezing bouts'
        )
    for inter in epochs_on:
        fig.add_vrect(
            x0=inter[1][0] / fps, 
            x1=inter[1][1] / fps, 
            fillcolor='blue' if event=='freezing' else event_colors[event], 
            opacity=0.2, 
            layer='below', 
            line_width=0,
            showlegend=True,
            name=f'{event} bouts in analysis'
        )
     
    overall_min = min(signal_percent.min(), control_percent.min()) - 5
    overall_max = max(signal_percent.max(), control_percent.max()) + 5
    fig.update_yaxes(range=[overall_min, overall_max], showticklabels=False)
    fig.update_layout(title='', xaxis_title='Time (s)', yaxis_title=f'% of {sensor} zdFF',
                    paper_bgcolor='white', plot_bgcolor='white')
    return fig