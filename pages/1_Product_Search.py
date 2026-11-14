import streamlit as st
from utils.data_loader import load_data
# ==========================================================
# Page Config
# ==========================================================
st.set_page_config(
    page_title="Production Monitoring Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Production Monitoring Dashboard")
st.write("Production Monitoring System")
# ==========================================================
# Load Data
# ==========================================================
try:

    df = load_data()

except Exception as e:

    st.error(f"Error Loading Excel File\n\n{e}")
    st.stop()
# ==========================================================
# Search Article Number
# ==========================================================
articles = sorted(
    df["Article Number"]
    .dropna()
    .unique()
)

selected_article = st.selectbox(
    "🔍 Search Article Number",
    articles
)

# ==========================================================
# Product Status (Traffic Light)
# ==========================================================
def get_product_status(warehouse_qty, transfer_qty, nonsellable_qty,
                        plan_qty, producted_qty, packaging_qty, delivery_qty):

    # 1. Ready (green)
    if warehouse_qty >= delivery_qty:
        return "🟢", "Ready", "Ready to Deliver (Available in Warehouse)"
    if producted_qty >= delivery_qty:
        return "🟢", "Ready", "Production Completed"
    if packaging_qty >= delivery_qty:
        return "🟢", "Ready", "Packaging Completed"
    if transfer_qty >= delivery_qty:
        return "🟢", "Ready", "Transferred for Delivery"

    # 2. Shortage (red)
    if plan_qty == 0:
        return "🔴", "Shortage", "No Production Plan"
    if (plan_qty + warehouse_qty + nonsellable_qty) < delivery_qty:
        return "🔴", "Shortage", "Shortage Detected"

    # 3. Planned (white/gray)
    if plan_qty > 0 and producted_qty == 0 and packaging_qty == 0:
        return "⚪", "Planned", "Production Planned (Plan covers the required delivery)"

    # 4. In Production (yellow)
    if producted_qty > 0 or packaging_qty > 0:
        return "🟡", "In Production", "Production in Progress"

    # Fallback
    return "⚪", "Unknown", "Status Undetermined"


if selected_article:
    product_rows = df[
        df["Article Number"] == selected_article
    ]
    first_row = product_rows.iloc[0]
    status_delivery_qty = product_rows["QTY"].sum()

    status_icon, status_label, status_comment = get_product_status(
        warehouse_qty=first_row["Warehouse"],
        transfer_qty=first_row["Transfer"],
        nonsellable_qty=first_row["Nonsellable"],
        plan_qty=first_row["Plan"],
        producted_qty=first_row["producted"],
        packaging_qty=first_row["Packaging"],
        delivery_qty=status_delivery_qty
    )

    st.markdown(f"### {status_icon} Status: {status_label}")
    st.info(status_comment)
    st.markdown("---")

# ==========================================================
# Product Information
# ==========================================================
if selected_article:
    description = first_row["Description"]

    customer_names = sorted(
        product_rows["Customer name"]
        .dropna()
        .astype(str)
        .unique()
    )
    customer_text = ", ".join(customer_names)

    st.subheader(f"Article : {selected_article}")
    st.write(f"**Description :** {description}")
    st.write(f"**Customer :** {customer_text}")
    st.markdown("---")

    # ==========================================================
    # Customer Orders
    # ==========================================================
    st.subheader("Customer Orders")

    po_table = product_rows[
        [
            "po no",
            "Requested Delivery date",
            "QTY"
        ]
    ].copy()

    po_table["Requested Delivery date"] = (
        po_table["Requested Delivery date"]
        .dt.strftime("%Y-%m-%d")
    )

    po_table = po_table.sort_values(
        by="Requested Delivery date"
    )

    po_table.columns = [
        "PO Number",
        "Requested Delivery Date",
        "Delivery Quantity"
    ]

    st.dataframe(
        po_table,
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # ==========================================================
    # KPI Calculations
    # ==========================================================
    warehouse_qty = first_row["Warehouse"]
    transfer_qty = first_row["Transfer"]
    nonsellable_qty = first_row["Nonsellable"]
    plan_qty = first_row["Plan"]
    producted_qty = first_row["producted"]
    delivery_qty = product_rows["QTY"].sum()

    # ==========================================================
    # KPI Cards (Divided into 2 rows of 3 columns)
    # ==========================================================
    st.subheader("Inventory Summary")

    # ردیف اول: انبار، انتقال و غیرقابل فروش
    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        st.metric(
            "Warehouse",
            f"{warehouse_qty:,.0f}"
        )

    with row1_col2:
        st.metric(
            "Transfer",
            f"{transfer_qty:,.0f}"
        )

    with row1_col3:
        st.metric(
            "Nonsellable",
            f"{nonsellable_qty:,.0f}"
        )

    # ایجاد فاصله کوچک بین دو ردیف
    st.write("")

    # ردیف دوم: برنامه، تولید شده و کل مقدار تحویل
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        st.metric(
            "Plan",
            f"{plan_qty:,.0f}"
        )

    with row2_col2:
        st.metric(
            "Produced",
            f"{producted_qty:,.0f}"
        )

    with row2_col3:
        st.metric(
            "Delivery Quantity",
            f"{delivery_qty:,.0f}"
        )

    # ==========================================================
    # Delivery Progress
    # ==========================================================
    st.markdown("### Delivery Progress")

    if delivery_qty > 0:
        progress = transfer_qty / delivery_qty
        progress = min(progress, 1)
    else:
        progress = 0

    st.progress(progress)
    st.write(
        f"Overall Delivery Progress : {progress * 100:.1f}%"
    )

    st.markdown("---")

    # ==========================================================
    # Production Stages (Visual Flow)
    # ==========================================================
    st.subheader("Production Stages")

    stages = {
        "Packaging": first_row["Packaging"],
        "final check": first_row["final check"],
        "sorting": first_row["sorting"],
        "cutting": first_row["cutting"],
        "Print test": first_row["Print test"],
        "UV printing": first_row["UV printing"],
        "offset print": first_row["offset print"],
        "Roll-to-Sheet Offset": first_row["Roll-to-Sheet Offset"],
        "slitting": first_row["slitting"],
        "Gravure printing": first_row["Gravure printing"],
        "emboss": first_row["emboss"],
        "Simultaneous cutting and embossing": first_row["Simultaneous cutting and embossing"],
        "mix": first_row["mix"],
        "roll to roll": first_row["roll to roll"],
        "Shrink": first_row["Shrink"],
        "boresh": first_row["boresh"],
        "Back printing": first_row["Back printing"],
        "Print pass 2": first_row["Print pass 2"]
    }

    # آیکون هر مرحله تولید (در صورت نیاز می‌تونی هرکدوم رو عوض کنی)
    stage_icons = {
        "Packaging": "📦",
        "final check": "✅",
        "sorting": "🔀",
        "cutting": "✂️",
        "Print test": "🖨️",
        "UV printing": "🔆",
        "offset print": "🖨️",
        "Roll-to-Sheet Offset": "📜",
        "slitting": "🔪",
        "Gravure printing": "🖼️",
        "emboss": "🔘",
        "Simultaneous cutting and embossing": "⚙️",
        "mix": "🔄",
        "roll to roll": "🎞️",
        "Shrink": "🔥",
        "boresh": "🧵",
        "Back printing": "🔁",
        "Print pass 2": "🖨️"
    }

    stage_items = list(stages.items())

    if not stage_items:
        st.info("No production stage data available for this article.")
    else:
        def wrap_label(text, max_chars=13):
            words = text.split()
            lines = []
            current = ""
            for w in words:
                trial = (current + " " + w).strip()
                if len(trial) <= max_chars:
                    current = trial
                else:
                    if current:
                        lines.append(current)
                    current = w
            if current:
                lines.append(current)
            return lines[:2] if lines else [text]

        COLS = 6
        ICON_R = 34
        SPACING_X = 155
        SPACING_Y = 165
        MARGIN_X = 80
        MARGIN_Y = 60
        RAIL_OFFSET = ICON_R + 20
        LABEL_LINE_H = 16

        n = len(stage_items)
        rows_count = -(-n // COLS)  # ceil division

        nodes = []
        for i, (name, qty) in enumerate(stage_items):
            row = i // COLS
            pos = i % COLS
            col = pos if row % 2 == 0 else (COLS - 1 - pos)
            cx = MARGIN_X + col * SPACING_X
            cy = MARGIN_Y + row * SPACING_Y
            rail_y = cy + RAIL_OFFSET
            icon = stage_icons.get(name, "🏭")
            nodes.append({
                "cx": cx, "cy": cy, "rail_y": rail_y,
                "name": name, "qty": qty, "icon": icon, "row": row
            })

        svg_width = MARGIN_X * 2 + (min(COLS, n) - 1) * SPACING_X + ICON_R
        svg_height = MARGIN_Y + (rows_count - 1) * SPACING_Y + RAIL_OFFSET + 3 * LABEL_LINE_H + 40

        # مسیر خط رابط بین مراحل (اتصال منحنی مثل نمونه)
        path_d = f"M {nodes[0]['cx']} {nodes[0]['rail_y']} "
        for i in range(1, len(nodes)):
            prev = nodes[i - 1]
            curr = nodes[i]
            if curr["row"] == prev["row"]:
                path_d += f"L {curr['cx']} {curr['rail_y']} "
            else:
                bulge = 1 if prev["row"] % 2 == 0 else -1
                hook = SPACING_X * 0.55
                ctrl_x = prev["cx"] + bulge * hook
                path_d += (
                    f"C {ctrl_x} {prev['rail_y']}, "
                    f"{ctrl_x} {curr['rail_y']}, "
                    f"{curr['cx']} {curr['rail_y']} "
                )

        nodes_svg = ""
        for node in nodes:
            cx, cy, rail_y = node["cx"], node["cy"], node["rail_y"]
            label_lines = wrap_label(node["name"])

            nodes_svg += f"""
            <line x1="{cx}" y1="{cy + ICON_R}" x2="{cx}" y2="{rail_y}"
                  stroke="#c9a24b" stroke-width="2" />
            <circle cx="{cx}" cy="{rail_y}" r="5" fill="#d9a441" />
            <circle cx="{cx}" cy="{cy}" r="{ICON_R}"
                    fill="#ffffff" stroke="#a85751" stroke-width="2.5" />
            <text x="{cx}" y="{cy + 10}" font-size="26" text-anchor="middle">{node['icon']}</text>
            <text x="{cx}" y="{rail_y + 22}" font-size="13" font-weight="700"
                  fill="#1f2937" text-anchor="middle">{node['qty']:,.0f}</text>
            """
            for j, line in enumerate(label_lines):
                nodes_svg += (
                    f'<text x="{cx}" y="{rail_y + 40 + j * LABEL_LINE_H}" '
                    f'font-size="12" fill="#555555" text-anchor="middle">{line}</text>'
                )

        stage_svg = f"""
        <div style="overflow-x:auto; padding:10px 0;">
        <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}"
             xmlns="http://www.w3.org/2000/svg">
            <path d="{path_d}" fill="none" stroke="#d9a441" stroke-width="4" stroke-linecap="round" />
            {nodes_svg}
        </svg>
        </div>
        """

        # مهم: هم فاصله‌ی ابتدای خط و هم خطوط خالی باید حذف بشن، وگرنه
        # Markdown بلوک HTML رو نصفه می‌بینه و تگ‌های svg (circle/text/line)
        # از داخل <svg> بیرون می‌افتن و به‌صورت متن ساده نمایش داده می‌شن
        stage_svg = "\n".join(
            line.strip()
            for line in stage_svg.strip().splitlines()
            if line.strip()
        )

        st.markdown(stage_svg, unsafe_allow_html=True)
