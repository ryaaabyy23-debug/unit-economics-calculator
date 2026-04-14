import dash
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import json
import os
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# ── Colors ────────────────────────────────────────────────────────────────────
BG       = "#0F0F0F"
CARD     = "#1F1F1F"
BORDER   = "#2A2A2A"
INPUT_BG = "#2A2A2A"
TEXT     = "#FFFFFF"
TEXT_DIM = "#8A8A8A"
GREEN    = "#D0F3AF"
BLUE     = "#C8E9FA"
PINK     = "#FFC8E4"

DATA_FILE = "data/scenarios.json"

# ── Data helpers ──────────────────────────────────────────────────────────────
def load_scenarios():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_scenarios(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── UI helpers ────────────────────────────────────────────────────────────────
def num_input(id, label, value, step=1.0):
    return html.Div([
        html.Label(label, style={"color": TEXT_DIM, "fontSize": "12px",
                                  "marginBottom": "6px", "display": "block"}),
        html.Div([
            html.Button("−", id=f"{id}-minus", n_clicks=0, style={
                "backgroundColor": INPUT_BG, "color": TEXT,
                "border": f"1px solid {BORDER}", "borderRadius": "8px 0 0 8px",
                "padding": "8px 14px", "cursor": "pointer", "fontSize": "16px"
            }),
            dcc.Input(id=id, type="number", value=value, step=step, debounce=True, style={
                "backgroundColor": INPUT_BG, "color": TEXT,
                "border": f"1px solid {BORDER}", "borderLeft": "none", "borderRight": "none",
                "padding": "8px 12px", "width": "100%", "textAlign": "center", "fontSize": "14px"
            }),
            html.Button("+", id=f"{id}-plus", n_clicks=0, style={
                "backgroundColor": INPUT_BG, "color": TEXT,
                "border": f"1px solid {BORDER}", "borderRadius": "0 8px 8px 0",
                "padding": "8px 14px", "cursor": "pointer", "fontSize": "16px"
            }),
        ], style={"display": "flex"})
    ], style={"marginBottom": "14px"})

def metric_card(label, value, pct, color):
    return html.Div([
        html.P(label, style={"color": TEXT_DIM, "fontSize": "11px",
                              "margin": "0 0 6px 0", "lineHeight": "1.4"}),
        html.P(value, style={"color": color, "fontSize": "28px",
                              "fontWeight": "700", "margin": "0 0 6px 0"}),
        html.Span(f"↑ {pct}", style={
            "backgroundColor": f"{color}22", "color": color,
            "borderRadius": "20px", "padding": "2px 10px",
            "fontSize": "12px", "fontWeight": "600"
        }),
    ], style={
        "backgroundColor": f"{color}15", "border": f"1px solid {color}44",
        "borderRadius": "12px", "padding": "16px", "flex": "1"
    })

def card(children, extra_style=None):
    s = {"backgroundColor": CARD, "borderRadius": "16px",
         "padding": "20px", "marginBottom": "16px"}
    if extra_style:
        s.update(extra_style)
    return html.Div(children, style=s)

def section_title(text):
    return html.H3(text, style={"color": TEXT, "fontSize": "16px",
                                 "fontWeight": "600", "margin": "0 0 16px 0"})

def table_header(*cols):
    return html.Thead(html.Tr([
        html.Th(c, style={"color": TEXT_DIM, "padding": "6px 12px",
                           "textAlign": "right" if i > 0 else "left",
                           "fontSize": "12px", "fontWeight": "500"})
        for i, c in enumerate(cols)
    ]))

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div([

    # ── Header ────────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Span("🧮", style={"fontSize": "24px", "marginRight": "12px"}),
            html.Div([
                html.H1("Unit Economics", style={"color": TEXT, "fontSize": "20px",
                                                  "fontWeight": "700", "margin": "0"}),
                html.P("Per order & monthly analysis", style={"color": TEXT_DIM,
                                                               "fontSize": "12px", "margin": "0"}),
            ])
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Button([
                "History ",
                html.Span(id="history-count", children="0", style={
                    "backgroundColor": "#333", "borderRadius": "20px",
                    "padding": "1px 8px", "fontSize": "11px", "marginLeft": "4px"
                })
            ], id="history-btn", n_clicks=0, style={
                "backgroundColor": CARD, "color": TEXT, "border": f"1px solid {BORDER}",
                "borderRadius": "8px", "padding": "8px 16px", "cursor": "pointer",
                "fontSize": "13px", "marginRight": "8px"
            }),
            html.Button("Save Scenario", id="save-btn", n_clicks=0, style={
                "backgroundColor": CARD, "color": TEXT, "border": f"1px solid {BORDER}",
                "borderRadius": "8px", "padding": "8px 16px", "cursor": "pointer",
                "fontSize": "13px", "marginRight": "8px"
            }),
            dcc.Dropdown(
                id="currency", options=[
                    {"label": "$ USD", "value": "$"},
                    {"label": "€ EUR", "value": "€"},
                    {"label": "£ GBP", "value": "£"},
                ], value="$", clearable=False,
                style={"minWidth": "100px", "fontSize": "13px"}
            ),
        ], style={"display": "flex", "alignItems": "center"}),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "marginBottom": "24px", "paddingBottom": "20px", "borderBottom": f"1px solid {BORDER}"
    }),

    # ── Save modal ─────────────────────────────────────────────────────────────
    html.Div(id="save-modal", style={"display": "none"}, children=[
        card([
            html.H4("Save Scenario", style={"color": TEXT, "marginBottom": "12px"}),
            dcc.Input(id="scenario-name", type="text", placeholder="e.g. My Store Q2 2026",
                      style={"backgroundColor": INPUT_BG, "color": TEXT,
                             "border": f"1px solid {BORDER}", "borderRadius": "8px",
                             "padding": "8px 12px", "width": "100%",
                             "marginBottom": "12px", "fontSize": "14px"}),
            html.Div([
                html.Button("Save", id="confirm-save-btn", n_clicks=0, style={
                    "backgroundColor": GREEN, "color": BG, "border": "none",
                    "borderRadius": "8px", "padding": "8px 20px",
                    "cursor": "pointer", "fontWeight": "700", "marginRight": "8px"
                }),
                html.Button("Cancel", id="cancel-save-btn", n_clicks=0, style={
                    "backgroundColor": INPUT_BG, "color": TEXT,
                    "border": f"1px solid {BORDER}", "borderRadius": "8px",
                    "padding": "8px 20px", "cursor": "pointer"
                }),
            ]),
            html.Div(id="save-status", style={"marginTop": "8px"}),
        ], extra_style={"maxWidth": "440px", "margin": "0 auto 24px auto",
                        "border": f"1px solid {BORDER}"})
    ]),

    # ── History panel ──────────────────────────────────────────────────────────
    html.Div(id="history-panel", style={"display": "none"}, children=[
        html.Div(id="history-list")
    ]),

    # ── Main 2-col grid ────────────────────────────────────────────────────────
    html.Div([

        # LEFT
        html.Div([
            card([
                section_title("Unit/Order gross margin"),
                num_input("aov", "AOV (average order value)", 320.0),
                html.P("Variable costs per order", style={"color": TEXT, "fontWeight": "600",
                                                           "fontSize": "13px", "marginBottom": "12px"}),
                html.Div([
                    html.Div([num_input("cogs", "Landed COGS", 160.0)], style={"flex": "1", "marginRight": "8px"}),
                    html.Div([num_input("processing", "Processing (fees)", 4.0, 0.01)], style={"flex": "1"}),
                ], style={"display": "flex"}),
                html.Div([
                    html.Div([num_input("returns", "Returns (cost per order)", 0.0)], style={"flex": "1", "marginRight": "8px"}),
                    html.Div([num_input("tpl", "3PL", 0.0)], style={"flex": "1"}),
                ], style={"display": "flex"}),
                html.Div([
                    html.Div([num_input("package", "Package", 0.0)], style={"flex": "1", "marginRight": "8px"}),
                    html.Div([num_input("label", "Label", 0.0)], style={"flex": "1"}),
                ], style={"display": "flex"}),
            ]),

            card([
                section_title("Margins per order"),
                num_input("ncac", "nCAC (marketing per order)", 75.0),
                html.Div(id="metric-cards", style={"display": "flex", "gap": "10px", "marginTop": "8px"}),
            ]),

            card([
                section_title("Cost breakdown per order"),
                html.Div(id="cost-table"),
            ]),

        ], style={"flex": "1", "marginRight": "16px"}),

        # RIGHT
        html.Div([
            card([
                section_title("Monthly view (orders)"),
                num_input("new-orders", "New orders", 135, 1),
                num_input("returning-orders", "Returning orders", 10, 1),
                html.Div(id="orders-summary", style={"display": "flex", "gap": "12px", "marginTop": "4px"}),
            ]),

            card([
                section_title("Contribution margin (monthly)"),
                html.Div(id="monthly-cm-table"),
            ]),

            card([
                section_title("Operating margin (monthly)"),
                num_input("marketing", "Marketing spend (monthly)", 10000.0),
                num_input("warehouse", "Warehouse", 0.0),
                num_input("payroll", "Payroll", 1000.0),
                num_input("software", "Software", 500.0),
                num_input("content", "Content", 620.0),
            ]),

            card([
                html.P("Operating profit (monthly)", style={"color": TEXT_DIM,
                                                             "fontSize": "13px", "margin": "0 0 8px 0"}),
                html.Div(id="op-profit"),
            ]),

        ], style={"flex": "1"}),

    ], style={"display": "flex"}),

    # ── Forecast ───────────────────────────────────────────────────────────────
    card([
        section_title("📈 Forecast"),
        html.Div([
            html.Div([
                html.Label("Months to forecast", style={"color": TEXT_DIM, "fontSize": "12px",
                                                         "marginBottom": "8px", "display": "block"}),
                dcc.Slider(id="forecast-months", min=1, max=12, step=1, value=6,
                           marks={i: {"label": str(i), "style": {"color": TEXT_DIM}} for i in range(1, 13)},
                           tooltip={"placement": "bottom", "always_visible": False}),
            ], style={"flex": "2", "marginRight": "32px"}),
            html.Div([
                html.Label("Monthly order growth %", style={"color": TEXT_DIM, "fontSize": "12px",
                                                              "marginBottom": "6px", "display": "block"}),
                dcc.Input(id="growth-rate", type="number", value=10, step=1, style={
                    "backgroundColor": INPUT_BG, "color": TEXT,
                    "border": f"1px solid {BORDER}", "borderRadius": "8px",
                    "padding": "8px 12px", "width": "100%", "fontSize": "14px"
                }),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "alignItems": "flex-end", "marginBottom": "20px"}),
        dcc.Graph(id="forecast-chart", config={"displayModeBar": False}),
    ]),

    dcc.Store(id="store"),

], style={
    "backgroundColor": BG, "minHeight": "100vh",
    "padding": "32px", "fontFamily": "system-ui, -apple-system, sans-serif",
    "maxWidth": "1400px", "margin": "0 auto"
})


# ── Main calc callback ────────────────────────────────────────────────────────
@callback(
    Output("metric-cards", "children"),
    Output("cost-table", "children"),
    Output("orders-summary", "children"),
    Output("monthly-cm-table", "children"),
    Output("op-profit", "children"),
    Output("history-count", "children"),
    [Input(x, "value") for x in
     ["aov","cogs","processing","returns","tpl","package","label",
      "ncac","new-orders","returning-orders","marketing","warehouse",
      "payroll","software","content","currency"]],
)
def update_all(aov, cogs, processing, returns, tpl, package, label, ncac,
               new_orders, returning_orders, marketing, warehouse, payroll, software, content, cur):

    cur = cur or "$"
    aov = float(aov or 0); cogs = float(cogs or 0)
    processing = float(processing or 0); returns = float(returns or 0)
    tpl = float(tpl or 0); package = float(package or 0); label = float(label or 0)
    ncac = float(ncac or 0); new_orders = int(new_orders or 0)
    returning_orders = int(returning_orders or 0); marketing = float(marketing or 0)
    warehouse = float(warehouse or 0); payroll = float(payroll or 0)
    software = float(software or 0); content = float(content or 0)

    total_var = cogs + processing + returns + tpl + package + label
    cm = aov - total_var
    cm_pct = cm / aov * 100 if aov else 0
    ncac_pct = ncac / aov * 100 if aov else 0
    om = cm - ncac
    om_pct = om / aov * 100 if aov else 0

    cards = [
        metric_card("Contribution\nmargin", f"{cur}{cm:,.0f}", f"{cm_pct:.2f}%", PINK),
        metric_card("nCAC", f"{cur}{ncac:,.0f}", f"{ncac_pct:.2f}%", BLUE),
        metric_card("Operating\nmargin per order", f"{cur}{om:,.0f}", f"{om_pct:.2f}%", GREEN),
    ]

    cost_rows = [("Landed COGS", cogs), ("Returns", returns), ("Package", package),
                 ("Processing", processing), ("3PL", tpl), ("Labels", label)]
    cost_table = html.Table([
        table_header("Name", "Amount", "% of AOV"),
        html.Tbody([
            html.Tr([
                html.Td(n, style={"color": TEXT, "padding": "8px 12px", "fontSize": "13px"}),
                html.Td(f"{cur}{v:.2f}", style={"color": TEXT, "padding": "8px 12px",
                                                  "textAlign": "right", "fontSize": "13px"}),
                html.Td(f"{v/aov*100:.2f}%" if aov else "—",
                        style={"color": TEXT_DIM, "padding": "8px 12px",
                               "textAlign": "right", "fontSize": "13px"}),
            ], style={"borderTop": f"1px solid {BORDER}"})
            for n, v in cost_rows
        ])
    ], style={"width": "100%", "borderCollapse": "collapse"})

    total_orders = new_orders + returning_orders
    ret_share = returning_orders / total_orders * 100 if total_orders else 0
    orders_summary = [
        html.Div([
            html.P("Total orders", style={"color": TEXT_DIM, "fontSize": "12px", "margin": "0 0 2px 0"}),
            html.P(f"{total_orders:,}", style={"color": TEXT, "fontSize": "24px", "fontWeight": "700", "margin": "0"}),
        ], style={"backgroundColor": INPUT_BG, "borderRadius": "10px", "padding": "12px 16px", "flex": "1"}),
        html.Div([
            html.P("Returning share", style={"color": TEXT_DIM, "fontSize": "12px", "margin": "0 0 2px 0"}),
            html.P(f"{ret_share:.2f}%", style={"color": TEXT, "fontSize": "24px", "fontWeight": "700", "margin": "0"}),
        ], style={"backgroundColor": INPUT_BG, "borderRadius": "10px", "padding": "12px 16px", "flex": "1"}),
    ]

    revenue_m = aov * total_orders
    cm_rows = [("Revenue", revenue_m), ("COGS", cogs * total_orders),
               ("Returns", returns * total_orders), ("Processing", processing * total_orders),
               ("Package", package * total_orders), ("3PL", tpl * total_orders),
               ("Labels", label * total_orders), ("Contribution", cm * total_orders)]
    monthly_table = html.Table([
        table_header("Name", "Amount"),
        html.Tbody([
            html.Tr([
                html.Td(n, style={"color": GREEN if n == "Contribution" else TEXT,
                                   "padding": "8px 12px", "fontSize": "13px",
                                   "fontWeight": "700" if n == "Contribution" else "normal"}),
                html.Td(f"{cur}{v:,.0f}", style={"color": GREEN if n == "Contribution" else TEXT,
                                                   "padding": "8px 12px", "textAlign": "right",
                                                   "fontSize": "13px",
                                                   "fontWeight": "700" if n == "Contribution" else "normal"}),
            ], style={"borderTop": f"1px solid {BORDER}"})
            for n, v in cm_rows
        ])
    ], style={"width": "100%", "borderCollapse": "collapse"})

    fixed = warehouse + payroll + software + content
    op = cm * total_orders - marketing - fixed
    op_pct = op / revenue_m * 100 if revenue_m else 0
    oc = GREEN if op_pct > 10 else "#F5A623" if op_pct > 0 else "#FF4D4D"
    op_card = html.Div([
        html.P(f"{cur}{op:,.0f}", style={"color": oc, "fontSize": "36px", "fontWeight": "700", "margin": "0 0 6px 0"}),
        html.Span(f"↑ {op_pct:.2f}%", style={"backgroundColor": f"{oc}22", "color": oc,
                                               "borderRadius": "20px", "padding": "2px 10px",
                                               "fontSize": "13px", "fontWeight": "600"}),
    ])

    return cards, cost_table, orders_summary, monthly_table, op_card, str(len(load_scenarios()))


# ── Save modal toggle ─────────────────────────────────────────────────────────
@callback(
    Output("save-modal", "style"),
    Input("save-btn", "n_clicks"),
    Input("cancel-save-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_modal(s, c):
    from dash import ctx
    return {"display": "block"} if ctx.triggered_id == "save-btn" else {"display": "none"}


# ── Save scenario ─────────────────────────────────────────────────────────────
@callback(
    Output("save-status", "children"),
    Output("store", "data"),
    Input("confirm-save-btn", "n_clicks"),
    State("scenario-name", "value"),
    State("aov", "value"), State("cogs", "value"), State("processing", "value"),
    State("returns", "value"), State("tpl", "value"), State("package", "value"),
    State("label", "value"), State("ncac", "value"), State("new-orders", "value"),
    State("returning-orders", "value"), State("marketing", "value"),
    State("warehouse", "value"), State("payroll", "value"),
    State("software", "value"), State("content", "value"),
    prevent_initial_call=True,
)
def save_scenario(_, name, aov, cogs, processing, returns, tpl, package, label,
                  ncac, new_orders, ret_orders, marketing, warehouse, payroll, software, content):
    if not name:
        return html.P("⚠️ Enter a name", style={"color": "#F5A623", "fontSize": "13px"}), dash.no_update
    s = {
        "id": int(datetime.now().timestamp() * 1000),
        "name": name,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "inputs": {"aov": aov, "cogs": cogs, "processing": processing, "returns": returns,
                   "tpl": tpl, "package": package, "label": label, "ncac": ncac,
                   "new_orders": new_orders, "returning_orders": ret_orders,
                   "marketing": marketing, "warehouse": warehouse, "payroll": payroll,
                   "software": software, "content": content}
    }
    data = load_scenarios()
    data.append(s)
    save_scenarios(data)
    return html.P(f"✅ Saved: {name}", style={"color": GREEN, "fontSize": "13px"}), _


# ── History panel ─────────────────────────────────────────────────────────────
@callback(
    Output("history-panel", "style"),
    Output("history-list", "children"),
    Input("history-btn", "n_clicks"),
    State("history-panel", "style"),
    prevent_initial_call=True,
)
def toggle_history(_, style):
    if style and style.get("display") == "block":
        return {"display": "none"}, []
    data = load_scenarios()
    if not data:
        items = [html.P("No saved scenarios yet.", style={"color": TEXT_DIM, "padding": "16px"})]
    else:
        items = [
            html.Div([
                html.Div([
                    html.P(s["name"], style={"color": TEXT, "fontWeight": "600",
                                             "margin": "0 0 2px 0", "fontSize": "14px"}),
                    html.P(s["saved_at"], style={"color": TEXT_DIM, "fontSize": "12px", "margin": "0"}),
                ]),
                html.Div([
                    html.P(f"AOV: ${s['inputs'].get('aov', 0)}", style={"color": TEXT_DIM, "fontSize": "12px", "margin": "0"}),
                    html.P(f"Orders: {s['inputs'].get('new_orders', 0)}", style={"color": TEXT_DIM, "fontSize": "12px", "margin": "0"}),
                ]),
            ], style={
                "display": "flex", "justifyContent": "space-between",
                "backgroundColor": INPUT_BG, "borderRadius": "10px",
                "padding": "12px 16px", "marginBottom": "8px",
                "border": f"1px solid {BORDER}"
            })
            for s in reversed(data)
        ]
    panel = html.Div([
        html.H4("Saved Scenarios", style={"color": TEXT, "marginBottom": "16px"}),
        html.Div(items),
    ], style={"backgroundColor": CARD, "border": f"1px solid {BORDER}",
              "borderRadius": "16px", "padding": "20px", "marginBottom": "24px"})
    return {"display": "block"}, [panel]


# ── Forecast chart ────────────────────────────────────────────────────────────
@callback(
    Output("forecast-chart", "figure"),
    [Input(x, "value") for x in
     ["aov","cogs","processing","returns","tpl","package","label","ncac",
      "new-orders","marketing","warehouse","payroll","software","content",
      "forecast-months","growth-rate","currency"]],
)
def update_forecast(aov, cogs, processing, returns, tpl, package, label, ncac,
                    new_orders, marketing, warehouse, payroll, software, content,
                    months, growth_rate, cur):
    cur = cur or "$"
    aov = float(aov or 0); cogs = float(cogs or 0)
    processing = float(processing or 0); returns = float(returns or 0)
    tpl = float(tpl or 0); package = float(package or 0); label = float(label or 0)
    ncac = float(ncac or 0); new_orders = int(new_orders or 0)
    marketing = float(marketing or 0); warehouse = float(warehouse or 0)
    payroll = float(payroll or 0); software = float(software or 0); content = float(content or 0)
    months = int(months or 6); growth = float(growth_rate or 0) / 100

    cm = aov - (cogs + processing + returns + tpl + package + label)
    fixed = warehouse + payroll + software + content

    labels, revenues, profits, margins = [], [], [], []
    now = datetime.now()
    for i in range(months):
        m = (now.month + i - 1) % 12 + 1
        y = now.year + (now.month + i - 1) // 12
        labels.append(datetime(y, m, 1).strftime("%b %Y"))
        o = int(new_orders * (1 + growth) ** i)
        rev = aov * o
        prof = cm * o - marketing - fixed
        revenues.append(rev)
        profits.append(prof)
        margins.append(prof / rev * 100 if rev else 0)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=revenues, name="Revenue", marker_color=BLUE, opacity=0.7))
    fig.add_trace(go.Bar(x=labels, y=profits, name="Operating Profit",
                         marker_color=[GREEN if p > 0 else "#FF4D4D" for p in profits]))
    fig.add_trace(go.Scatter(x=labels, y=margins, name="Margin %", yaxis="y2",
                             mode="lines+markers", line={"color": PINK, "width": 2},
                             marker={"size": 6}))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font={"color": TEXT, "family": "system-ui"},
        barmode="group", height=320,
        legend={"orientation": "h", "y": -0.2, "font": {"color": TEXT}},
        xaxis={"showgrid": False, "linecolor": BORDER},
        yaxis={"showgrid": False, "linecolor": BORDER, "title": f"Amount ({cur})"},
        yaxis2={"overlaying": "y", "side": "right", "showgrid": False,
                "title": "Margin %", "ticksuffix": "%"},
        margin={"l": 20, "r": 60, "t": 20, "b": 60},
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
