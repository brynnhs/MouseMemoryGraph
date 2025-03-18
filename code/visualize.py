import plotly.graph_objs as go
import numpy as np

color_map = {
    'Recent': '#FFB3BA',
    'Remote': '#FFDFBA',
    'Control': '#FFFFBA'
}

pastel_colors = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D4BAFF', '#FFBAE1', '#BAFFD4'
]

def generate_average_plot(sensor, epochs_on, epochs_off, avg_on, avg_off, before, after, fps, color_overrides=None):
    """
    Generate average plots for ON and OFF epochs.
    
    If epochs_on (or epochs_off) is a dictionary, then:
      - For each key (group), a trace is added showing that group's average.
      - An overall average (mean and std) across all groups is computed and added as a separate trace.
    If epochs_on is a list, the function behaves as before.
    """
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

        # Now add the overall average trace (if any epochs were collected)
        if overall_on:
            arr_overall = np.array(overall_on)
            mean_overall = np.mean(arr_overall, axis=0)
            std_overall = np.std(arr_overall, axis=0)
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_overall, mode='lines',
                name='Overall Average',
                line=dict(width=3, dash='dash', color='rgba(128,128,128,0.8)')
            ))
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_overall + std_overall,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
            fig_on.add_trace(go.Scatter(
                x=x, y=mean_overall - std_overall,
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
    
    fig_on.update_layout(
        title=f'{sensor} Onset Average Epoch',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig_on.add_vrect(x0=-before, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    
    # ----- Offset Plot -----
    fig_off = go.Figure()
    
    if isinstance(epochs_off, dict):
        overall_off = []
        for group, group_epochs in epochs_off.items():
            if not group_epochs:
                continue
            arr = np.array(group_epochs)
            mean_off = np.mean(arr, axis=0)
            overall_off.extend(group_epochs)

            trace_name = f'Group {group}'
            line_color = color_overrides.get(trace_name, color_map.get(group, '#000000'))

            fig_off.add_trace(go.Scatter(
                x=x, y=mean_off, mode='lines',
                name=trace_name,
                line=dict(color=line_color)
            ))
        if overall_off:
            arr_overall = np.array(overall_off)
            mean_overall = np.mean(arr_overall, axis=0)
            std_overall = np.std(arr_overall, axis=0)
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_overall, mode='lines',
                name='Overall Average',
                line=dict(width=3, dash='dash', color='rgba(128,128,128,0.8)'),
            ))
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_overall + std_overall,
                mode='lines',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
            fig_off.add_trace(go.Scatter(
                x=x, y=mean_overall - std_overall,
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False,
                hoverinfo="skip"
            ))
            
    fig_off.update_layout(
        title=f'{sensor} Offset Average Epoch',
        xaxis_title='Time (s)',
        yaxis_title='Signal',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 10, 10, 0.02)'
    )
    fig_off.add_vrect(x0=0, x1=after, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    # average change plot
    avg_change_on = go.Figure(layout_yaxis_range=[-2, 2])

    for group, group_avg in avg_on.items():
        avg_change_on.add_trace(go.Scatter(
            x=[group] * len(group_avg),
            y=group_avg,
            mode='markers',
            marker_color=color_map[group])
        )
        avg_change_on.add_trace(go.Bar(
            x=[group],
            y=[np.mean(group_avg)],
            marker_color=[color_map[group]],
            opacity=0.3,
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
        avg_change_off.add_trace(go.Scatter(
            x=[group] * len(group_avg),
            y=group_avg,
            mode='markers',
            marker_color=color_map[group])
        )
        avg_change_off.add_trace(go.Bar(
            x=[group],
            y=[np.mean(group_avg)],
            marker_color=[color_map[group]],
            opacity=0.3,
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

def generate_plots(object, mergeddataset, freezing_intervals, fps, before, after, epochs_acc_on, epochs_acc_off, avg_on, avg_off, event, name='ACC'):
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
    
    # Dummy traces for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'freezing bouts in analysis', 
        marker=dict(color='blue', size=7, symbol='square', opacity=0.2)
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers', name=f'all freezing bouts', 
        marker=dict(color='lightblue', size=7, symbol='square', opacity=0.3)
    ))
    
    # Highlight all freezing intervals
    for on, off in freezing_intervals:
        on_sec = on / fps
        off_sec = off / fps
        fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)

    for i, e in enumerate(object.events):
        if e != 'freezing':
            event_intervals = object.get_freezing_intervals(0, e)
            for on, off in event_intervals:
                on_sec = on / fps
                off_sec = off / fps
                fig.add_vrect(x0=on_sec, x1=off_sec, fillcolor=pastel_colors[0], opacity=0.2, layer='below', line_width=0)
            # Check if a trace with the same name already exists
            if not any(trace.name == f'Event {e}' for trace in fig.data):
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode='markers', name=f'Event {e}', 
                    marker=dict(color=pastel_colors[0], size=7, symbol='square', opacity=0.3)
                ))
    
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
            x0=inter[1][0] / fps, x1=inter[1][1] / fps, fillcolor='blue' if event=='freezing' else pastel_colors[0], 
            opacity=0.2, layer='below', line_width=0
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
        interval_on.add_vrect(x0=0, x1=after, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    
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
        interval_off.add_vrect(x0=-before, x1=0, fillcolor='lightblue', opacity=0.3, layer='below', line_width=0)
    
    # Bar plot for the zdFF change
    if avg_on and avg_off:
        avg_on = np.array(avg_on)
        avg_off = np.array(avg_off)
        avg_change.add_trace(go.Scatter(
            x=['Onset'] * len(avg_on[:, 2]),
            y=avg_on[:, 2],
            mode='markers',
            marker_color='blue'
        ))
        avg_change.add_trace(go.Scatter(
            x=['Offset'] * len(avg_off[:, 2]),
            y=avg_off[:, 2],
            mode='markers',
            marker_color='lightblue'
        ))
        avg_change.add_trace(go.Bar(
            x=['Onset', 'Offset'],
            y=[np.mean(avg_on[:, 2]), np.mean(avg_off[:, 2])],
            marker_color=['blue', 'lightblue'],
            opacity=0.3,
            error_y=dict(type='data', array=[np.std(avg_on[:, 2]), np.std(avg_off[:, 2])], visible=True)
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