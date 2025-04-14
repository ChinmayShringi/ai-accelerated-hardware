# AI Accelerator Simulator: Visualizing Algebraic Enhancements in Systolic Arrays

A fully interactive and educational platform to visualize, simulate, and analyze AI hardware acceleration techniques using advanced systolic array architectures. This project was developed as part of an independent research submission and explores the inner workings of deep learning accelerator systems through both visual and performance perspectives.

---

## 🚀 Project Description

This simulator provides:
- Cycle-accurate visualization of matrix operations on hardware-like systolic arrays
- Interactive comparisons between multiple accelerator designs (Baseline, FIP, FFIP)
- Real-time calculation of MAC utilization, throughput, and performance bottlenecks
- A pedagogical and research-friendly frontend for architectural exploration

Unlike conventional hardware simulators or toolchains, this tool prioritizes clarity, traceability, and hardware behavior explanation — ideal for instructional purposes or architecture validation.

---

### Results Preview

![image](https://github.com/user-attachments/assets/9b4439d8-aa96-42a5-91fa-0f78b05aa12b)
![image](https://github.com/user-attachments/assets/9908560c-ca32-47dd-85ba-a59d3ecf8b4e)
![image](https://github.com/user-attachments/assets/14535256-e78a-4e8d-95ad-266cbabc01cd)

---

## 📐 Architecture Modes

### 🔹 Baseline Architecture
- Traditional MAC operation grid
- Direct multiplication per PE
- Reference model to compare optimized architectures
- RTL: `rtl/arith/mac_array.sv` (`FIP_METHOD=0`)

📊 Metrics:
- MACs: 1280
- MACs/PE/Clock: 1.00
- Utilization: 100.0%
- Peak MACs: 1280

### 🔸 Fast Inner Product (FIP)
- Pre-adds adjacent elements to halve multiplication count
- Doubles throughput per multiplier with fixed PE grid
- RTL: `rtl/arith/mac_array.sv` (`FIP_METHOD=1`)

📊 Metrics:
- MACs: 1280
- MACs/PE/Clock: 1.00
- Utilization: 200.0%
- Peak MACs: 640

### 🔺 Fused Fast Inner Product (FFIP)
- Extends FIP with fused ops to reduce intermediate logic
- Most compact architecture with high performance-per-area
- RTL: `rtl/arith/mac_array.sv` (`FIP_METHOD=2`)

📊 Metrics:
- MACs: 1280
- MACs/PE/Clock: 1.00
- Utilization: 250.0%
- Peak MACs: 512

---

## 🧠 Visualization Features

### Configuration Controls
- Choose architecture: Baseline, FIP, FFIP
- Adjust array dimensions (rows/cols)
- Load custom input matrices

### Dynamic Simulation
- Per-cycle systolic array state
- PE-level heatmap of utilization
- MACs per cycle charting

### Performance Dashboard
- Cycle count, total MACs, and throughput
- Utilization vs theoretical peak comparison
- Architecture efficiency insights

---

## 🛠️ Project Layout

```
project-root/
├── compiler/           # Simulator logic and architecture model
├── rtl/                # SystemVerilog modules (MXU, MAC arrays)
├── visualizer/         # Streamlit-based interface
├── tests/              # Verification and test scaffolds
└── utils/              # Parameter helpers and generation scripts
```

---

## 🧪 Getting Started

### Installation:
```bash
pip install -r requirements.txt
```

### Launch Visual Simulator:
```bash
streamlit run visualizer/run.py
```

### Open in browser:
```
http://localhost:8501
```

---

## 📈 Future Enhancements
- Interactive timeline slider to explore cycles
- Support for additional matrix multiplication algorithms (e.g., Winograd, Karatsuba)
- Exportable performance logs
- Support for float32/fixed16 inputs


---

### Current Chip Analysis
Detailed analysis of individual AI accelerator chips:
- [NVIDIA H200](chips/nvidia-h200.md) - Latest Hopper Architecture
- [Google TPU v5p](chips/google-tpu.md) - Cloud AI Accelerator
- [Cerebras CS-3](chips/cerebras-cs3.md) - Wafer-Scale Engine
- [Intel Gaudi3](chips/intel-gaudi3.md) - Data Center AI Accelerator
- [Apple Baltra](chips/apple-baltra.md) - In Development
- [AWS Trainium3](chips/aws-trainium.md) - Cloud Training Accelerator
- [IBM Analog](chips/ibm-analog.md) - Analog AI Chip
- [EnCharge Edge](chips/encharge-edge.md) - Edge AI Accelerator
- [Lightmatter](chips/lightmatter.md) - Photonic Computing
- [Quantum-Hybrid](chips/quantum-hybrid.md) - Research Stage

### Comparative Analysis
Cross-cutting analysis of key aspects:
- [Performance Comparison](analysis/performance-comparison.md) - Detailed metrics comparison
- [Architecture Analysis](analysis/architecture-analysis.md) - Design approaches evaluation
- [Market Impact](analysis/market-impact.md) - Industry and economic effects
- [Software Ecosystem](analysis/software-ecosystem.md) - Development environments and tools
- [Environmental Impact](analysis/environmental-impact.md) - Sustainability analysis
- [Technical Roadmap](analysis/technical-roadmap.md) - Future development trajectory
- [Deployment Strategy](analysis/deployment-strategy.md) - Implementation guidelines

## 📄 License

This simulator is developed for educational and academic research purposes. Released under the MIT License.


<!-- Keywords: AI Accelerator, Systolic Array, Deep Learning Hardware, Hardware Visualization, MAC Optimization, FIP, FFIP, GEMM, Matrix Multiplication, RTL Simulation, Architecture Design, AI Hardware Research -->

