from decimal import Decimal
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def fmt_money(value) -> str:
    if value is None:
        return "0.00"
    return f"{Decimal(str(value)):.2f}"


def fmt_dt(dt: datetime) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _header_footer(canvas, doc, client):
    canvas.saveState()
    width, height = A4

    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(
        20 * mm, height - 15 * mm, "Banking System - Transaction Statement"
    )
    canvas.setFont("Helvetica", 9)
    canvas.drawString(
        20 * mm,
        height - 22 * mm,
        f"Client: {client.name} {client.surname}  |  Email: {client.email}",
    )
    canvas.drawRightString(
        width - 20 * mm,
        height - 22 * mm,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 20 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_statement_pdf(client, transactions) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=30 * mm,
        bottomMargin=20 * mm,
        title=f"Statement_{client.id}.pdf",
        author="Banking System",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(name="Right", parent=styles["Normal"], alignment=TA_RIGHT)
    )
    styles.add(
        ParagraphStyle(name="Center", parent=styles["Normal"], alignment=TA_CENTER)
    )
    styles.add(
        ParagraphStyle(name="Bold", parent=styles["Normal"], fontName="Helvetica-Bold")
    )
    styles.add(ParagraphStyle(name="Mono", parent=styles["Normal"], fontName="Courier"))
    story = []

    story.append(Paragraph(f"Detailed Transaction Statement", styles["Title"]))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"Client: <b>{client.name} {client.surname}</b> (ID: {client.id})",
            styles["Normal"],
        )
    )
    story.append(Paragraph(f"Email: {client.email or '-'}", styles["Normal"]))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            f"Current Balance: <b>{fmt_money(client.balance)}</b>", styles["Bold"]
        )
    )
    story.append(Spacer(1, 12))

    data = [["Date & Time", "Type", "Amount", "Status"]]

    txs = sorted(transactions, key=lambda t: t.timestamp or datetime.min, reverse=True)

    for t in txs:
        status = "OK"
        if getattr(t, "is_reversed", False):
            status = "REVERSED"
        elif getattr(t, "reversal_of_id", None):
            status = "REVERSAL"

        row = [
            fmt_dt(t.timestamp),
            t.type.capitalize(),
            fmt_money(t.amount),
            status,
        ]
        data.append(row)

    table = Table(data, colWidths=[60 * mm, 30 * mm, 35 * mm, 35 * mm])
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F3F4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (2, 1), (2, -1), "RIGHT"),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
            ("ALIGN", (3, 1), (3, -1), "CENTER"),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#FAFAFA")],
            ),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
        ]
    )
    table.setStyle(table_style)
    story.append(table)

    deposits = sum(
        Decimal(str(t.amount))
        for t in txs
        if t.type == "deposit" and not getattr(t, "is_reversed", False)
    )
    withdrawals = sum(
        Decimal(str(t.amount))
        for t in txs
        if t.type == "withdrawal" and not getattr(t, "is_reversed", False)
    )
    transfer_in = sum(
        Decimal(str(t.amount))
        for t in txs
        if t.type == "transfer_in" and not getattr(t, "is_reversed", False)
    )
    transfer_out = sum(
        Decimal(str(t.amount))
        for t in txs
        if t.type == "transfer_out" and not getattr(t, "is_reversed", False)
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(f"Total Deposits: <b>{fmt_money(deposits)}</b>", styles["Normal"])
    )
    story.append(
        Paragraph(
            f"Total Withdrawals: <b>{fmt_money(withdrawals)}</b>", styles["Normal"]
        )
    )
    story.append(
        Paragraph(
            f"Total Transfer In: <b>{fmt_money(transfer_in)}</b>", styles["Normal"]
        )
    )
    story.append(
        Paragraph(
            f"Total Transfer Out: <b>{fmt_money(transfer_out)}</b>", styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"Net Change: <b>{fmt_money(deposits + transfer_in - transfer_out - withdrawals)}</b>",
            styles["Bold"],
        )
    )

    def on_page(canvas, doc_):
        _header_footer(canvas, doc_, client)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
