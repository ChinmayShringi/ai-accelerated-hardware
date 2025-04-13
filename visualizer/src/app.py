import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import sys
import os

# Add repository root to Python path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(repo_root)

# Import only what we need
from compiler.nnhw.top import FIPMethod  # Just import FIPMethod enum

# Constants from rtl/top/define.svh
class Globals:
    BASELINE = 0
    FIP = 1 
    FFIP = 2

# Read hardware configuration from define.svh
def read_hardware_config():
    with open(os.path.join(repo_root, 'rtl/top/define.svh'), 'r') as f:
        config = f.read()
        # Parse important parameters
        params = {}
        for line in config.split('\n'):
            # Skip lines without '=' or with comments
            if '=' not in line or '//' in line:
                continue
                
            if 'FIP_METHOD' in line:
                # Extract the enum value after '='
                value = line.split('=')[1].strip().split(';')[0].strip()
                # Remove any backslashes
                value = value.replace('\\', '').strip()
                # Map enum values to integers
                if 'BASELINE' in value:
                    params['FIP_METHOD'] = 0
                elif 'FIP' in value:
                    params['FIP_METHOD'] = 1
                elif 'FFIP' in value:
                    params['FIP_METHOD'] = 2
                else:
                    params['FIP_METHOD'] = 0  # Default to baseline
            elif 'SZI =' in line:
                value = line.split('=')[1].strip().split(';')[0].strip()
                # Remove any backslashes and commas
                value = value.replace('\\', '').replace(',', '').strip()
                try:
                    params['SZI'] = int(value)
                except ValueError:
                    params['SZI'] = 4  # Default value
            elif 'LAYERIO_WIDTH =' in line:
                value = line.split('=')[1].strip().split(';')[0].strip()
                # Remove any backslashes and commas
                value = value.replace('\\', '').replace(',', '').strip()
                try:
                    params['LAYERIO_WIDTH'] = int(value)
                except ValueError:
                    params['LAYERIO_WIDTH'] = 8  # Default value
            elif 'WEIGHT_WIDTH =' in line:
                value = line.split('=')[1].strip().split(';')[0].strip()
                # Remove any backslashes and commas
                value = value.replace('\\', '').replace(',', '').strip()
                try:
                    params['WEIGHT_WIDTH'] = int(value)
                except ValueError:
                    params['WEIGHT_WIDTH'] = 8  # Default value
        
        # Ensure all required parameters have values
        if 'FIP_METHOD' not in params:
            params['FIP_METHOD'] = 0
        if 'SZI' not in params:
            params['SZI'] = 4
        if 'LAYERIO_WIDTH' not in params:
            params['LAYERIO_WIDTH'] = 8
        if 'WEIGHT_WIDTH' not in params:
            params['WEIGHT_WIDTH'] = 8
            
    return params

# Read actual RTL implementation
def read_mac_array_impl():
    with open(os.path.join(repo_root, 'rtl/arith/mac_array.sv'), 'r') as f:
        return f.read()

class SystolicArrayVisualizer:
    def __init__(self, rows, cols, fip_method=Globals.BASELINE):
        # Read hardware configuration
        self.hw_config = read_hardware_config()
        self.mac_array_impl = read_mac_array_impl()
        
        # Use parameters from define.svh
        self.rows = rows  # SZI
        self.cols = cols  # SZJ
        self.fip_method = fip_method
        self.layerio_width = self.hw_config.get('LAYERIO_WIDTH', 8)
        self.weight_width = self.hw_config.get('WEIGHT_WIDTH', 8)
        
        # State variables
        self.array_state = np.zeros((rows, cols))
        self.heatmap_data = np.zeros((rows, cols))
        self.cycle_count = 0
        self.total_mults = 0
        self.pe_values = np.zeros((rows, cols, 2))  # Store a and b values
        self.chainout = np.zeros((rows, cols))  # For modeling DSP chainout
        
        # FIP specific parameters
        self.pe_input_depth = 4 if fip_method > Globals.BASELINE else 2
        self.szi_fip = rows + 1 if fip_method > Globals.BASELINE else rows
        
        # Add MAC counting variables
        self.mac_counts = np.zeros((rows, cols))  # Track MACs per PE
        self.cycle_macs = []  # Track MACs per cycle for logging
        
        # Add cycle history tracking
        self.array_states_history = []  # Store array state for each cycle
        self.heatmap_history = []  # Store heatmap data for each cycle
        self.cycle_macs_history = []  # Store MAC counts per cycle
        
    def reset(self):
        self.__init__(self.rows, self.cols, self.fip_method)
    
    def simulate_cycle(self, A, B):
        """Simulate one cycle using actual hardware implementation logic"""
        self.cycle_count += 1
        new_states = {}
        cycle_mac_count = 0  # Track MACs in this cycle
        
        # Follow mac_array.sv implementation
        for i in range(self.rows):
            for j in range(self.cols):
                if self.fip_method == Globals.FFIP:
                    # FFIP implementation from mac_array.sv
                    if i < self.szi_fip - 1:
                        # FFIP only uses A matrix for first SZI_FIP-1 rows
                        a_val = A[i][j] if j < A.shape[1] else 0
                        b_val = 0  # FFIP doesn't use B matrix in these rows
                        
                        # FFIP specific computation - counts as 1 MAC
                        if a_val != 0:
                            self.array_state[i][j] = a_val
                            self.heatmap_data[i][j] += 1
                            self.mac_counts[i][j] += 1
                            cycle_mac_count += 1
                    else:
                        # Last row uses alpha_vec
                        a_val = A[i][j] if j < A.shape[1] else 0
                        b_val = 0
                        if a_val != 0:
                            self.array_state[i][j] = a_val
                            self.heatmap_data[i][j] += 1
                            self.mac_counts[i][j] += 1
                            cycle_mac_count += 1
                    
                elif self.fip_method == Globals.FIP:
                    # FIP implementation from mac_array.sv
                    if i < self.szi_fip - 1:
                        # Get adjacent elements for FIP optimization
                        a0 = A[i][j] if j < A.shape[1] else 0
                        a1 = A[i][j+1] if j+1 < A.shape[1] else 0
                        b0 = B[i][j] if j < B.shape[1] else 0
                        b1 = B[i][j+1] if j+1 < B.shape[1] else 0
                        
                        # FIP optimization: (a0 + b1) * (a1 + b0)
                        # This reduces MAC operations by ~50%
                        if (a0 + b1) != 0 and (a1 + b0) != 0:
                            self.array_state[i][j] = (a0 + b1) * (a1 + b0)
                            self.heatmap_data[i][j] += 1
                            self.mac_counts[i][j] += 1
                            cycle_mac_count += 1
                    else:
                        # Last row uses alpha_vec
                        a_val = A[i][j] if j < A.shape[1] else 0
                        b_val = 0
                        if a_val != 0:
                            self.array_state[i][j] = a_val
                            self.heatmap_data[i][j] += 1
                            self.mac_counts[i][j] += 1
                            cycle_mac_count += 1
                        
                else:  # Baseline
                    # Standard MAC operation from RTL
                    a_val = A[i][j] if j < A.shape[1] else 0
                    b_val = B[i][j] if j < B.shape[1] else 0
                    
                    if a_val != 0 and b_val != 0:
                        self.array_state[i][j] = a_val * b_val
                        self.heatmap_data[i][j] += 1
                        self.mac_counts[i][j] += 1
                        cycle_mac_count += 1
                
                # Model chainout connections from RTL
                if j > 0:
                    self.chainout[i][j] = self.chainout[i][j-1]
                
                new_states[(i, j)] = self.array_state[i][j]
        
        # Log MACs for this cycle
        self.cycle_macs.append(cycle_mac_count)
        
        # Store state history
        self.array_states_history.append(np.copy(self.array_state))
        self.heatmap_history.append(np.copy(self.heatmap_data))
        self.cycle_macs_history.append(cycle_mac_count)
        
        return new_states
    
    def get_normalized_heatmap(self):
        """Normalize heatmap data to percentage of peak utilization"""
        # For FIP and FFIP, adjust max possible MACs based on architecture
        if self.fip_method == Globals.FIP:
            # FIP can do ~50% fewer MACs
            max_possible_per_pe = self.cycle_count * 0.5
        elif self.fip_method == Globals.FFIP:
            # FFIP can do even fewer MACs
            max_possible_per_pe = self.cycle_count * 0.4
        else:
            # Baseline can do 1 MAC per cycle
            max_possible_per_pe = self.cycle_count
            
        return (self.heatmap_data / max_possible_per_pe) * 100
    
    def get_metrics(self):
        """Get performance metrics matching hardware implementation"""
        # Calculate total MACs from the counter
        total_macs = np.sum(self.mac_counts)
        
        # Calculate theoretical peak based on architecture
        if self.fip_method == Globals.FIP:
            # FIP can do ~50% fewer MACs
            theoretical_peak = self.cycle_count * self.rows * self.cols * 0.5
        elif self.fip_method == Globals.FFIP:
            # FFIP can do even fewer MACs
            theoretical_peak = self.cycle_count * self.rows * self.cols * 0.4
        else:
            # Baseline can do 1 MAC per cycle per PE
            theoretical_peak = self.cycle_count * self.rows * self.cols
        
        # Calculate utilization based on theoretical peak for each architecture
        utilization = (total_macs / theoretical_peak * 100) if theoretical_peak > 0 else 0
        
        return {
            "total_cycles": self.cycle_count,
            "total_multiplications": total_macs,
            "mults_per_mac_per_clock": total_macs / (self.rows * self.cols * self.cycle_count) if self.cycle_count > 0 else 0,
            "theoretical_peak_mults": theoretical_peak,
            "utilization": utilization,
            "macs_per_cycle": self.cycle_macs  # For logging
        }

    def get_state_at_cycle(self, cycle):
        """Get array state at a specific cycle"""
        if 0 <= cycle < len(self.array_states_history):
            return self.array_states_history[cycle]
        return None
        
    def get_heatmap_at_cycle(self, cycle):
        """Get heatmap data at a specific cycle"""
        if 0 <= cycle < len(self.heatmap_history):
            return self.heatmap_history[cycle]
        return None
        
    def get_metrics_at_cycle(self, cycle):
        """Get metrics at a specific cycle"""
        if 0 <= cycle < len(self.cycle_macs_history):
            total_macs = sum(self.cycle_macs_history[:cycle+1])
            theoretical_peak = self.calculate_theoretical_peak(cycle+1)
            utilization = (total_macs / theoretical_peak * 100) if theoretical_peak > 0 else 0
            
            return {
                "total_cycles": cycle + 1,
                "total_multiplications": total_macs,
                "mults_per_mac_per_clock": total_macs / (self.rows * self.cols * (cycle + 1)) if cycle > 0 else 0,
                "theoretical_peak_mults": theoretical_peak,
                "utilization": utilization,
                "macs_per_cycle": self.cycle_macs_history[:cycle+1]
            }
        return None
        
    def calculate_theoretical_peak(self, cycles):
        """Calculate theoretical peak MACs for given number of cycles"""
        if self.fip_method == Globals.FIP:
            return cycles * self.rows * self.cols * 0.5
        elif self.fip_method == Globals.FFIP:
            return cycles * self.rows * self.cols * 0.4
        else:
            return cycles * self.rows * self.cols

def main():
    st.title("Hardware-Accurate Systolic Array Visualization")
    
    # Show hardware configuration
    st.sidebar.header("Hardware Configuration")
    hw_config = read_hardware_config()
    st.sidebar.code(f"""
    // Hardware parameters from define.svh:
    FIP_METHOD = {hw_config['FIP_METHOD']}
    SZI = {hw_config['SZI']}
    LAYERIO_WIDTH = {hw_config['LAYERIO_WIDTH']}
    WEIGHT_WIDTH = {hw_config['WEIGHT_WIDTH']}
    """)
    
    # Configuration using actual hardware parameters
    rows = st.sidebar.slider("Number of Rows (SZI)", 2, 8, 4)
    cols = st.sidebar.slider("Number of Columns (SZJ)", 2, 8, 4)
    
    # Architecture selection using actual FIP_METHOD values
    architecture = st.sidebar.selectbox(
        "Architecture (FIP_METHOD)", 
        ["Baseline (0)", "FIP (1)", "FFIP (2)"],
        help="Select systolic array architecture from define.svh"
    )
    
    fip_method = int(architecture.split('(')[1].split(')')[0])
    architecture_name = {
        Globals.BASELINE: "Baseline",
        Globals.FIP: "FIP",
        Globals.FFIP: "FFIP"
    }[fip_method]
    
    # Show RTL implementation
    with st.expander("View RTL Implementation"):
        st.code(read_mac_array_impl(), language='systemverilog')
    
    # Create two columns for side-by-side comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{architecture_name} Architecture Details")
        if fip_method == Globals.BASELINE:
            st.markdown("""
            **Baseline Systolic Array**
            - Traditional MAC operations
            - Direct multiplication of inputs
            - 1 MAC/PE/cycle theoretical peak
            - Implementation: rtl/arith/mac_array.sv (FIP_METHOD=0)
            """)
        elif fip_method == Globals.FIP:
            st.markdown("""
            **Fast Inner Product (FIP)**
            - Pre-adds adjacent elements
            - Reduces total multiplications by ~50%
            - Higher throughput per multiplier
            - Implementation: rtl/arith/mac_array.sv (FIP_METHOD=1)
            """)
        else:
            st.markdown("""
            **Fused Fast Inner Product (FFIP)**
            - Enhanced FIP with fused operations
            - Further reduces hardware complexity
            - Maintains FIP's multiplication reduction
            - Implementation: rtl/arith/mac_array.sv (FIP_METHOD=2)
            """)
    
    # Initialize visualizer with hardware parameters
    visualizer = SystolicArrayVisualizer(rows, cols, fip_method)
    
    # Generate test matrices
    A = np.random.randint(1, 10, size=(rows, cols))
    B = np.random.randint(1, 10, size=(cols, rows))
    
    # Display input matrices
    st.subheader("Input Matrices")
    matrix_col1, matrix_col2 = st.columns(2)
    with matrix_col1:
        st.write("Matrix A:")
        st.write(A)
    with matrix_col2:
        st.write("Matrix B:")
        st.write(B)
    
    # Create containers for visualizations
    st.subheader(f"{architecture_name} Systolic Array State")
    array_chart = st.empty()
    
    st.subheader(f"{architecture_name} PE Activity Heatmap")
    heatmap_chart = st.empty()
    
    # Only create metrics container if simulation has started
    metrics_text = None
    
    if st.button("Start Hardware Simulation"):
        # Create metrics container after simulation starts
        st.subheader(f"{architecture_name} ({fip_method}) Hardware Performance Metrics")
        metrics_text = st.empty()
        
        # Create container for MACs per cycle graph
        st.subheader("MACs per Cycle")
        macs_chart = st.empty()
        
        # Run simulation for exactly 20 cycles
        for cycle in range(20):
            visualizer.simulate_cycle(A, B)
            
            # Get state at current cycle
            current_state = visualizer.get_state_at_cycle(cycle)
            current_heatmap = visualizer.get_heatmap_at_cycle(cycle)
            current_metrics = visualizer.get_metrics_at_cycle(cycle)
            
            if current_state is not None:
                # Update array visualization
                fig_array = go.Figure(data=go.Heatmap(
                    z=current_state,
                    colorscale='Viridis',
                    showscale=True,
                    text=np.round(current_state, 2),
                    texttemplate="%{text}",
                    textfont={"size": 10},
                ))
                fig_array.update_layout(
                    title=f"{architecture_name} Systolic Array State (Cycle {cycle + 1})",
                    xaxis_title="Column (matches rtl/arith/mac_array.sv)",
                    yaxis_title="Row"
                )
                array_chart.plotly_chart(fig_array, use_container_width=True)
                
                # Update PE utilization heatmap
                normalized_heatmap = current_heatmap / (cycle + 1) * 100
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=normalized_heatmap,
                    colorscale='Hot',
                    showscale=True,
                    text=np.round(normalized_heatmap, 1),
                    texttemplate="%{text}%",
                    textfont={"size": 10},
                ))
                fig_heatmap.update_layout(
                    title=f"{architecture_name} PE Utilization (Cycle {cycle + 1})",
                    xaxis_title="Column",
                    yaxis_title="Row"
                )
                heatmap_chart.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Update hardware metrics
                metrics_text.markdown(f"""
                **{architecture_name} ({fip_method}) Hardware Performance Metrics**
                **Cycle {cycle + 1}**
                - Total Cycles: {current_metrics['total_cycles']}
                - Total MAC Operations: {current_metrics['total_multiplications']:.1f}
                - MACs/PE/Clock: {current_metrics['mults_per_mac_per_clock']:.2f}
                - PE Array Utilization: {current_metrics['utilization']:.1f}%
                - Theoretical Peak MACs: {current_metrics['theoretical_peak_mults']}
                """)
                
                # Add a small delay to make the animation visible
                time.sleep(0.5)
        
        # After all cycles are complete, show the final MACs per cycle graph
        final_metrics = visualizer.get_metrics_at_cycle(19)  # Get metrics for last cycle
        fig_macs = go.Figure(data=go.Scatter(
            y=final_metrics['macs_per_cycle'],
            mode='lines+markers',
            line=dict(color='white', width=2),
            marker=dict(size=8, color='red')
        ))
        fig_macs.update_layout(
            title="MAC Operations per Cycle",
            xaxis_title="Cycle",
            yaxis_title="MAC Operations",
            showlegend=False,
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='gray',
                showgrid=True,
                zeroline=True,
                zerolinecolor='white',
                color='white'
            ),
            yaxis=dict(
                gridcolor='gray',
                showgrid=True,
                zeroline=True,
                zerolinecolor='white',
                color='white'
            )
        )
        macs_chart.plotly_chart(fig_macs, use_container_width=True)

if __name__ == "__main__":
    main() 