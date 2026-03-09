"""
Sample PDF Generator for IntelliCredit AI Demo
Generates a realistic-looking corporate annual report PDF for testing.

Usage:
    cd m:\intelli-credit-ai-1
    python sample_data\generate_sample_pdf.py

Output: sample_data\ABC_Steel_Annual_Report_2024.pdf
"""
import os
import sys


def generate_sample_txt():
    """Generate a sample plain-text annual report that the document processor can parse."""
    content = """
=================================================================
               ABC STEEL MANUFACTURING LIMITED
              ANNUAL REPORT — FISCAL YEAR 2024
=================================================================

COMPANY OVERVIEW
-----------------------------------------------------------------
ABC Steel Manufacturing Limited is a leading manufacturer of
steel products with operations spanning across Maharashtra and
Gujarat. The company is engaged in manufacturing structural steel,
TMT bars, HR coils, and CR sheets.

Registered Office: Plot 42, MIDC Industrial Area, Pune 411020
CIN: U27100MH2010PLC123456
Website: www.abcsteel.example.com

BOARD OF DIRECTORS
-----------------------------------------------------------------
Mr. Rajesh Kumar — Chairman & Managing Director
Ms. Priya Sharma — Independent Director
Mr. Anand Gupta — Chief Financial Officer

=================================================================
         STANDALONE STATEMENT OF PROFIT & LOSS
              (for the year ended March 31, 2024)
=================================================================

Particulars                          FY 2024          FY 2023
-----------------------------------------------------------------

Revenue from Operations:
  Net Sales                        650,00,00,000    580,00,00,000
  Other Operating Revenue            5,00,00,000      4,50,00,000
  Total Revenue:                   655,00,00,000    584,50,00,000

Revenue: 65 Crore

Expenses:
  Cost of Materials Consumed       350,00,00,000    310,00,00,000
  Employee Benefits Expense         45,00,00,000     42,00,00,000
  Finance Cost:                     21,00,00,000     19,00,00,000
  Interest Expense: 2.1 Crore
  Depreciation                      28,00,00,000     25,00,00,000
  Other Expenses                    85,00,00,000     80,00,00,000
  Total Expenses                   529,00,00,000    476,00,00,000

Profit Before Tax                  126,00,00,000    108,50,00,000
Tax Expense                         56,00,00,000     48,50,00,000

Net Profit: 7 Crore
Profit After Tax                    70,00,00,000     60,00,00,000

EBITDA: 10.5 Crore

Earnings Per Share (Rs.)                   14.00            12.00

=================================================================
                STANDALONE BALANCE SHEET
              (as at March 31, 2024)
=================================================================

EQUITY AND LIABILITIES
-----------------------------------------------------------------

Shareholders Equity: 25 Crore
Share Capital                       50,00,00,000     50,00,00,000
Reserves and Surplus               200,00,00,000    180,00,00,000
Total Equity                       250,00,00,000    230,00,00,000

NON-CURRENT LIABILITIES
Long Term Borrowings               120,00,00,000    100,00,00,000
Total Debt: 18 Crore
Deferred Tax Liabilities            15,00,00,000     13,00,00,000

CURRENT LIABILITIES
Short Term Borrowings               60,00,00,000     55,00,00,000
Trade Payables                      55,00,00,000     48,00,00,000
Other Current Liabilities           25,00,00,000     22,00,00,000
Current Liabilities: 140,00,00,000

Total Liabilities                  525,00,00,000    468,00,00,000

ASSETS
-----------------------------------------------------------------

NON-CURRENT ASSETS
Property, Plant and Equipment      180,00,00,000    160,00,00,000
Intangible Assets                    5,00,00,000      4,00,00,000
Long Term Investments               35,00,00,000     30,00,00,000

CURRENT ASSETS
Inventories                         85,00,00,000     78,00,00,000
Trade Receivables                   75,00,00,000     68,00,00,000
Cash and Bank Balances              25,00,00,000     20,00,00,000
Other Current Assets                35,00,00,000     30,00,00,000
Current Assets: 220,00,00,000

Total Assets: 45 Crore
Total Assets                       525,00,00,000    468,00,00,000

=================================================================
                KEY FINANCIAL RATIOS
=================================================================

Ratio                              FY 2024      FY 2023
-----------------------------------------------------------------
Debt-to-Equity Ratio                 0.72         0.65
Current Ratio                        1.57         1.44
Profit Margin                       10.77%       10.26%
Return on Equity                    28.00%       26.09%
Interest Coverage Ratio              5.00x        4.68x

=================================================================
              MANAGEMENT DISCUSSION & ANALYSIS
=================================================================

INDUSTRY OUTLOOK
The Indian steel industry continues to benefit from government
infrastructure spending and the 'Make in India' initiative.
Demand growth is expected at 7-8% annually through 2026.

RISKS AND CONCERNS
1. Raw material price volatility remains a key concern
2. Competition from imported steel, especially from China
3. Environmental compliance costs are increasing
4. The company is facing regulatory investigation by the
   pollution control board regarding emissions at Gujarat plant

CORPORATE SOCIAL RESPONSIBILITY
The company invested Rs. 1.5 Crore in CSR activities including
education, healthcare, and environmental sustainability programs.

CAUTIONARY STATEMENT
Statements in this report describing the company's projections
and estimates may be forward-looking within the meaning of
applicable securities laws and regulations.

=================================================================
              AUDITOR'S REPORT (EXTRACTS)
=================================================================

We have audited the accompanying financial statements of
ABC Steel Manufacturing Limited. In our opinion, the financial
statements give a true and fair view of the financial position.

No fraud cases or irregularities were identified during the audit.

=================================================================
        End of Annual Report — ABC Steel Manufacturing Ltd
=================================================================
"""
    return content


def generate_pdf():
    """Try to generate PDF using reportlab, fall back to text file."""
    os.makedirs("sample_data", exist_ok=True)
    content = generate_sample_txt()

    # Try PDF with reportlab
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        pdf_path = os.path.join("sample_data", "ABC_Steel_Annual_Report_2024.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # Split content into lines and write to PDF
        lines = content.strip().split("\n")
        y = height - 50
        page_num = 1

        for line in lines:
            if y < 50:  # New page
                c.setFont("Courier", 8)
                c.drawString(width - 100, 30, f"Page {page_num}")
                c.showPage()
                page_num += 1
                y = height - 50

            # Style headers differently
            if "===" in line:
                c.setFont("Courier-Bold", 9)
                c.setFillColor(colors.HexColor("#1a3a5c"))
            elif "---" in line:
                c.setFont("Courier", 7)
                c.setFillColor(colors.grey)
            elif any(kw in line.upper() for kw in ["REVENUE", "PROFIT", "DEBT", "EQUITY", "ASSETS", "EBITDA"]):
                c.setFont("Courier-Bold", 9)
                c.setFillColor(colors.HexColor("#0a2540"))
            else:
                c.setFont("Courier", 9)
                c.setFillColor(colors.black)

            c.drawString(40, y, line[:95])  # Trim long lines
            y -= 12

        c.setFont("Courier", 8)
        c.drawString(width - 100, 30, f"Page {page_num}")
        c.save()
        print(f"✅ Sample PDF created: {pdf_path}")
        return pdf_path

    except ImportError:
        print("⚠️  reportlab not installed — creating .txt instead (system can parse this too)")
        txt_path = os.path.join("sample_data", "ABC_Steel_Annual_Report_2024.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Sample text file created: {txt_path}")
        return txt_path


if __name__ == "__main__":
    generate_pdf()
