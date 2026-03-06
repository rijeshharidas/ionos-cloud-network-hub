<p align="center">
  <img src="docs/ionos-cloud-banner.svg" alt="IONOS Cloud Network Visualizer" width="800">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <img src="https://img.shields.io/badge/Python-3.6%2B-3776AB?logo=python&logoColor=white" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/D3.js-v7-F9A03C?logo=d3dotjs&logoColor=white" alt="D3.js v7">
  <img src="https://img.shields.io/badge/Leaflet-1.9.4-199900?logo=leaflet&logoColor=white" alt="Leaflet 1.9.4">
  <img src="https://img.shields.io/badge/Zero%20Build%20Step-brightgreen" alt="Zero Build Step">
  <img src="https://img.shields.io/badge/IONOS%20Cloud-Visualizer-003D8F" alt="IONOS Cloud">
</p>

<p align="center">
  Visualize, analyze, and get AI-powered insights for your IONOS Cloud infrastructure.<br>
  From a global map of regions down to individual servers, LANs, managed services, flow logs, and billing —<br>
  with a built-in <strong>AI Cloud Assistant</strong> that understands your entire topology.
</p>

---

<p align="center">
  <a href="#ai-cloud-assistant">AI Assistant</a> &nbsp;·&nbsp;
  <a href="#key-capabilities">Key Capabilities</a> &nbsp;·&nbsp;
  <a href="#quick-start">Quick Start</a> &nbsp;·&nbsp;
  <a href="#view-modes">View Modes</a> &nbsp;·&nbsp;
  <a href="#supported-resource-types">Resources</a> &nbsp;·&nbsp;
  <a href="#keyboard-shortcuts">Shortcuts</a> &nbsp;·&nbsp;
  <a href="#architecture">Architecture</a> &nbsp;·&nbsp;
  <a href="#security">Security</a> &nbsp;·&nbsp;
  <a href="#contributing">Contributing</a>
</p>

---

### Global Map & VDC Drill-Down

[![Global Map and VDC topology drill-down](docs/visualizer.gif)](docs/visualizer.gif)

### Cross-Connect Visualization (Regional View)

[![Cross-connect visualization in regional mode](docs/cross-connect.gif)](docs/cross-connect.gif)

## AI Cloud Assistant

> *"Which servers have no firewall enabled?"* · *"Design a 3-tier web app"* · *"Export my VDC as Terraform"*

The built-in AI Cloud Assistant connects to the **IONOS AI Model Hub** and understands your full cloud context — topology, servers, LANs, databases, security posture, billing, and flow logs. Choose from **Llama 3.1 8B**, **Mistral Small 24B**, or **Llama 3.3 70B**. Press `A` to open.

The assistant has two modes, accessible via tabs:

**Assist** — Analyze your existing infrastructure. Ask about security posture, cost optimization, traffic patterns, resource inventory, or generate Terraform. Toggle the **Docs** button to ground answers in the official IONOS Cloud documentation via MCP.

**Design** — Build new architectures from natural language. Describe what you need, and the AI generates a visual draft topology on the canvas. Iterate via chat until satisfied, then export as Terraform. Quick-start templates are available for common patterns like 3-tier web apps, Kubernetes clusters, microservices, CI/CD pipelines, and more.

## Key Capabilities

### Visualization

| | | |
|:--|:--|:--|
| 🗺️ **Global Map View** — Interactive map of all IONOS DC locations with fractional zoom. Toggle DC Network backbone (AS-8560), Object Storage endpoints (S3, filterable by bucket type), or Support Contacts overlays. `G` | 🔗 **Managed Services** — Databases, VPN gateways, NFS, load balancers, K8s clusters, and Kafka on the topology with LAN connections. K8s resources get a helm badge. | 🌐 **Cross-Connect View** — All VDCs in a metro region on one canvas with PCC cross-connect lines, AZ color-coding, and hover tooltips showing billable transfer data. |
| 🖥️ **Compute View** — VM type, cores, RAM, CPU family for every server. Color-coded: cyan (dedicated), purple (vCPU), orange (Cube), rose (GPU). `C` | 📡 **IP & DNS View** — IP labels on every NIC with reverse DNS and forward DNS. Public IP blocks, DNS zones, and CDN distributions in the sidebar. `I` | 🛡️ **Highlights** — Filter by firewall, flow logs, security groups, IPv6, failover, cross connect, multi-queue, or idle VMs. Matches glow, rest fades. `H` |

### Analysis & Monitoring

| | | |
|:--|:--|:--|
| 📜 **Flow Log Explorer** — Drag-and-drop flow log files to analyze traffic. Filter by IP, port, protocol, action. Click any row to trace the path on the topology. `W` | 🔥 **Traffic Heatmap** — Color-coded halos — toggle volume (bytes), security (rejected ratio), or billing (transfer) modes. Cool blue to hot red. `X` / `B` | 💰 **Idle VM Scanner** — Queries Prometheus telemetry to find stopped-but-billed VMs and near-zero traffic servers. Results feed into the AI for cost tips. |
| 🛡️ **Security Posture** — VDC security summary with progress bars: firewall, flow logs, security groups, private LANs, IPv6. Click any metric to highlight nodes. `S` | 📊 **Live Metrics** — 1-hour throughput and packet charts for any selected server. Data from the IONOS Telemetry API, refreshed per selection. | 📈 **Data Transfer (Billable)** — Per-VDC and per-server billable transfer from the Billing API. Adaptive daily chart with auto-scaling Y-axis, region breakdown on the global map. |

### AI & Export

| | | |
|:--|:--|:--|
| 🤖 **AI Assist** — Ask about security, costs, traffic, or resources — the AI sees your full topology. Generate Terraform, toggle Docs for IONOS documentation via MCP. Voice input supported. | ✏️ **AI Design** — Describe an architecture in plain English, get a visual draft on the canvas. Iterate via chat, export as Terraform. Quick-start templates included. | 📤 **Export** — PNG, SVG, JSON, CSV, XLSX workbook, and PDF report with topology diagram and resource inventory — all from one dropdown. |

### Customization

| | | | |
|:--|:--|:--|:--|
| 🌗 **Themes** — Dark and light mode with system-preference detection. Map tiles and UI adapt seamlessly. | 🌐 **i18n** — English, German, Spanish, French. Switch from the sidebar flag dropdown. | ⭐ **Favorites** — Pin frequently used VDCs to the top of the dropdown for quick access. | 🏢 **Multi-Contract** — Reseller accounts get a contract switcher with separate data centers. |
| 🔍 **Canvas Search** — Type-ahead search with instant highlighting. Matching nodes glow, rest dims. `Ctrl+F` | 📋 **Resource Table** — Full-screen sortable table with type filter pills and CSV export. `T` | 📞 **Support Contacts** — Phone and email for 9 countries as markers on the global map. | |

## Quick Start

```bash
git clone https://github.com/rijeshharidas/ionos-cloud-network-visualizer.git
cd ionos-cloud-network-visualizer
python3 serve.py
```

**No npm, no build step, no pip install required** — just Python and a browser.

1. Enter your IONOS Cloud API token
2. The Global Map loads automatically — explore your regions
3. Click into any VDC to visualize its full network topology

<details>
<summary><strong>Docker</strong></summary>

```bash
docker build -t ionos-cloud-visualizer .
docker run -p 8080:8080 ionos-cloud-visualizer
```

Then open `http://localhost:8080` in your browser. No Python installation needed — just Docker.

</details>

<details>
<summary><strong>Installing Python</strong> (skip if you already have Python 3.6+)</summary>

### macOS

Python 3 comes pre-installed on recent macOS versions. Check with `python3 --version`.

If missing, download from <https://www.python.org/downloads/> or run `brew install python`.

### Windows

1. Download from <https://www.python.org/downloads/>
2. Run the installer — **check "Add python.exe to PATH"**
3. Use `python serve.py` (not `python3`) on Windows

Alternatively, search "Python" in the Microsoft Store.

### Linux (Ubuntu / Debian)

Usually pre-installed. If missing: `sudo apt update && sudo apt install python3`

</details>

<details>
<summary><strong>Prerequisites</strong></summary>

| Requirement | Details |
|-------------|---------|
| **Python 3.6+** | Standard library only — no pip dependencies (not required if using Docker) |
| **Modern browser** | Chrome, Firefox, Safari, or Edge |
| **IONOS Cloud API Token** | Generate at [dcd.ionos.com](https://dcd.ionos.com) under **Management > Token Manager** |
| **Docker** *(optional)* | Only if running via Docker instead of Python directly |

</details>

<details>
<summary><strong>Configuration</strong></summary>

```bash
python3 serve.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--port PORT` | `8080` | Server port (auto-increments if unavailable) |
| `--no-browser` | `false` | Don't auto-open the browser |

</details>

## View Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| 🗺️ **Global Map** | Interactive map showing all IONOS DC locations with cloud type tooltips. Active regions display as cluster bubbles. Press `G`. | Navigate multi-region infrastructure |
| 🖥️ **Single VDC** | Full force-directed topology for one data center: servers, LANs, NICs, managed services, gateways, and load balancers. | Inspect a specific data center |
| 📍 **By Location** | All VDCs in a metro region on one canvas with Private Cross Connect links visible. | See cross-VDC connections |

## Supported Resource Types

| Category | Resources |
|----------|-----------|
| **Compute** | Servers, Cube Servers, Kubernetes Node Pools |
| **Networking** | LANs, NICs, NAT Gateways, Private Cross Connects |
| **Databases** | PostgreSQL, MongoDB, MySQL, MariaDB |
| **Storage** | Network File System (NFS) |
| **Security** | VPN Gateways (WireGuard, IPSec) |
| **Load Balancing** | Application Load Balancers, Network Load Balancers |
| **Streaming** | Kafka Clusters |
| **DNS** | Public Zones, Reverse DNS Records |
| **CDN** | CDN Distributions (indicated on DNS zones) |

## Architecture

Two files, zero build process:

| File | Role |
|------|------|
| **`ionos-cloud-network-visualizer.html`** | Self-contained frontend — D3.js v7 for topology, Leaflet.js v1.9.4 for maps, all CSS/JS inline |
| **`serve.py`** | Lightweight localhost CORS proxy (Python stdlib only) bridging browser requests to IONOS Cloud APIs |

```text
Browser (localhost:8080)  →  Proxy (serve.py)  →  IONOS Cloud API (*.ionos.com)
```

Your API token never leaves your machine.

<details>
<summary><strong>Supported IONOS Cloud Services</strong></summary>

| Service | API Endpoint | Scope |
|---------|--------------|-------|
| Virtual Servers | `/cloudapi/v6` | Per Data Center |
| Networks (LANs) | `/cloudapi/v6` | Per Data Center |
| Network Interfaces | `/cloudapi/v6` | Per Data Center |
| PostgreSQL | `/databases/postgresql` | Centralized |
| MongoDB | `/databases/mongodb` | Centralized |
| MySQL | `/databases/mysql` | Centralized |
| MariaDB | `mariadb.{location}.ionos.com` | Regional |
| VPN Gateway | `vpn.{location}.ionos.com` | Regional |
| Network File System | `nfs.{location}.ionos.com` | Regional |
| Kubernetes | `/cloudapi/v6` | Centralized |
| NAT Gateway | `/cloudapi/v6` | Per Data Center |
| Load Balancers | `/cloudapi/v6` | Per Data Center |
| Cross Connects | `/cloudapi/v6` | Centralized |
| Kafka | `kafka.{location}.ionos.com` | Regional |
| Cloud DNS | `dns.de-fra.ionos.com` | Centralized |
| CDN | `cdn.de-fra.ionos.com` | Centralized |
| Data Transfer | `/billing/{contract}/traffic` | Per Contract |
| Telemetry | `api.ionos.com/telemetry/api/v1` | Centralized |
| AI Model Hub | `openai.inference.de-txl.ionos.com/v1` | Centralized |
| Labels | `/cloudapi/v6/labels` | Centralized |
| IONOS Cloud Docs (MCP) | `docs.ionos.com/cloud/~gitbook/mcp` | Centralized |

</details>

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `?` or `/` | Show keyboard shortcuts help |
| `Escape` | Close panels and overlays |
| `Ctrl/Cmd+F` | Focus search bar |
| `+` / `-` | Zoom in / out |
| `F` / `R` | Reset & fit to view |
| `L` | Toggle labels |
| `I` | Toggle IP view |
| `C` | Toggle compute view |
| `H` | Toggle highlights overlay |
| `S` | Security posture overlay |
| `M` | Toggle map background |
| `T` | Resource table view |
| `W` | Flow Log Explorer |
| `X` | Traffic Heatmap |
| `B` | Data Transfer Heatmap |
| `A` | AI Cloud Assistant |
| `G` | Global map view |

## Security

| Measure | Detail |
|---------|--------|
| **Token Isolation** | Your API token never leaves your local machine. The proxy validates all requests target `*.ionos.com` only. |
| **In-Memory Storage** | Tokens live exclusively in browser memory — cleared when you close the tab. No cookies, no disk persistence. |
| **Localhost Binding** | The proxy binds to `127.0.0.1` only, preventing remote access. |
| **XSS Protection** | All user-controlled content is escaped before rendering in the DOM. |
| **AI Context Sanitization** | Infrastructure names are stripped of control characters before embedding in AI prompts. Context size is capped to stay within model token limits. |

## Contributing

We welcome contributions! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues, proposing features, and making pull requests.

## License

IONOS Cloud Network Visualizer is licensed under the [Apache License 2.0](LICENSE).

## Links

| | |
|---|---|
| **IONOS Cloud Platform** | <https://cloud.ionos.com> |
| **API Documentation** | <https://api.ionos.com/docs/cloud/v6/> |
| **GitHub Issues** | <https://github.com/rijeshharidas/ionos-cloud-network-visualizer/issues> |
| **IONOS Cloud Status** | <https://status.ionos.com> |

---

<p align="center"><strong>IONOS Cloud</strong> — Enterprise cloud infrastructure made simple.</p>
