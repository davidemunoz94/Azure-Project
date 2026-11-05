#!/usr/bin/env python3
"""Generate local cost artifacts from documented assumptions; no Azure access."""

import csv
import html
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "estimate-inputs.json").read_text())


def components(hours, nodes):
    c = CONFIG
    return {
        "compute": hours * nodes * c["vm_per_node_hour"],
        "disks": hours * nodes * c["disk_per_node_month"] / c["monthly_hours"],
        "public_ip": hours * c["public_ip_per_hour"],
        "lb_allowance": math.ceil(hours) * c["load_balancer_rule_allowance_per_hour"],
        "registry": max(c["registry_minimum_days_for_planning"], hours / 24) * c["registry_per_day"],
        "build": c["build_count"] * c["build_vcpus"] * c["build_seconds"] * c["task_per_vcpu_second"],
        "control_plane": hours * c["aks_control_plane_per_hour"],
    }


def total(hours, nodes):
    return sum(components(hours, nodes).values())


def money(value):
    return f"${value:,.2f}"


def make_svg(hours_list, title, subtitle):
    width, height = 1100, 480
    left, top, plot_width, plot_height = 100, 135, 910, 245
    nodes_list = CONFIG["node_scenarios"]
    peak = max(total(h, n) for h in hours_list for n in nodes_list)
    ceiling = math.ceil(peak * 1.16 * 2) / 2
    colors = ["#1879b5", "#d15b32"]
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(title)}</title>',
        '<desc id="desc">Estimated cost by resource lifetime for one and two AKS worker nodes. Preliminary assumptions, East US, USD. Includes one build and registry allowance; excludes taxes and transfer.</desc>',
        '<rect width="1100" height="480" fill="#f8fafc" rx="16"/>',
        '<g font-family="Arial, sans-serif" fill="#142b40">',
        f'<text x="36" y="44" font-size="26" font-weight="700">{html.escape(title)}</text>',
        f'<text x="36" y="71" font-size="15" fill="#526579">{html.escape(subtitle)}</text>',
    ]
    for idx, n in enumerate(nodes_list):
        x = 36 + idx * 170
        pieces.extend([
            f'<rect x="{x}" y="93" width="16" height="12" rx="2" fill="{colors[idx % 2]}"/>',
            f'<text x="{x + 23}" y="104" font-size="14">{n} worker node{"s" if n != 1 else ""}</text>',
        ])
    for tick in range(5):
        value = ceiling * tick / 4
        y = top + plot_height * (1 - tick / 4)
        pieces.extend([
            f'<line x1="{left}" y1="{y}" x2="{left + plot_width}" y2="{y}" stroke="#d9e2ea"/>',
            f'<text x="{left - 14}" y="{y + 5}" text-anchor="end" font-size="13">{money(value)}</text>',
        ])
    group = plot_width / len(hours_list)
    bar_width = min(48, group / (len(nodes_list) + 2))
    for i, h in enumerate(hours_list):
        mid = left + group * (i + 0.5)
        for j, n in enumerate(nodes_list):
            value = total(h, n)
            bar_height = value / ceiling * plot_height
            x = mid + (j - (len(nodes_list) - 1) / 2) * (bar_width + 9) - bar_width / 2
            y = top + plot_height - bar_height
            pieces.extend([
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" rx="4" fill="{colors[j % 2]}"><title>{h} hours, {n} nodes: {money(value)}</title></rect>',
                f'<text x="{x + bar_width / 2:.2f}" y="{y - 8:.2f}" text-anchor="middle" font-size="13" font-weight="700">{money(value)}</text>',
            ])
        pieces.append(f'<text x="{mid:.2f}" y="407" text-anchor="middle" font-size="14">{h:g} hours</text>')
    pieces.extend([
        '<text x="36" y="440" font-size="13" fill="#526579">Resource lifetime includes provisioning and cleanup. One-node cloud configuration verified.</text>',
        '<text x="36" y="461" font-size="13" fill="#526579">Includes one build, minimum one registry day for planning, and Standard LB rule estimate. Excludes tax and data transfer.</text>',
        '</g></svg>',
    ])
    return "\n".join(pieces)


def main():
    c = CONFIG
    hours_list = c["hour_scenarios"]
    nodes_list = c["node_scenarios"]
    rows = []
    for hours in hours_list:
        for nodes in nodes_list:
            detail = components(hours, nodes)
            rows.append({"hours": hours, "nodes": nodes,
                         **{key: f"{value:.6f}" for key, value in detail.items()},
                         "total_usd": f"{sum(detail.values()):.6f}"})
    with (HERE / "cost-scenarios.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    table_lines = [
        "# Calculated scenarios", "",
        "East US / USD; starter specifies one node; two nodes shown for comparison. Actual one-node settings verified. Includes one build and at least one registry day for planning. Excludes taxes and transfer.", "",
        "| Resource lifetime | " + " | ".join(f"{n} node{'s' if n != 1 else ''}" for n in nodes_list) + " |",
        "| --- | " + " | ".join("---:" for _ in nodes_list) + " |",
    ]
    table_body = []
    for hours in hours_list:
        label = "730 hours (month)" if hours == 730 else f"{hours:g} hours"
        values = [money(total(hours, n)) for n in nodes_list]
        table_lines.append(f"| {label} | " + " | ".join(values) + " |")
        table_body.append("<tr><th scope=\"row\">" + label + "</th>" + "".join(f"<td>{v}</td>" for v in values) + "</tr>")
    (HERE / "cost-table.md").write_text("\n".join(table_lines) + "\n")

    svg = make_svg([h for h in hours_list if h <= 24], "AKS lab: estimated session cost", f"{c['region']} · {c['currency']} · pricing checked {c['checked_date']} · preliminary")
    (HERE / "cost-chart.svg").write_text(svg + "\n")
    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Azure Project — lab cost estimate</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#edf2f7;color:#142b40;font:16px/1.55 system-ui,-apple-system,sans-serif}main{max-width:1150px;margin:32px auto;padding:0 24px 40px}h1{font-size:34px;line-height:1.2;margin:10px 0}h2{font-size:22px;margin-top:0}.eyebrow{color:#526579;font-size:13px;letter-spacing:.12em;font-weight:700}.notice{border-left:4px solid #d15b32;background:#fff5ed;padding:16px 20px;margin:24px 0}.card{background:white;border:1px solid #d9e2ea;border-radius:16px;padding:24px;margin:22px 0}.chart svg{display:block;width:100%;height:auto}.chart{padding:0;overflow:hidden}.controls{display:flex;flex-wrap:wrap;gap:20px;align-items:end}label{display:block;font-weight:600}input,select{display:block;font:inherit;padding:8px;border:1px solid #a6b7c7;border-radius:7px;max-width:180px}#amount{font-size:40px;font-weight:750;margin:18px 0 0;color:#1879b5}#detail{font-size:14px;color:#526579}table{width:100%;border-collapse:collapse}th,td{padding:11px;text-align:right;border-bottom:1px solid #d9e2ea}th:first-child{text-align:left}thead{background:#f3f7fa}a{color:#126b9d}.small{font-size:14px;color:#526579}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.grid .card{margin:0}ul{padding-left:22px}@media(max-width:700px){.grid{grid-template-columns:1fr}main{padding:0 12px}h1{font-size:28px}.card{padding:16px}}
</style></head><body><main>
<div class="eyebrow">AZURE PROJECT · COST PLANNING</div>
<h1>Know the lab cost before deployment</h1>
<p>AKS troubleshooting lab · __REGION__ · __CURRENCY__ · __DATE__</p>
<div class="notice"><strong>Starter inspected: one node, AKS Free, ACR Basic.</strong> Two nodes are shown for comparison. Actual disk, networking and two-CPU build verified. Model retains a five-minute build allowance. Standard load-balancer rate and one outbound rule verified. Deployment and cleanup status are recorded in the lab journal.</div>
<section class="card chart" aria-label="Cost chart">__SVG__</section>
<div class="grid"><section class="card"><h2>Plan a session</h2>
<div class="controls"><label>Resource lifetime, hours<input id="hours" type="number" value="2" min="0.25" max="8760" step="0.25"></label><label>Worker nodes<select id="nodes">__OPTIONS__</select></label></div>
<p id="amount" aria-live="polite"></p><p id="detail"></p><noscript><p>Enable JavaScript for the calculator. The chart and scenario table work without it.</p></noscript>
<p class="small">Count provisioning and deletion time. Changing inputs here only changes this local estimate; it does not change or create Azure resources.</p></section>
<section class="card"><h2>Time matters more than activity</h2><p>A first session can fit within a $1–$2 planning allowance under these assumptions. Reserving $3 gives room for retries.</p><p>A running month is approximately <strong>__MONTH1__–__MONTH2__</strong>. Closing your terminal does not delete the cluster.</p><p class="small">These estimates are not a spending cap. Added resources, longer runtime or different settings can exceed them.</p></section></div>
<section class="card"><h2>Compare resource lifetimes</h2><table><thead><tr><th scope="col">Lifetime</th>__HEADERS__</tr></thead><tbody>__ROWS__</tbody></table></section>
<section class="card"><h2>What the model includes</h2><ul>__LINEITEMS__</ul><p>Excludes taxes, network data processing and transfer, excess registry storage, surge nodes, extra builds, monitoring, NAT Gateway and paid AKS tiers.</p><p class="small">Verified Azure retail meter evidence and open assumptions: <a href="ESTIMATE.md">estimate report</a> · <a href="retail-price-evidence.json">pricing evidence</a> · <a href="cost-scenarios.csv">CSV</a> · <a href="../PROJECT-PLAN.md">lab plan</a></p></section>
<p class="small">Sources: <a href="https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices">Azure retail pricing</a> · <a href="https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html">official lab</a>. Starter configuration inspected; actual one-node settings verified; resource status is in the lab journal.</p>
</main><script>
const cfg=__CONFIG__;
function update(){
 const h=Number(document.getElementById('hours').value),n=Number(document.getElementById('nodes').value);
 const amount=document.getElementById('amount'),detail=document.getElementById('detail');
 if(!Number.isFinite(h)||h<0.25||h>8760){amount.textContent='Enter 0.25–8,760 hours';detail.textContent='';return;}
 const compute=h*n*cfg.vm_per_node_hour,disks=h*n*cfg.disk_per_node_month/cfg.monthly_hours;
 const network=h*cfg.public_ip_per_hour+Math.ceil(h)*cfg.load_balancer_rule_allowance_per_hour;
 const registry=Math.max(cfg.registry_minimum_days_for_planning,h/24)*cfg.registry_per_day;
 const build=cfg.build_count*cfg.build_vcpus*cfg.build_seconds*cfg.task_per_vcpu_second;
 const control=h*cfg.aks_control_plane_per_hour;
 const usd=v=>v.toLocaleString('en-US',{style:'currency',currency:'USD'});
 amount.textContent=usd(compute+disks+network+registry+build+control);
 detail.textContent=`Compute ${usd(compute)} · disks ${usd(disks)} · networking allowance ${usd(network)} · registry ${usd(registry)} · builds ${usd(build)} · control plane ${usd(control)}`;
}
document.getElementById('hours').addEventListener('input',update);document.getElementById('nodes').addEventListener('change',update);update();
</script></body></html>
"""
    items = [
        f"{c['vm_sku']} Linux compute: ${c['vm_per_node_hour']:g} per node-hour.",
        f"One assumed {c['disk_sku']} OS disk per node: {money(c['disk_per_node_month'])} per {c['monthly_hours']}-hour month.",
        f"Registry tier {c['registry_tier']}: ${c['registry_per_day']:g}/day, with {c['registry_minimum_days_for_planning']} day(s) allowed for short sessions.",
        f"{c['build_count']} build(s), {c['build_vcpus']} vCPUs, {c['build_seconds']} seconds each: {money(components(1, 1)['build'])}.",
        f"One public IPv4: ${c['public_ip_per_hour']:g}/hour; provisional LB rule allowance: ${c['load_balancer_rule_allowance_per_hour']:g}/hour, rounded up to whole hours.",
        f"AKS tier {c['aks_tier']}: ${c['aks_control_plane_per_hour']:g}/hour.",
    ]
    replacements = {
        "__REGION__": html.escape(c['region']),
        "__CURRENCY__": html.escape(c['currency']),
        "__DATE__": html.escape(c['checked_date']),
        "__LINEITEMS__": "".join(f"<li>{html.escape(item)}</li>" for item in items),
        "__SVG__": svg,
        "__OPTIONS__": "".join(f'<option value="{n}">{n} node{"s" if n != 1 else ""}</option>' for n in nodes_list),
        "__HEADERS__": "".join(f'<th scope="col">{n} node{"s" if n != 1 else ""}</th>' for n in nodes_list),
        "__ROWS__": "".join(table_body),
        "__MONTH1__": money(total(730, nodes_list[0])),
        "__MONTH2__": money(total(730, nodes_list[-1])),
        "__CONFIG__": json.dumps(c).replace("<", "\\u003c"),
    }
    for token, value in replacements.items():
        page = page.replace(token, value)
    (HERE / "cost-chart.html").write_text(page)
    print("Generated HTML, SVG, CSV, and Markdown cost artifacts.")
    print("\n".join(table_lines[4:]))


if __name__ == "__main__":
    main()
