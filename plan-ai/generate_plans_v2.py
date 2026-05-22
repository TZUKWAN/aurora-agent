#!/usr/bin/env python3
"""
批量生成湖北省大学生创业扶持项目商业计划书 v2.0
严格遵循4章模板结构，每份6万字+
"""
import os
import sys
import json
import re
import time
import openpyxl
from docx import Document
from docx.shared import Pt, Cm, Inches, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import random

# ============================================================
# 配置
# ============================================================
EXCEL_PATH = r"D:\计划书AI\省补贴项目清单.xlsx"
OUTPUT_DIR = r"D:\计划书AI\output_v2"
TEMPLATE_PATH = r"D:\计划书AI\湖北省大学生创业扶持项目模板2026.docx"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 工具函数
# ============================================================

def read_projects():
    """读取Excel中的项目清单"""
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb.active
    projects = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        title = row[0] or ''
        desc = row[1] or ''
        company = row[2] or '【待填写】'
        person = row[3] or '【待填写】'
        if title:
            projects.append({
                'id': i,
                'title': title.strip(),
                'desc': desc.strip(),
                'company': company,
                'person': person
            })
    return projects


def set_cell_font(cell, text, font_name='宋体', font_size=9, bold=False):
    """设置单元格字体"""
    cell.text = str(text)
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)


def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                          f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                          f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                          f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                          f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                          f'</w:tcBorders>')
    tcPr.append(tcBorders)


def add_heading(doc, text, level):
    """添加标题"""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = '黑体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    return heading


def add_paragraph(doc, text, font_name='宋体', font_size=12, bold=False,
                  first_line_indent=True, alignment=None):
    """添加正文段落"""
    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment
    if first_line_indent:
        p.paragraph_format.first_line_indent = Pt(24)
    p.paragraph_format.line_spacing = 1.5

    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    return p


def add_figure_placeholder(doc, fig_num, caption, width_cm=15):
    """添加图片占位符（灰色框+标题）"""
    # 添加图片占位框
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 创建一个单行单列表格作为占位框
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.text = f'\n\n【图 {fig_num} 区域 - 请插入图片】\n\n'
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 设置灰色背景
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E8E8E8" w:val="clear"/>')
    cell._tc.get_or_add_tcPr().append(shading)

    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(128, 128, 128)

    # 图尾标题
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_caption.add_run(f'图{fig_num} {caption}')
    run.font.name = '宋体'
    run.font.size = Pt(10)
    run.font.bold = True
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    return table


def add_table_caption(doc, table_num, caption):
    """添加表头（表格上方的标题）"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'表{table_num} {caption}')
    run.font.name = '宋体'
    run.font.size = Pt(10)
    run.font.bold = True
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def format_financial_table(table, data, header_row=True):
    """格式化财务表格 - 动态适配行列数"""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    num_rows = len(data)
    num_cols = max(len(row) for row in data) if data else 7

    # 确保表格行数正确
    while len(table.rows) < num_rows:
        table.add_row()
    # 确保每行列数正确
    for row in table.rows[:num_rows]:
        while len(row.cells) < num_cols:
            row._tr.append(parse_xml(f'<w:tc {nsdecls("w")}><w:tcPr/><w:p/></w:tc>'))

    # 设置表格边框
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    # 填充数据
    for i, row_data in enumerate(data):
        row = table.rows[i]
        for j, val in enumerate(row_data):
            if j >= len(row.cells):
                break
            cell = row.cells[j]
            is_bold = (i == 0) if header_row else False
            is_section_header = isinstance(val, str) and (val.startswith('一、') or val.startswith('二、') or
                                                          val.startswith('三、') or val.startswith('四、') or
                                                          val.startswith('五、') or val.startswith('六、') or
                                                          val.startswith('流动资产') or val.startswith('非流动资产') or
                                                          val.startswith('流动负债') or val.startswith('非流动负债') or
                                                          val.startswith('所有者') or val.startswith('资产总计') or
                                                          val.startswith('负债合计') or val.startswith('负债和'))
            set_cell_font(cell, val, font_size=9, bold=is_bold or is_section_header)


# ============================================================
# 财务数据生成
# ============================================================

def generate_profit_table(base_revenue=None):
    """生成利润表数据"""
    if base_revenue is None:
        base_revenue = random.randint(185, 255)

    years = ['项       目', '2026年度', '2027年度', '2028年度', '2029年度', '2030年度', '2031年度']
    growth_rates = [0.30, 0.32, 0.35, 0.28, 0.25, 0.22]

    revenues = [base_revenue]
    for rate in growth_rates:
        revenues.append(round(revenues[-1] * (1 + rate), 2))

    cost_ratio = random.uniform(0.45, 0.55)
    tax_rate_ratio = random.uniform(0.005, 0.01)
    sell_ratio = random.uniform(0.08, 0.12)
    admin_ratio = random.uniform(0.10, 0.15)
    fin_ratio = random.uniform(0.01, 0.03)

    rows = [years]

    rev_row = ['一、营业收入'] + [round(r, 2) for r in revenues]
    rows.append(rev_row)

    cost_row = ['减：营业成本'] + [round(-r * cost_ratio, 2) for r in revenues]
    rows.append(cost_row)

    tax_row = ['营业税金及附加'] + [round(-r * tax_rate_ratio, 2) for r in revenues]
    rows.append(tax_row)

    sell_row = ['销售费用'] + [round(-r * sell_ratio, 2) for r in revenues]
    rows.append(sell_row)

    admin_row = ['管理费用'] + [round(-r * admin_ratio, 2) for r in revenues]
    rows.append(admin_row)

    fin_row = ['财务费用'] + [round(-r * fin_ratio, 2) for r in revenues]
    rows.append(fin_row)

    asset_loss = ['资产减值损失'] + [0] * 6
    rows.append(asset_loss)

    fair_value = ['加：公允价值变动收益'] + [0] * 6
    rows.append(fair_value)

    invest_income = ['投资收益'] + [0] * 6
    rows.append(invest_income)

    # 营业利润 = 营业收入 + 成本 + 税金 + 三费 + 公允价值 + 投资收益
    op_profits = []
    for i in range(6):
        op_profit = revenues[i] + cost_row[i+1] + tax_row[i+1] + sell_row[i+1] + admin_row[i+1] + fin_row[i+1]
        op_profits.append(round(op_profit, 2))
    op_profit_row = ['二、营业利润'] + op_profits
    rows.append(op_profit_row)

    non_op_income = ['加：营业外收入'] + [round(random.uniform(1, 5), 2) for _ in range(6)]
    rows.append(non_op_income)

    non_op_exp = ['减：营业外支出'] + [round(-random.uniform(0.5, 2), 2) for _ in range(6)]
    rows.append(non_op_exp)

    total_profits = [round(op_profits[i] + non_op_income[i+1] + non_op_exp[i+1], 2) for i in range(6)]
    total_profit_row = ['三、利润总额'] + total_profits
    rows.append(total_profit_row)

    income_tax = ['减：所得税费用'] + [round(-max(0, tp) * 0.15, 2) for tp in total_profits]
    rows.append(income_tax)

    net_profits = [round(total_profits[i] + income_tax[i+1], 2) for i in range(6)]
    net_profit_row = ['四、净利润'] + net_profits
    rows.append(net_profit_row)

    eps_basic = ['五、每股收益：']
    eps_diluted = ['（一）基本每股收益']
    eps_diluted2 = ['（二）稀释每股收益']
    for i in range(6):
        eps_val = round(net_profits[i] / 500, 4)
        eps_basic.append('')
        eps_diluted.append(eps_val)
        eps_diluted2.append(eps_val)
    rows.append(eps_basic)
    rows.append(eps_diluted)
    rows.append(eps_diluted2)

    return {
        'data': rows,
        'revenues': revenues,
        'net_profits': net_profits,
        'total_profits': total_profits,
        'op_profits': op_profits,
        'costs': [abs(cost_row[i+1]) for i in range(6)],
        'sell_expenses': [abs(sell_row[i+1]) for i in range(6)],
        'admin_expenses': [abs(admin_row[i+1]) for i in range(6)]
    }


def generate_cashflow_table(profit_data):
    """生成现金流量表数据（与利润表勾稽）"""
    revenues = profit_data['revenues']
    net_profits = profit_data['net_profits']
    costs = profit_data['costs']
    sell_exp = profit_data['sell_expenses']
    admin_exp = profit_data['admin_expenses']

    rows = []
    header = ['项       目', '2026年度', '2027年度', '2028年度', '2029年度', '2030年度', '2031年度']
    rows.append(header)

    # 经营活动
    sale_cash = ['销售商品、提供劳务收到的现金'] + [round(r * random.uniform(0.95, 1.05), 2) for r in revenues]
    rows.append(sale_cash)

    tax_return = ['收到的税费返还'] + [round(random.uniform(1, 5), 2) for _ in range(6)]
    rows.append(tax_return)

    other_op_cash = ['收到其他与经营活动有关的现金'] + [round(random.uniform(2, 10), 2) for _ in range(6)]
    rows.append(other_op_cash)

    op_inflow = ['经营活动现金流入小计']
    for i in range(6):
        op_inflow.append(round(sale_cash[i+1] + tax_return[i+1] + other_op_cash[i+1], 2))
    rows.append(op_inflow)

    purchase_cash = ['购买商品、接受劳务支付的现金'] + [round(-c * random.uniform(0.90, 1.0), 2) for c in costs]
    rows.append(purchase_cash)

    employee_cash = ['支付给职工以及为职工支付的现金'] + [round(-admin_exp[i] * random.uniform(0.5, 0.7), 2) for i in range(6)]
    rows.append(employee_cash)

    tax_paid = ['支付的各项税费'] + [round(-r * random.uniform(0.03, 0.06), 2) for r in revenues]
    rows.append(tax_paid)

    other_op_out = ['支付其他与经营活动有关的现金'] + [round(-sell_exp[i] * random.uniform(0.6, 0.8), 2) for i in range(6)]
    rows.append(other_op_out)

    op_outflow = ['经营活动现金流出小计']
    for i in range(6):
        op_outflow.append(round(purchase_cash[i+1] + employee_cash[i+1] + tax_paid[i+1] + other_op_out[i+1], 2))
    rows.append(op_outflow)

    op_net = ['经营活动产生的现金流量净额']
    for i in range(6):
        op_net.append(round(op_inflow[i+1] + op_outflow[i+1], 2))
    rows.append(op_net)

    # 投资活动
    rows.append(['二、投资活动产生的现金流量：', '', '', '', '', '', ''])
    rows.append(['收回投资收到的现金'] + [0]*6)
    rows.append(['取得投资收益收到的现金'] + [0]*6)
    rows.append(['处置固定资产、无形资产和其他长期资产收回的现金净额'] + [0]*6)
    rows.append(['收到的其他与投资活动有关的现金'] + [0]*6)
    rows.append(['投资活动现金流入小计'] + [0]*6)

    invest_out = ['购建固定资产、无形资产和其他长期资产所支付的现金']
    invest_vals = []
    for i in range(6):
        val = round(-random.uniform(15, 40) * (1 - i * 0.1), 2) if i < 4 else round(-random.uniform(5, 15), 2)
        invest_vals.append(val)
    invest_out += invest_vals
    rows.append(invest_out)

    rows.append(['投资支付的现金'] + [0]*6)
    rows.append(['支付其他与投资活动有关的现金'] + [0]*6)

    inv_outflow = ['投资活动现金流出小计'] + invest_vals
    rows.append(inv_outflow)

    inv_net = ['投资活动产生的现金流量净额'] + invest_vals
    rows.append(inv_net)

    # 筹资活动
    rows.append(['三、筹资活动产生的现金流量：', '', '', '', '', '', ''])
    absorb_invest = ['吸收投资收到的现金']
    absorb_vals = [round(random.uniform(200, 500), 2), round(random.uniform(100, 300), 2)] + [0]*4
    absorb_invest += absorb_vals
    rows.append(absorb_invest)

    rows.append(['其中：子公司吸收少数股东投资收到的现金'] + [0]*6)

    borrow_cash = ['取得借款所收到的现金']
    borrow_vals = [round(random.uniform(50, 100), 2), 0, 0, 0, 0, 0]
    borrow_cash += borrow_vals
    rows.append(borrow_cash)

    rows.append(['收到其他与筹资活动有关的现金'] + [0]*6)

    fin_inflow = ['筹资活动现金流入小计']
    for i in range(6):
        fin_inflow.append(round(absorb_vals[i] + borrow_vals[i], 2))
    rows.append(fin_inflow)

    repay = ['偿还债务支付的现金'] + [round(-borrow_vals[0] / 3, 2), round(-borrow_vals[0] / 3, 2), round(-borrow_vals[0] / 3, 2)] + [0]*3
    rows.append(repay)

    dividend = ['分配股利、利润或偿付利息支付的现金']
    div_vals = [0, 0, round(-net_profits[2] * 0.1, 2)]
    for i in range(3, 6):
        div_vals.append(round(-net_profits[i] * random.uniform(0.1, 0.2), 2))
    dividend += div_vals
    rows.append(dividend)

    rows.append(['其中：子公司支付给少数股东的股利、利润'] + [0]*6)
    rows.append(['支付其他与筹资活动有关的现金'] + [0]*6)

    fin_outflow = ['筹资活动现金流出小计']
    for i in range(6):
        fin_outflow.append(round(repay[i+1] + div_vals[i], 2))
    rows.append(fin_outflow)

    fin_net = ['筹资活动产生的现金流量净额']
    for i in range(6):
        fin_net.append(round(fin_inflow[i+1] + fin_outflow[i+1], 2))
    rows.append(fin_net)

    rows.append(['四、汇率变动对现金及现金等价物的影响'] + [0]*6)

    cash_net_increase = ['五、现金及现金等价物净增加额']
    for i in range(6):
        cash_net_increase.append(round(op_net[i+1] + inv_net[i+1] + fin_net[i+1], 2))
    rows.append(cash_net_increase)

    cash_begin = ['加：期初现金及现金等价物余额']
    cash_balances = [round(random.uniform(20, 50), 2)]
    for i in range(5):
        cash_balances.append(round(cash_balances[-1] + cash_net_increase[i+1], 2))
    cash_begin += cash_balances
    rows.append(cash_begin)

    cash_end = ['六、期末现金及现金等价物余额']
    end_balances = [round(cash_balances[i] + cash_net_increase[i+1], 2) for i in range(6)]
    cash_end += end_balances
    rows.append(cash_end)

    return {
        'data': rows,
        'op_net': [op_net[i+1] for i in range(6)],
        'end_balances': end_balances,
        'invest_out': invest_vals,
        'absorb_vals': absorb_vals
    }


def generate_balance_sheet(profit_data, cashflow_data):
    """生成资产负债表数据（与利润表、现金流量表勾稽）"""
    revenues = profit_data['revenues']
    net_profits = profit_data['net_profits']
    costs = profit_data['costs']
    end_balances = cashflow_data['end_balances']
    invest_vals = cashflow_data['invest_out']

    header = ['项       目', '2026年度', '2027年度', '2028年度', '2029年度', '2030年度', '2031年度']
    rows = [header]

    # 流动资产
    rows.append(['流动资产：', '', '', '', '', '', ''])

    cash_row = ['货币资金'] + end_balances
    rows.append(cash_row)

    rows.append(['交易性金融资产'] + [0]*6)
    rows.append(['应收票据'] + [round(random.uniform(5, 15), 2) for _ in range(6)])
    rows.append(['应收账款'] + [round(r * random.uniform(0.08, 0.15), 2) for r in revenues])
    rows.append(['预付款项'] + [round(random.uniform(3, 8), 2) for _ in range(6)])
    rows.append(['应收利息'] + [0]*6)
    rows.append(['应收股利'] + [0]*6)
    rows.append(['其他应收款'] + [round(random.uniform(1, 5), 2) for _ in range(6)])
    rows.append(['存货'] + [round(c * random.uniform(0.1, 0.2), 2) for c in costs])
    rows.append(['一年内到期的非流动资产'] + [0]*6)
    rows.append(['其他流动资产'] + [round(random.uniform(2, 8), 2) for _ in range(6)])

    # 流动资产合计
    current_asset_items = [cash_row] + [rows[i] for i in range(len(rows)-5, len(rows)) if rows[i][0] in ['交易性金融资产', '应收票据', '应收账款', '预付款项', '应收利息', '应收股利', '其他应收款', '存货', '一年内到期的非流动资产', '其他流动资产']]

    # 重新计算 - 简化方式
    ca_start = 3  # 货币资金的index
    ca_total = ['流动资产合计']
    for col in range(1, 7):
        total = 0
        for r in rows[ca_start:]:
            if r[0] in ['非流动资产：', '流动资产合计']:
                break
            if isinstance(r[col], (int, float)):
                total += r[col]
        ca_total.append(round(total, 2))

    # 插入流动资产合计
    # 找到非流动资产位置
    non_current_idx = None
    for i, r in enumerate(rows):
        if r[0] == '非流动资产：':
            non_current_idx = i
            break
    if non_current_idx is None:
        rows.append(ca_total)
    else:
        rows.insert(non_current_idx, ca_total)

    # 非流动资产
    rows.append(['非流动资产：', '', '', '', '', '', ''])

    rows.append(['可供出售金融资产'] + [0]*6)
    rows.append(['持有至到期投资'] + [0]*6)
    rows.append(['长期股权投资'] + [0]*6)

    # 固定资产 = 累计投资
    fixed_assets = [500]  # 初始固定资产
    for i in range(5):
        fixed_assets.append(round(fixed_assets[-1] + abs(invest_vals[i+1]) - fixed_assets[-1] * 0.08, 2))
    rows.append(['固定资产'] + fixed_assets)

    rows.append(['在建工程'] + [round(random.uniform(5, 20), 2) for _ in range(6)])

    intangible = [50]
    for i in range(5):
        intangible.append(round(intangible[-1] + random.uniform(5, 15) - intangible[-1] * 0.1, 2))
    rows.append(['无形资产'] + intangible)

    rows.append(['商誉'] + [0]*6)
    rows.append(['长期待摊费用'] + [round(random.uniform(2, 8), 2) for _ in range(6)])
    rows.append(['递延所得税资产'] + [round(random.uniform(1, 3), 2) for _ in range(6)])
    rows.append(['其他非流动资产'] + [0]*6)

    non_ca_total = ['非流动资产合计']
    for col in range(1, 7):
        total = 0
        for r in rows:
            if r[0] in ['固定资产', '在建工程', '无形资产', '商誉', '长期待摊费用', '递延所得税资产', '其他非流动资产']:
                if isinstance(r[col], (int, float)):
                    total += r[col]
        non_ca_total.append(round(total, 2))
    rows.append(non_ca_total)

    asset_total = ['资产总计']
    for col in range(1, 7):
        asset_total.append(round(ca_total[col] + non_ca_total[col], 2))
    rows.append(asset_total)

    # 流动负债
    rows.append(['流动负债：', '', '', '', '', '', ''])
    rows.append(['短期借款'] + [round(random.uniform(20, 50), 2), round(random.uniform(10, 30), 2)] + [0]*4)
    rows.append(['交易性金融负债'] + [0]*6)
    rows.append(['应付票据'] + [round(random.uniform(3, 10), 2) for _ in range(6)])
    rows.append(['应付账款'] + [round(c * random.uniform(0.05, 0.12), 2) for c in costs])
    rows.append(['预收款项'] + [round(r * random.uniform(0.02, 0.05), 2) for r in revenues])
    rows.append(['应付职工薪酬'] + [round(random.uniform(5, 15), 2) for _ in range(6)])
    rows.append(['应交税费'] + [round(random.uniform(3, 10), 2) for _ in range(6)])
    rows.append(['应付利息'] + [round(random.uniform(1, 3), 2) for _ in range(6)])
    rows.append(['应付股利'] + [0]*6)
    rows.append(['其他应付款'] + [round(random.uniform(2, 8), 2) for _ in range(6)])
    rows.append(['一年内到期的非流动负债'] + [0]*6)
    rows.append(['其他流动负债'] + [0]*6)

    cl_total = ['流动负债合计']
    for col in range(1, 7):
        total = 0
        in_section = False
        for r in rows:
            if r[0] == '流动负债：':
                in_section = True
                continue
            if r[0] in ['非流动负债：', '流动负债合计']:
                in_section = False
                continue
            if in_section and isinstance(r[col], (int, float)):
                total += r[col]
        cl_total.append(round(total, 2))
    rows.append(cl_total)

    # 非流动负债
    rows.append(['非流动负债：', '', '', '', '', '', ''])
    rows.append(['长期借款'] + [round(random.uniform(30, 80), 2)] + [round(random.uniform(20, 50), 2)] + [0]*4)
    rows.append(['应付债券'] + [0]*6)
    rows.append(['长期应付款'] + [0]*6)
    rows.append(['其他非流动负债'] + [0]*6)

    ncl_total = ['非流动负债合计']
    for col in range(1, 7):
        total = 0
        for r in rows:
            if r[0] in ['长期借款', '应付债券', '长期应付款', '其他非流动负债'] and col < len(r):
                if isinstance(r[col], (int, float)):
                    total += r[col]
        ncl_total.append(round(total, 2))
    rows.append(ncl_total)

    liability_total = ['负债合计']
    for col in range(1, 7):
        liability_total.append(round(cl_total[col] + ncl_total[col], 2))
    rows.append(liability_total)

    # 所有者权益
    rows.append(['所有者权益（或股东权益）：', '', '', '', '', '', ''])
    rows.append(['实收资本（或股本）'] + [500]*6)
    rows.append(['资本公积'] + [round(random.uniform(50, 100), 2)]*6)

    surplus = ['盈余公积']
    sv = 0
    for i in range(6):
        sv += round(max(0, net_profits[i]) * 0.10, 2)
        surplus.append(round(sv, 2))
    rows.append(surplus)

    retained = ['未分配利润']
    rv = 0
    for i in range(6):
        rv += round(net_profits[i] * 0.9, 2)
        retained.append(round(rv, 2))
    rows.append(retained)

    equity_total = ['所有者权益（或股东权益）合计']
    for col in range(1, 7):
        equity_total.append(round(500 + rows[-4][col] + surplus[col] + retained[col], 2))
    rows.append(equity_total)

    # 负债和所有者权益总计 - 需要与资产总计匹配
    # 调整资本公积使资产负债表平衡
    for col in range(1, 7):
        target = asset_total[col]
        current_liab = liability_total[col]
        equity_needed = target - current_liab
        equity_current = 500 + rows[-4][col] + surplus[col] + retained[col]
        diff = equity_needed - equity_current
        rows[-4][col] = round(rows[-4][col] + diff, 2)
        equity_total[col] = round(target - current_liab, 2)

    le_total = ['负债和所有者权益（或股东益）总计']
    for col in range(1, 7):
        le_total.append(round(liability_total[col] + equity_total[col], 2))
    rows.append(le_total)

    return {'data': rows}


# ============================================================
# 内容生成模块
# ============================================================

def generate_chapter1_content(project):
    """生成第一章内容：企业基本情况"""
    title = project['title']
    desc = project['desc']
    company = project['company']
    person = project['person']

    # 提取项目关键词
    name_part = title.split('——')[0] if '——' in title else title
    tech_part = title.split('——')[1] if '——' in title else desc

    content_parts = []

    # 一、企业概况 (3000-5000字)
    content_parts.append({
        'heading': '一、企业概况',
        'level': 2,
        'text': f"""{company}公司注册成立于湖北省武汉市东湖新技术开发区，注册资本人民币500万元。公司专注于{desc}领域的科技创新与产业化应用，主营业务为{tech_part}的研发、运营与技术服务。核心产品"{name_part}"，面向{extract_target_scene(desc)}场景，基于{extract_tech_method(desc)}技术路线，系统性地解决{extract_pain_point(desc)}等行业痛点问题，在{extract_advantage(desc)}等方面具有显著的创新优势。

当前，{generate_industry_background(desc)}行业正处于技术迭代与产业升级的关键阶段。随着{generate_tech_trend(desc)}技术的持续突破，{extract_target_scene(desc)}领域对智能化、数字化解决方案的需求日益迫切。然而，现有市场中的同类产品与服务在{extract_pain_point(desc)}等关键环节存在明显的技术瓶颈与应用短板，难以满足终端用户对精准性、实时性与智能化水平的实际需求。本公司基于对行业发展趋势的深度研判与核心技术的系统性攻关，自主研发了"{name_part}"产品体系，构建了覆盖数据采集、智能分析、决策支持与系统优化的全链路技术解决方案。

公司核心产品"{name_part}"采用{extract_tech_method(desc)}技术架构，深度融合{generate_core_tech_stack(desc)}等前沿技术模块，在{extract_advantage(desc)}等核心技术指标上实现了行业突破。系统具备{generate_feature_list(desc)}等多项核心功能，能够为终端用户提供端到端的智能化服务体验。公司已取得软件著作权2项，正在申请发明专利1项，核心技术体系形成了完整的自主知识产权保护矩阵。

公司始终坚持自主研发与技术创新双轮驱动的发展战略，组建了一支涵盖{generate_team_domains(desc)}等多个专业方向的高层次研发团队。团队核心成员拥有{generate_team_background(desc)}等深厚的学术积累与产业实践经验。公司秉承"技术驱动价值，创新服务产业"的经营理念，致力于将前沿科研成果转化为可规模化复制的商业产品，为行业客户提供高质量、高可靠性的智能化解决方案，推动{desc}领域的技术进步与产业升级。

公司在技术研发层面持续加大投入力度，研发费用占营业收入的比例始终保持在较高水平。公司建立了完善的研发管理体系，涵盖需求分析、技术预研、原型开发、系统测试、产品迭代等全流程研发环节，确保技术创新的持续性与产品研发的高效性。公司积极与高校、科研院所开展产学研合作，与华中科技大学、武汉大学等高校建立了长期稳定的合作关系，在{extract_tech_method(desc)}等核心技术领域形成了联合攻关机制。

公司高度重视知识产权保护与技术壁垒构建，围绕核心产品与关键技术建立了完善的知识产权保护体系。目前已获得授权的知识产权包括软件著作权2项，另有1项发明专利正在实质审查阶段。公司在技术文档管理、源代码分级加密、核心人员保密与竞业限制等方面建立了严格的内控制度，确保核心技术的安全性与可控性。公司同时积极参与行业标准的制定与技术交流，持续提升在{desc}领域的技术影响力与行业话语权。"""
    })

    # 二、公司股权结构 (2000-3000字)
    content_parts.append({
        'heading': '二、公司股权结构',
        'level': 2,
        'text': f"""公司法定代表人为{person}，持有公司股份42%，为公司控股股东及实际控制人。公司股权结构设计充分遵循现代公司治理理念，兼顾了创始团队的控制力、核心人才的激励效果与公司治理的规范性要求。

公司股东结构及持股比例如下：法定代表人{person}持有公司42%的股权，为公司最大股东及实际控制人，负责公司整体战略规划与核心技术攻关。技术合伙人（{generate_tech_direction(desc)}方向）持有公司23%的股权，主要负责公司核心技术研发体系建设与前沿技术预研工作。运营合伙人（{generate_biz_direction(desc)}方向）持有公司18%的股权，主要负责公司产品运营、市场拓展与客户关系管理工作。公司同时预留了17%的员工期权池，用于未来核心人才的股权激励，确保公司在人才竞争中保持持续吸引力。

上述股权结构设计体现了以下几方面的合理性考量。创始团队保持相对控股地位，确保公司在重大决策方向上的战略定力与执行效率。技术合伙人与运营合伙人的持股比例与其在项目中的核心贡献度相匹配，充分体现了"价值创造决定价值分配"的股权设计原则。员工期权池的预留为公司后续引进高层次技术人才与市场拓展骨干提供了充足的激励空间，有助于构建长期稳定的核心团队。公司股权结构集中度适中，既避免了股权过度分散导致的决策效率低下问题，也规避了一股独大可能带来的治理风险。

公司在股权管理方面建立了规范的制度体系。公司章程对股权转让、增资扩股、股权激励等重大股权变动事项设定了明确的决策程序与审批流程。股东协议中对优先购买权、共同出售权、反稀释条款等核心条款作出了详细约定，有效保障了各股东的合法权益。公司在后续融资过程中将严格遵守股权管理的各项制度规范，确保股权结构的稳定性和公司治理的规范性。

公司计划在后续发展阶段根据业务发展需要和人才引进计划，通过股权激励方式逐步释放员工期权池中的预留股权。股权激励方案将结合员工岗位价值、服务年限、绩效贡献等多重维度综合确定，确保激励机制的公平性与有效性。公司在股权激励实施过程中将严格按照《公司法》及相关法律法规的规定履行审批程序，确保股权激励的合法合规性。"""
    })

    # 三、创业团队 (3000-5000字)
    content_parts.append({
        'heading': '三、创业团队',
        'level': 2,
        'text': f"""公司创始团队由{generate_team_domains(desc)}等多个专业领域的高层次人才组成，团队成员在学术研究、技术研发与产业实践方面均具有深厚的积累与突出的成就，形成了专业互补、能力协同的高水平创业团队。

创始人兼首席执行官（CEO）{person}，拥有{generate_founder_bg(desc)}。创始人长期深耕{extract_tech_method(desc)}领域的学术研究与技术开发工作，研究方向聚焦于{generate_research_focus(desc)}等前沿课题，在国内外顶级学术期刊和会议上发表多篇高水平研究论文。创始人在{desc}领域积累了丰富的理论基础与技术实践经验，对行业技术发展趋势和市场需求变化具有敏锐的洞察力和前瞻性判断能力，曾主导完成多个{extract_target_scene(desc)}领域的重点研发项目，具有突出的技术攻关能力和项目组织协调能力。

技术合伙人兼首席技术官（CTO），拥有{generate_cto_bg(desc)}。技术合伙人专注于{generate_tech_direction(desc)}方向的工程化研发与系统架构设计工作，在{generate_core_tech_stack(desc)}等核心技术领域积累了丰富的工程实践经验。技术合伙人曾参与多个大型{extract_target_scene(desc)}系统的研发工作，主导完成了从技术选型、架构设计到系统开发、测试部署的全流程技术管理工作，具备将前沿科研成果转化为可规模化部署的商业产品的完整技术能力。技术合伙人对分布式系统架构、高并发数据处理、智能算法优化等关键技术环节具有深入的理解和丰富的工程化落地经验。

运营合伙人兼首席运营官（COO），拥有{generate_co_bg(desc)}。运营合伙人在{generate_biz_direction(desc)}领域拥有八年的行业从业经验，对{extract_target_scene(desc)}行业的商业模式、客户需求特征、市场竞争格局和产业链上下游关系有着系统性的认知和深刻的理解。运营合伙人曾在多家{desc}领域的企业担任核心运营管理岗位，主导完成了多个产品的市场推广与客户拓展项目，积累了丰富的市场运营经验和客户资源。运营合伙人擅长从市场需求出发进行产品定位与商业模式设计，具备将技术创新转化为商业价值的系统化能力。

团队现有成员共{random.randint(10, 18)}人，其中研发人员占比超过65%，团队成员中拥有博士学位{random.randint(2, 5)}人、硕士学位{random.randint(5, 10)}人，本科及以上学历覆盖率达到100%。团队成员的专业背景涵盖{generate_team_domains(desc)}等多个学科方向，形成了多学科交叉融合的创新型团队结构。公司在人才招聘方面坚持"高标准、严要求"的选人用人原则，重点引进具有深厚学术积累和丰富工程经验的高层次技术人才，确保团队整体技术水平的持续提升。

团队在协作机制方面建立了高效的沟通与决策体系。公司实行周度技术评审、月度项目复盘、季度战略研讨的常态化沟通机制，确保信息传递的及时性与决策过程的科学性。团队内部建立了明确的技术分工与责任体系，各核心成员在其专业领域内拥有充分的技术决策权与资源调配权，有效激发了团队的创新活力与执行效率。公司同时注重团队文化建设，营造开放包容、追求卓越的创新氛围，吸引和留住优秀人才。"""
    })

    # 四、员工社会保障情况 (500-1000字)
    content_parts.append({
        'heading': '四、员工社会保障情况',
        'level': 2,
        'text': f"""公司高度重视员工社会保障工作，严格遵守《中华人民共和国劳动法》《中华人民共和国社会保险法》等相关法律法规的规定，为全部在册员工依法缴纳养老保险、医疗保险、失业保险、工伤保险、生育保险等五项社会保险及住房公积金，社会保险覆盖率达到100%。

公司在员工福利保障方面建立了多层次的保障体系。在法定社会保险和住房公积金的基础上，公司为全体员工购买了商业补充医疗保险和意外伤害保险，进一步提升了员工的医疗保障水平和抗风险能力。公司同时建立了年度健康体检制度，为每位员工提供每年一次的全面健康体检服务，关注员工的身体健康状况。公司严格执行国家法定休假制度，并在此基础上设立了带薪年假、弹性工作等人性化的假期管理制度，保障员工的工作与生活平衡。

公司在劳动关系管理方面严格遵循法律法规的要求，与全部员工签订了规范的劳动合同，劳动合同签订率达到100%。公司在员工入职、岗位调整、薪酬变更等环节均建立了规范的审批流程和档案管理制度，确保劳动关系的合规性和可追溯性。公司建立了完善的薪酬福利体系，员工的薪酬水平与岗位价值、绩效贡献挂钩，确保薪酬分配的公平性和激励性。

公司将持续完善员工社会保障体系，随着公司业务规模的扩大和盈利能力的提升，逐步提高员工的福利保障水平，为员工提供更加全面、更加优质的社会保障服务，切实维护员工的合法权益，构建和谐稳定的劳动关系。"""
    })

    # 五、公司组织结构情况 (2000-3000字)
    content_parts.append({
        'heading': '五、公司组织结构情况',
        'level': 2,
        'text': f"""公司根据业务发展需要和现代企业管理理念，构建了扁平化、高效率的组织架构体系。公司设立三大核心职能部门：技术研发部、产品运营部和市场商务部，各部门在公司总经理的统一领导下分工协作、高效运转。

技术研发部是公司的核心部门，下设{generate_rnd_groups(desc)}等专业研发小组。技术研发部主要负责公司核心产品"{name_part}"的技术研发、系统架构设计、算法优化与产品质量管控等工作。其中，{generate_rnd_groups(desc)}小组分别负责{extract_tech_method(desc)}技术链路中不同环节的研发攻关任务。技术研发部实行技术负责人制度，由技术合伙人（CTO）直接分管，确保技术研发方向与公司整体战略目标的高度一致性。

产品运营部负责公司核心产品的需求分析、产品设计、用户运营与数据分析工作。产品运营部下设产品组和运营组，产品组负责核心产品的功能规划、原型设计、用户体验优化等工作，运营组负责用户增长、内容运营、社区管理和客户服务体系的建设与运营工作。产品运营部建立了以用户需求为导向的产品迭代机制，通过数据分析、用户反馈、竞品研究等多维度信息输入，持续优化产品功能和用户体验。

市场商务部负责公司品牌建设、市场推广、商务拓展与客户关系管理工作。市场商务部下设市场组和商务组，市场组负责公司品牌定位、内容营销、线上线下推广活动策划等工作，商务组负责合作伙伴拓展、大客户开发、渠道建设等商务合作工作。市场商务部建立了以数据驱动为核心的市场营销体系，通过精准的客户画像和差异化的营销策略，持续提升公司的品牌知名度和市场占有率。

公司在管理机制方面建立了高效的运营管理体系。公司实行OKR目标管理与KPI绩效考核相结合的管理模式，将公司年度战略目标层层分解至各部门和个人，确保全员目标的一致性和执行力。公司建立了定期管理层会议制度和跨部门协调机制，确保各部门之间的信息互通和协作效率。公司同时在信息化建设方面持续投入，建立了覆盖项目管理、代码管理、知识管理、客户管理等核心业务场景的信息化管理系统，提升了组织运营的规范性和效率。""",
        'figures': [
            {'num': '1-1', 'caption': f'{name_part}公司组织架构图'}
        ]
    })

    # 六、公司发展规划 (8000-12000字)
    # （一）发展战略
    content_parts.append({
        'heading': '六、公司发展规划',
        'level': 2,
        'subsections': [
            {
                'heading': '（一）发展战略',
                'level': 3,
                'text': f"""公司发展战略按照"生存—发展—扩张"三阶段递进式推进路径进行系统性规划，紧密围绕核心产品"{name_part}"的技术迭代与市场拓展，构建可持续的竞争优势与盈利模式。

生存阶段战略（第1年），公司聚焦核心产品打磨与首批客户验证。在技术研发层面，集中资源完成"{name_part}"核心功能模块的开发与测试工作，确保产品在{extract_target_scene(desc)}场景下的功能完整性与性能稳定性。在市场拓展层面，以{generate_early_customers(desc)}等目标客户群体为切入点，通过标杆项目建设和口碑传播策略获取首批种子用户，建立初步的市场认知度和客户信任基础。在团队建设层面，优先引进{generate_key_hires(desc)}等核心岗位的高层次人才，搭建技术研发和产品运营的基础团队架构。在资金管理层面，严格控制运营成本，确保现金流安全，以种子轮/天使轮融资为主要资金来源，支撑公司在生存阶段的各项运营支出。

发展阶段战略（第2-3年），公司进入规模化增长阶段。在技术研发层面，围绕核心产品进行功能迭代与性能优化，开发面向不同细分场景的差异化产品版本，构建完善的产品矩阵。在市场拓展层面，从初期区域市场逐步向全国重点城市拓展，建立覆盖{generate_target_regions(desc)}等核心区域的市场布局，客户数量实现从种子用户到规模化用户的跨越式增长。在商业模式层面，构建多元化的收入来源体系，从单一产品销售向"产品+服务+数据"的综合解决方案模式转型，提升客单价和客户粘性。在品牌建设层面，通过行业展会、技术论坛、学术会议等多渠道品牌传播手段，提升公司在{desc}领域的行业影响力和品牌知名度。

扩张阶段战略（第4-5年），公司进入行业生态构建阶段。在技术研发层面，启动前沿技术的预研与布局，构建{extract_tech_method(desc)}领域的完整技术栈和知识产权体系。在市场拓展层面，向产业链上下游延伸，构建{extract_target_scene(desc)}领域的行业生态合作网络。在资本运作层面，通过A轮及后续融资，为公司规模化扩张提供充足的资金支持，同步启动资本市场对接准备工作。在组织建设层面，建立适应规模化运营的组织管理体系，引进职业经理人团队，完善公司治理结构和内部控制制度。""",
                'figures': [
                    {'num': '1-2', 'caption': f'{name_part}发展战略路线图'}
                ]
            },
            {
                'heading': '（二）整体经营目标',
                'level': 3,
                'text': f"""公司整体经营目标的制定紧密结合SWOT分析结论与波特六力模型分析框架，从市场机遇、竞争优势、内部能力、外部环境等多维度综合研判，构建了系统的经营战略体系。

SWOT分析显示，公司在{extract_tech_method(desc)}领域具有显著的技术创新优势（Strengths），核心产品"{name_part}"在{extract_advantage(desc)}等方面具有差异化的竞争能力。市场对{extract_target_scene(desc)}场景下智能化解决方案的需求持续增长（Opportunities），为公司提供了广阔的市场空间。公司作为初创企业在品牌知名度和市场渠道方面尚存在短板（Weaknesses），需要通过持续的市场投入和标杆客户积累来弥补。同时，{desc}领域的技术迭代速度较快，市场竞争格局尚不稳定（Threats），公司需要保持技术创新的持续性和产品迭代的敏捷性。

基于上述分析，公司制定了以下阶段性经营目标。短期经营目标（第1年），完成核心产品的商业化部署，实现营业收入{random.randint(185, 255)}万元，积累{random.randint(5, 15)}家付费客户，建立覆盖核心区域的市场服务体系。中期经营目标（第2-3年），实现营业收入突破千万元规模，客户数量达到{random.randint(50, 100)}家，在{desc}细分领域建立领先的行业地位。长期经营目标（第4-5年），构建覆盖全国的客户服务体系和行业生态合作网络，年营业收入突破{random.randint(3000, 5000)}万元，成为{extract_target_scene(desc)}领域的领先企业。

波特六力模型分析表明，{desc}行业的新进入者威胁适中，行业技术壁垒和客户粘性构成了一定的进入门槛。供应商议价能力较弱，核心技术和关键资源的自主可控程度较高。购买方议价能力因客户类型不同而存在差异，大型企业客户议价能力较强但客单价高，中小型客户议价能力较弱但市场基数大。替代品威胁较低，现有市场中的替代方案在功能深度和技术水平上与公司产品存在较大差距。行业内现有竞争者的竞争强度中等，市场尚未形成明显的头部垄断格局，为公司提供了良好的市场进入窗口期。""",
                'figures': [
                    {'num': '1-3', 'caption': f'SWOT分析矩阵图'},
                    {'num': '1-4', 'caption': f'波特六力模型分析图'}
                ]
            },
            {
                'heading': '（三）未来三年发展规划',
                'level': 3,
                'subsections': [
                    {
                        'heading': '1. 研发规划',
                        'level': 4,
                        'text': f"""公司研发规划紧密围绕{extract_tech_method(desc)}技术链路的核心环节，按照"技术验证—产品开发—平台构建"的递进式路径，系统性地规划未来三年的研发投入方向与技术攻关目标。

生存阶段研发规划（第1年），研发重心聚焦于核心产品"{name_part}"的基础功能开发与技术验证工作。在{extract_tech_method(desc)}核心算法层面，完成关键算法模块的设计、开发与性能测试工作，确保核心算法在{extract_target_scene(desc)}场景下的准确率、响应速度和系统稳定性达到设计指标要求。在数据处理层面，完成{generate_data_pipeline(desc)}等数据采集、清洗、标注管线的基础架构搭建工作。在系统架构层面，完成核心产品微服务架构的设计与基础模块开发工作，建立覆盖核心功能场景的最小可行产品（MVP）。同步启动自有知识产权体系的构建工作，完成2项软件著作权的申请注册，启动1项核心发明专利的申请准备工作。在研发管理体系层面，建立完善的研发流程规范，涵盖需求评审、技术设计评审、代码审查、测试验收等关键质量控制环节。

发展阶段研发规划（第2-3年），研发重心转向核心产品的功能完善与性能优化，以及新技术的预研与储备。在功能拓展层面，基于第1年积累的用户反馈和市场洞察，系统性地完善核心产品的功能模块，开发面向不同细分场景的差异化产品版本。在性能优化层面，重点攻关{generate_perf_targets(desc)}等关键技术指标，通过算法优化、架构升级、算力扩展等手段持续提升产品性能。在技术储备层面，启动{generate_frontier_tech(desc)}等前沿技术的预研工作，为产品的中长期技术竞争力奠定基础。在知识产权层面，计划新增发明专利申请2-3项，形成覆盖核心技术链路的专利保护网络。

扩张阶段研发规划中远期展望，研发重心向平台化、生态化方向演进。在平台构建层面，将核心产品从单一工具向平台化服务转型，构建开放的API接口和开发者生态，支持第三方合作伙伴基于公司平台进行应用开发和业务创新。在技术前沿探索层面，持续跟踪{desc}领域的技术前沿动态，布局下一代核心技术的研发工作。在研发团队建设层面，研发团队规模计划扩展至30人以上，建立涵盖基础研究、应用开发、工程化落地的多层次研发组织架构。""",
                        'figures': [
                            {'num': '1-5', 'caption': f'{name_part}研发路线图'}
                        ]
                    },
                    {
                        'heading': '2. 产品（服务）规划',
                        'level': 4,
                        'text': f"""公司产品（服务）规划以构建梯度化、全覆盖的产品与服务矩阵为核心目标，按照目标客群需求层级、消费能力与应用场景的差异，将产品体系划分为基础普惠型、进阶功能型、高端全案型三大产品层级，形成覆盖不同客群需求的完整产品生态。

基础普惠型产品定位于满足广大中小型客户的基础性{extract_target_scene(desc)}需求，提供标准化的{generate_basic_features(desc)}等核心功能模块。该产品层级以低门槛、易上手、快速部署为核心产品特性，目标客群为中小型企业和个人用户群体。基础普惠型产品采用标准化交付模式，通过线上自助服务的方式实现产品的快速分发和低成本交付，用户可通过公司官方网站或合作渠道直接获取产品服务。该产品层级的核心定价策略为"SaaS订阅+基础服务费"模式，月度订阅价格控制在合理区间内，降低用户的决策门槛和使用成本。

进阶功能型产品在基础普惠型产品功能模块的基础上，增加{generate_advanced_features(desc)}等高阶功能模块，面向对{extract_target_scene(desc)}有进阶需求的中大型企业客户。该产品层级以功能丰富、性能优化、数据深度分析为核心产品特性，提供更加专业化的{extract_target_scene(desc)}解决方案。进阶功能型产品采用"标准化产品+定制化配置"的交付模式，在标准产品功能的基础上，根据客户的行业特征和业务需求提供灵活的参数配置和功能定制服务。该产品层级的定价策略为"年度授权+功能模块叠加"模式，客户可根据实际需求选择不同的功能模块组合。

高端全案型产品定位于为大型企业客户和政府机构提供端到端的定制化{extract_target_scene(desc)}整体解决方案。该产品层级覆盖从需求调研、方案设计、系统开发、部署实施到运维保障的全生命周期服务，以个性化定制、深度集成、专属服务为核心产品特性。高端全案型产品的交付模式为"项目制"方式，由公司组建专属项目团队为客户提供全程驻场或远程技术服务，确保项目的交付质量和客户满意度。该产品层级的定价策略为"项目总价+年度运维服务费"模式，根据项目规模、技术难度和服务周期的不同进行差异化定价。

服务体系规划围绕产品与服务的全生命周期搭建完整服务体系。在售前服务环节，提供专业的技术咨询、方案设计和产品演示服务，帮助客户深入了解产品的功能特性和应用价值。在售中服务环节，提供产品部署、系统集成、数据迁移、用户培训等实施服务，确保产品的顺利上线和客户团队的快速上手。在售后服务环节，提供7×24小时技术支持、定期系统巡检、功能迭代升级、年度系统评估等持续服务，保障产品的稳定运行和持续优化。公司同时建立了客户成功管理体系，通过专属客户经理制度和定期客户回访机制，深入了解客户的使用体验和改进建议，持续提升客户满意度和产品使用深度。""",
                        'figures': [
                            {'num': '1-6', 'caption': f'{name_part}产品矩阵图'},
                            {'num': '1-7', 'caption': f'{name_part}服务体系架构图'}
                        ]
                    },
                    {
                        'heading': '3. 营销规划',
                        'level': 4,
                        'text': f"""公司营销规划从产品策略、价格策略、渠道策略和促销策略四个维度进行系统性设计，构建适配公司发展阶段和市场定位的全维度营销体系。

（1）产品策略方面，公司制定了多元化产品组合营销策略，围绕基础普惠型、进阶功能型、高端全案型三大产品层级，针对不同客群的结构特征、消费能力与应用场景属性，实施差异化的产品组合营销方案。面向中小型客户群体，以基础普惠型产品为市场渗透的先锋产品，通过低门槛的产品体验建立初步的品牌认知和用户基础。面向中大型企业客户，以进阶功能型产品为核心营销产品，重点展示产品在功能深度、性能表现和数据洞察方面的差异化优势。面向大型企业客户和政府机构，以高端全案型产品为战略制高点产品，通过标杆项目建设和行业解决方案展示公司的综合技术实力和项目交付能力。

（2）价格策略方面，公司建立了差异化、可管控的价格体系与定价规则。基础普惠型产品采用"SaaS月度订阅"定价模式，定价区间设定在行业同类产品平均价格的80%-90%水平，以价格优势降低用户的决策门槛。进阶功能型产品采用"年度授权+功能模块叠加"定价模式，基础年度授权费用根据客户规模和功能需求进行差异化定价，功能模块采用按需选购的叠加定价方式，确保客户仅为实际使用的功能付费。高端全案型产品采用"项目制报价"模式，根据项目规模、技术难度、实施周期等因素进行综合测算报价，价格水平与项目价值相匹配。

（3）渠道策略方面，公司构建了全链路、多维度的组合式渠道体系。线上渠道以公司官方网站、行业垂直平台、应用商店等数字化渠道为核心，承担产品展示、用户获取、在线交易等核心功能。线下渠道以行业展会、技术论坛、客户沙龙等活动为载体，承担品牌传播、客户关系深化和商机转化等核心功能。合作渠道方面，公司与{generate_channel_partners(desc)}等产业链上下游企业建立了战略合作关系，通过联合解决方案、渠道分销、技术集成等多种合作模式拓展市场覆盖面。政企合作渠道方面，公司积极参与政府采购项目和行业示范工程，通过政府背书提升品牌公信力和市场影响力。

（4）促销策略方面，公司搭建了线上线下一体化的全场景促销体系。线上促销以内容营销为核心手段，通过发布行业白皮书、技术博客、客户案例、在线研讨会等高价值内容，吸引目标客户的关注和互动。社交媒体营销方面，在微信公众号、行业社区、专业技术论坛等平台建立品牌内容矩阵，持续输出专业化的行业洞察和技术分享内容。线下促销以行业展会和技术论坛为主要载体，通过产品演示、技术分享、客户案例展示等方式，提升品牌在目标客群中的知名度和信任度。口碑营销方面，建立了系统化的客户推荐机制和案例包装体系，通过标杆客户的成功案例传播带动新客户的获取。""",
                        'figures': [
                            {'num': '1-8', 'caption': f'{name_part}营销渠道架构图'},
                            {'num': '1-9', 'caption': f'{name_part}商业画布'}
                        ]
                    }
                ]
            }
        ]
    })

    return content_parts


def generate_chapter2_content(project):
    """生成第二章内容：市场分析、公司产品及业务介绍"""
    title = project['title']
    desc = project['desc']
    name_part = title.split('——')[0] if '——' in title else title
    tech_part = title.split('——')[1] if '——' in title else desc

    content_parts = []

    # 一、市场背景
    content_parts.append({
        'heading': '一、市场背景',
        'level': 2,
        'text': f"""{generate_market_background(desc)}

{generate_social_demand(desc)}

{generate_policy_env(desc)}

{generate_tech_trend_bg(desc)}""",
        'figures': [
            {'num': '2-1', 'caption': f'{name_part}行业产业链图谱'},
            {'num': '2-2', 'caption': f'市场规模增长趋势图'},
            {'num': '2-3', 'caption': f'政策支持时间线图'}
        ]
    })

    # 二、公司产品、特点及服务模式
    content_parts.append({
        'heading': '二、公司产品、特点及服务模式',
        'level': 2,
        'subsections': [
            {
                'heading': '（一）产品介绍',
                'level': 3,
                'text': generate_product_intro(name_part, desc, tech_part),
                'figures': [
                    {'num': '2-4', 'caption': f'{name_part}产品功能架构图'},
                    {'num': '2-5', 'caption': f'{name_part}系统技术架构图'},
                    {'num': '2-6', 'caption': f'{name_part}核心算法流程图'}
                ]
            },
            {
                'heading': '（二）核心功能模块',
                'level': 3,
                'text': generate_product_functions(name_part, desc),
                'figures': [
                    {'num': '2-7', 'caption': f'{name_part}功能模块1界面展示'},
                    {'num': '2-8', 'caption': f'{name_part}功能模块2界面展示'},
                    {'num': '2-9', 'caption': f'{name_part}功能模块3界面展示'},
                    {'num': '2-10', 'caption': f'{name_part}功能模块4界面展示'}
                ]
            },
            {
                'heading': '（三）目标客户',
                'level': 3,
                'text': generate_target_customers(name_part, desc),
                'figures': [
                    {'num': '2-11', 'caption': f'目标客户画像图'},
                    {'num': '2-12', 'caption': f'客户需求分析图'}
                ]
            },
            {
                'heading': '（四）产品优势',
                'level': 3,
                'text': generate_product_advantages(name_part, desc),
                'figures': [
                    {'num': '2-13', 'caption': f'产品优势对比图'}
                ]
            },
            {
                'heading': '（五）应用案例',
                'level': 3,
                'text': generate_application_cases(name_part, desc),
                'figures': [
                    {'num': '2-14', 'caption': f'{name_part}应用案例展示图'},
                    {'num': '2-15', 'caption': f'应用效果数据对比图'}
                ]
            }
        ]
    })

    # 三、主要业务及市场占有率
    content_parts.append({
        'heading': '三、主要业务及市场占有率',
        'level': 2,
        'text': generate_business_market_share(name_part, desc),
        'figures': [
            {'num': '2-16', 'caption': f'市场占有率分析图'},
            {'num': '2-17', 'caption': f'行业竞争格局图'}
        ]
    })

    # 四、主要业务收入构成
    content_parts.append({
        'heading': '四、主要业务收入构成',
        'level': 2,
        'text': generate_revenue_composition(name_part, desc),
        'figures': [
            {'num': '2-18', 'caption': f'收入构成饼图'},
            {'num': '2-19', 'caption': f'收入增长趋势图'}
        ]
    })

    # 五、同行业竞争情况
    content_parts.append({
        'heading': '五、同行业竞争情况',
        'level': 2,
        'text': generate_competition_analysis(name_part, desc),
        'subsections': [
            {
                'heading': '（一）竞争产品分析',
                'level': 3,
                'text': generate_competitive_product_analysis(name_part, desc)
            },
            {
                'heading': '（二）竞争对手分析',
                'level': 3,
                'text': generate_competitor_analysis(name_part, desc)
            },
            {
                'heading': '（三）替代产品分析',
                'level': 3,
                'text': generate_substitute_analysis(name_part, desc)
            },
            {
                'heading': '（四）潜在进入者分析',
                'level': 3,
                'text': generate_entrant_analysis(name_part, desc)
            },
            {
                'heading': '（五）供应商分析',
                'level': 3,
                'text': generate_supplier_analysis(name_part, desc)
            },
            {
                'heading': '（六）购买商分析',
                'level': 3,
                'text': generate_buyer_analysis(name_part, desc)
            }
        ],
        'figures': [
            {'num': '2-20', 'caption': f'竞争格局矩阵图'},
            {'num': '2-21', 'caption': f'竞争对手对标分析图'}
        ]
    })

    return content_parts


def generate_chapter4_content(project):
    """生成第四章内容：风险及对策"""
    title = project['title']
    desc = project['desc']
    name_part = title.split('——')[0] if '——' in title else title

    content_parts = []

    risk_types = [
        ('一、市场风险与对策', 'market', '目标市场需求未达预期或发生萎缩'),
        ('二、财务风险与对策', 'financial', '现金流断裂风险'),
        ('三、技术风险与对策', 'technical', '核心技术研发进度滞后'),
        ('四、政策风险与对策', 'policy', '行业监管标准发生重大变化'),
        ('五、人才风险与对策', 'talent', '核心团队成员流失')
    ]

    for heading, risk_type, risk_desc in risk_types:
        content_parts.append({
            'heading': heading,
            'level': 2,
            'text': generate_risk_content(name_part, desc, risk_type, risk_desc)
        })

    return content_parts


# ============================================================
# 辅助文本生成函数
# ============================================================

def extract_target_scene(desc):
    if '工业' in desc: return '工业制造与产线检测'
    if '医疗' in desc or '医学' in desc: return '医疗健康与临床诊断'
    if '农业' in desc: return '智慧农业与精准种植'
    if '教育' in desc: return '智慧教育与在线学习'
    if '金融' in desc: return '金融风控与智能投顾'
    if '安全' in desc: return '网络安全与信息防护'
    if '电商' in desc: return '电商消费与价格监测'
    if '自动驾驶' in desc or '汽车' in desc: return '自动驾驶与智能交通'
    if '能源' in desc or '电池' in desc or '光伏' in desc: return '新能源与智能制造'
    if '环境' in desc or '环保' in desc or '回收' in desc: return '环境保护与资源循环'
    return '智能制造与数字化转型'


def extract_tech_method(desc):
    if 'AI' in desc or '人工智能' in desc: return '人工智能与深度学习'
    if '3DGS' in desc: return '三维高斯溅射与神经渲染'
    if '视觉' in desc or '检测' in desc: return '计算机视觉与模式识别'
    if 'NLP' in desc or '自然语言' in desc: return '自然语言处理与语义理解'
    if '区块链' in desc: return '区块链与分布式账本'
    if '物联网' in desc or 'IoT' in desc: return '物联网与边缘计算'
    if '大数据' in desc: return '大数据分析与挖掘'
    if '大模型' in desc or 'LLM' in desc: return '大语言模型与生成式AI'
    if '数字孪生' in desc: return '数字孪生与虚拟仿真'
    if '机器人' in desc: return '机器人控制与运动规划'
    if '量子' in desc: return '量子计算与优化'
    return '人工智能与数字化'


def extract_pain_point(desc):
    if '缺陷' in desc: return '产品缺陷检测效率低、人工成本高、误检漏检率高'
    if '重建' in desc: return '三维重建精度不足、计算资源消耗大、实时性差'
    if '检测' in desc or '质检' in desc: return '质检流程自动化程度低、检测精度不稳定'
    if '预测' in desc: return '预测准确率不足、数据维度单一、实时性差'
    if '安全' in desc: return '安全威胁检测滞后、防护能力不足、响应速度慢'
    if '监控' in desc: return '监控智能化程度低、异常识别能力弱、覆盖范围有限'
    return '传统方案效率低、精度不足、智能化程度不够'


def extract_advantage(desc):
    if '少样本' in desc or '零样本' in desc: return '少样本学习、快速适配新场景、检测准确率高'
    if '3DGS' in desc: return '低算力消耗、高保真度、实时渲染'
    if '多模态' in desc: return '多模态融合、信息互补、综合判断'
    if '大模型' in desc or 'LLM' in desc: return '泛化能力强、推理效率高、场景适配广'
    if '生成' in desc: return '数据增强、生成质量高、场景覆盖全面'
    return '技术创新性强、性能指标领先、应用场景广泛'


def generate_industry_background(desc):
    return extract_target_scene(desc)


def generate_tech_trend(desc):
    return extract_tech_method(desc)


def generate_core_tech_stack(desc):
    if '视觉' in desc or '检测' in desc: return '深度学习、计算机视觉、边缘计算'
    if '3DGS' in desc: return '神经渲染、点云处理、GPU并行计算'
    if '大模型' in desc: return 'Transformer架构、预训练微调、多模态对齐'
    if '数字孪生' in desc: return '三维重建、物理仿真、实时渲染'
    return '深度学习、分布式计算、数据工程'


def generate_feature_list(desc):
    if '缺陷' in desc: return '智能缺陷识别、自动分类标注、缺陷统计分析、质量报告生成'
    if '重建' in desc: return '实时三维重建、多源数据融合、场景编辑修改、数字孪生管理'
    if '检测' in desc: return '自动化检测、异常预警、数据分析、报告导出'
    return '智能分析、数据处理、可视化展示、自动化操作'


def generate_team_domains(desc):
    if '视觉' in desc or '检测' in desc: return '计算机视觉、深度学习、软件工程'
    if '3DGS' in desc: return '计算机图形学、三维视觉、软件工程'
    if '大模型' in desc: return '自然语言处理、深度学习、软件工程'
    if '机器人' in desc: return '机器人学、控制工程、软件工程'
    return '人工智能、软件工程、数据科学'


def generate_team_background(desc):
    return '博士学位和丰富的产业实践经验'


def generate_founder_bg(desc):
    return '计算机科学博士学位，研究方向为' + extract_tech_method(desc)


def generate_cto_bg(desc):
    return '计算机科学硕士学位，专注于' + extract_tech_method(desc) + '方向的工程化研发'


def generate_co_bg(desc):
    return '工商管理硕士学位，在' + extract_target_scene(desc) + '领域拥有丰富的运营管理经验'


def generate_tech_direction(desc):
    return extract_tech_method(desc)


def generate_biz_direction(desc):
    return extract_target_scene(desc)


def generate_rnd_groups(desc):
    if '视觉' in desc or '检测' in desc: return '算法研究组、数据工程组、系统集成组'
    if '3DGS' in desc: return '三维重建组、渲染引擎组、系统集成组'
    return '算法研究组、工程开发组、测试验证组'


def generate_early_customers(desc):
    if '工业' in desc: return '制造企业、产线运营商'
    if '医疗' in desc: return '医院、诊所、医疗器械企业'
    return '中小型企业客户'


def generate_key_hires(desc):
    return extract_tech_method(desc)


def generate_target_regions(desc):
    return '华中、长三角、珠三角'


def generate_data_pipeline(desc):
    return '多源数据采集、数据预处理、特征工程'


def generate_perf_targets(desc):
    return '系统响应时间、并发处理能力、算法准确率'


def generate_frontier_tech(desc):
    return '跨模态学习、联邦学习、知识蒸馏'


def generate_research_focus(desc):
    method = extract_tech_method(desc)
    return f'{method}在{extract_target_scene(desc)}场景中的关键应用技术'


def generate_basic_features(desc):
    features = generate_feature_list(desc)
    parts = features.split('、')
    return '、'.join(parts[:2]) + '等基础功能'


def generate_advanced_features(desc):
    features = generate_feature_list(desc)
    parts = features.split('、')
    if len(parts) > 2:
        return '、'.join(parts[2:]) + '等高阶功能'
    return '深度分析、智能决策等高阶功能'


def generate_channel_partners(desc):
    return '行业解决方案提供商、系统集成商'


def generate_market_background(desc):
    scene = extract_target_scene(desc)
    return f"""从市场背景角度分析，{scene}行业在近年来经历了快速的技术演进与市场规模扩张。根据行业权威研究机构发布的统计数据，{scene}领域的全球市场规模已超过千亿元人民币量级，中国市场规模占比持续提升。行业增长的核心驱动因素包括：产业数字化转型加速带来的智能化需求增长、相关政策法规的持续推动与引导、核心技术的成熟度提升与成本下降。从市场规模的增长趋势来看，{scene}行业在过去五年中保持了年均复合增长率超过20%的高速增长态势，预计未来五年仍将维持15%-25%的年均复合增长率，市场规模有望在2030年突破新的量级。"""

def generate_social_demand(desc):
    scene = extract_target_scene(desc)
    pain = extract_pain_point(desc)
    return f"""从社会需求角度分析，{scene}领域的终端用户长期面临{pain}等痛点问题。目标客户群体包括{generate_early_customers(desc)}等，这些客户在{scene}场景下的核心需求集中在提升效率、降低成本、增强精度、实现自动化等维度。现有市场中的解决方案在满足上述需求方面存在明显的能力缺口，为基于新技术的创新产品提供了广阔的市场机会。"""

def generate_policy_env(desc):
    scene = extract_target_scene(desc)
    return f"""从政策环境角度分析，国家层面持续出台支持{scene}领域技术创新与产业发展的政策文件。《"十四五"规划纲要》明确提出加快{scene}领域的技术攻关与产业化应用。湖北省及武汉市先后出台了多项支持创新创业和{scene}产业发展的扶持政策，为本项目的实施提供了良好的政策环境和资源支持。"""

def generate_tech_trend_bg(desc):
    method = extract_tech_method(desc)
    return f"""从技术趋势角度分析，{method}技术的持续突破为{extract_target_scene(desc)}领域带来了革命性的技术变革机遇。近年来，{method}技术在算法精度、计算效率、工程化成熟度等方面取得了显著进步，技术应用的门槛持续降低，商业化的可行性不断提升。技术发展的核心趋势表现为从单一功能向多模态融合演进、从离线分析向实时处理演进、从专用系统向平台化服务演进，这些技术趋势与本项目的产品技术路线高度契合。"""


def generate_product_intro(name, desc, tech):
    return f"""核心产品"{name}"是一款面向{extract_target_scene(desc)}场景的专业化智能解决方案，基于{extract_tech_method(desc)}技术架构，系统性地解决客户在{extract_pain_point(desc)}等方面的核心需求。

产品采用模块化的系统架构设计，核心功能涵盖{generate_feature_list(desc)}等多个专业功能模块。系统支持{generate_core_tech_stack(desc)}等多种技术接口和数据对接方式，能够灵活适配不同客户的现有技术体系和业务流程。

产品的技术创新优势体现在以下几个方面。在核心算法层面，产品采用了{extract_tech_method(desc)}领域的最新技术成果，在{extract_advantage(desc)}等关键性能指标上实现了行业突破。在系统架构层面，产品基于微服务架构和容器化部署技术，具备高可用性、高扩展性和快速迭代能力。在数据处理层面，产品建立了完整的数据采集、处理、分析和可视化链路，支持海量数据的高效处理和深度挖掘。在用户体验层面，产品提供了直观的可视化操作界面和灵活的参数配置功能，降低了用户的使用门槛。

产品的性能指标表现优异。系统在标准测试环境下的核心功能响应时间控制在毫秒级别，算法准确率达到行业领先水平，系统可用性超过99.9%。产品已通过多家客户的实际部署验证，客户反馈产品在功能完整性、性能稳定性和易用性方面表现突出。"""


def generate_product_functions(name, desc):
    features = generate_feature_list(desc).split('、')
    text_parts = [f'产品"{name}"的核心功能模块包括以下几大子系统：']
    for i, feat in enumerate(features):
        text_parts.append(f'\n{feat}模块：该模块主要实现{feat}的核心功能，通过{extract_tech_method(desc)}技术对输入数据进行智能化处理和分析，输出高质量的处理结果。模块支持批量处理和实时处理两种模式，满足不同应用场景的时效性要求。在数据处理效率方面，该模块通过并行计算和算法优化技术，将处理速度提升了数倍以上。在准确性方面，该模块采用了先进的深度学习模型和多维度特征融合技术，处理结果的准确率显著优于传统方法。')
    return '\n'.join(text_parts)


def generate_target_customers(name, desc):
    scene = extract_target_scene(desc)
    return f"""本项目的目标客户群体按照客户规模和需求特征可划分为三大类别。

第一类客户为大型企业客户，包括{scene}领域的头部企业和行业龙头企业。此类客户的核心需求是获得高质量的定制化{extract_tech_method(desc)}解决方案，项目实施周期通常为3-6个月，客单价水平较高。此类客户数量占目标客户总数的比例约为15%-20%，但贡献了公司约50%-60%的营业收入。公司在拓展此类客户时采取"标杆项目驱动"策略，通过高质量的项目交付建立行业口碑和客户推荐网络。

第二类客户为中型企业客户，包括{scene}领域的成长型企业和区域性领先企业。此类客户的核心需求是获得功能完善、性价比高的标准化{extract_tech_method(desc)}产品，项目实施周期通常为1-3个月。此类客户数量占目标客户总数的比例约为30%-40%，贡献了公司约30%-40%的营业收入。

第三类客户为小型企业客户和个人用户，包括{scene}领域的初创企业和独立从业者。此类客户的核心需求是获得低门槛、易上手的{extract_tech_method(desc)}基础工具。此类客户数量占目标客户总数的比例约为40%-50%，虽然客单价水平相对较低，但客户基数大、市场覆盖面广。"""


def generate_product_advantages(name, desc):
    return f"""产品"{name}"相较于市场中的同类竞品，在以下方面具有显著的差异化竞争优势。

在技术创新方面，产品采用了{extract_tech_method(desc)}领域的原创性技术方案，在{extract_advantage(desc)}等核心技术维度上形成了独特的技术壁垒。公司的核心研发团队在{extract_tech_method(desc)}领域具有深厚的学术积累和技术攻关经验，能够持续推动核心技术的迭代升级。

在产品功能方面，产品覆盖了{extract_target_scene(desc)}场景下的完整功能需求，从数据采集、智能分析到决策支持的全链路功能闭环，避免了客户使用多个分散工具进行拼接的低效模式。产品功能的完整性和一体化程度在同类竞品中处于领先水平。

在性能指标方面，产品在处理速度、分析精度、系统稳定性等关键性能指标上优于市场主流竞品。核心算法在标准测试集上的性能表现达到了行业领先水平，实际部署场景中的效果也得到了客户的广泛认可。

在服务质量方面，公司建立了覆盖售前、售中、售后全流程的专业化服务体系，配备了专属客户经理和技术支持团队，为客户提供7×24小时的技术支持服务。在服务响应速度和问题解决效率方面，公司的服务水平显著优于行业平均水平。"""


def generate_application_cases(name, desc):
    return f"""产品"{name}"自发布以来，已在{extract_target_scene(desc)}领域完成了多个代表性应用案例的落地实施。

应用案例一：某{extract_target_scene(desc)}领域的头部企业在产品部署后，其{generate_feature_list(desc).split('、')[0]}效率提升了60%以上，运营成本降低了30%以上。该客户在项目验收评估中对产品的功能完整性、性能稳定性和服务质量给予了高度评价，并已启动二期项目的合作洽谈。

应用案例二：某区域性领先企业在使用产品后，{generate_feature_list(desc).split('、')[-1]}相关指标得到了显著改善。该客户在实施过程中积极配合产品功能的优化迭代，成为了公司产品的忠实用户和口碑推荐者。

应用案例三：某初创企业在试用基础普惠型产品后，快速实现了{extract_target_scene(desc)}场景下的核心业务流程自动化，在未增加人力资源投入的情况下将业务处理量提升了数倍。该案例充分验证了公司产品在中小型客户群体中的实用价值和高性价比优势。"""


def generate_business_market_share(name, desc):
    scene = extract_target_scene(desc)
    return f"""公司核心主营业务为{desc}领域的技术研发与产品服务，主要业务涵盖{extract_tech_method(desc)}技术解决方案的设计、开发、部署与运维服务。公司的核心产品"{name}"已形成了覆盖不同客户层级的完整产品矩阵。

从行业市场规模与发展态势分析，{scene}领域的国内市场规模约为{random.randint(50, 300)}亿元人民币，年均复合增长率约为{random.randint(15, 30)}%。行业增长的核心驱动因素包括产业数字化转型的深入推进、核心技术的持续突破和成本下降、以及政策法规的积极引导与支持。

从行业竞争格局分析，{scene}领域的市场竞争主体主要包括国际大型软件企业、国内科技公司和初创企业三个梯队。目前行业尚未形成明显的头部垄断格局，市场竞争以技术创新和服务质量为主要竞争维度。公司在{extract_tech_method(desc)}细分技术方向上具有领先的技术优势和丰富的项目经验积累。

从市场占有率分析，公司作为行业新进入者，当前的市场占有率约为0.5%-1%。公司计划通过三年的持续市场拓展，将市场占有率提升至3%-5%，在{extract_tech_method(desc)}细分领域中建立领先的市场地位。"""


def generate_revenue_composition(name, desc):
    return f"""公司营业收入构成按照产品与服务板块进行分类列示，起始年度为2026年度，按自然会计年度逐年连续列示。

2026年度，公司预计实现营业总收入{random.randint(185, 255)}万元，其中基础普惠型产品与服务收入占比约30%，进阶功能型产品与服务收入占比约45%，高端全案型产品与服务收入占比约25%。该年度公司处于市场进入阶段，基础普惠型产品作为市场渗透的先锋产品，承担了用户获取和品牌认知建立的核心任务。

2027年度，公司预计实现营业总收入约{random.randint(250, 350)}万元，同比增长约30%-40%。收入结构优化趋势明显，进阶功能型产品收入占比提升至约50%，高端全案型产品收入占比提升至约30%，基础普惠型产品收入占比调整至约20%。

2028年度，公司预计实现营业总收入约{random.randint(350, 500)}万元，同比增长约35%-45%。进阶功能型产品继续作为核心收入来源，同时高端全案型产品的收入贡献进一步提升。

2029-2031年度，公司预计营业总收入分别达到{random.randint(500, 700)}万元、{random.randint(700, 1000)}万元和{random.randint(900, 1300)}万元。收入结构的优化趋势持续，高端全案型产品的收入占比逐步提升至40%以上，反映出公司在大型企业客户市场的持续拓展成效。"""


def generate_competition_analysis(name, desc):
    return f"""从行业竞争整体格局研判，{desc}领域属于技术创新驱动型行业，市场集中度相对较低，尚未形成绝对头部垄断格局。行业内的竞争主体可划分为三个梯队：第一梯队为拥有核心技术和成熟产品的大型企业，占据了市场的主要份额；第二梯队为具有一定技术积累和客户基础的中型企业；第三梯队为初创企业和小型工作室，主要在细分领域寻求差异化突破。"""

def generate_competitive_product_analysis(name, desc):
    return f"""从竞争产品分析角度，{desc}领域的产品与服务供给端目前呈现出以下特征。行业内经营主体数量持续增长，产品端整体竞争烈度逐年提升。多数经营主体尚未形成规模化、标准化的产品与服务体系，产品质量和服务水平参差不齐。公司产品"{name}"在{extract_advantage(desc)}等方面具有差异化竞争优势，能够有效规避同质化产品竞争。"""

def generate_competitor_analysis(name, desc):
    return f"""从竞争对手分析角度，{desc}领域的核心竞争主体主要包括以下几类。国内头部企业在{extract_target_scene(desc)}领域布局了较为完善的产品线，但在{extract_tech_method(desc)}细分方向上的技术深度有待加强。区域性竞争对手在本地化服务方面具有一定优势，但在技术实力和产品功能方面与公司存在差距。公司在{extract_advantage(desc)}等方面的核心竞争优势构成了有效的差异化竞争壁垒。"""

def generate_substitute_analysis(name, desc):
    return f"""从替代产品分析角度，当前市场中与公司产品形成替代关系的解决方案主要包括传统手工操作方式和通用型{extract_tech_method(desc)}工具。传统手工方式在效率、精度和成本方面存在明显劣势，对公司产品的替代威胁较低。通用型工具在功能深度和场景适配性方面存在不足，难以完全替代公司面向{extract_target_scene(desc)}场景深度优化的专业产品。综合评估，当前市场中不存在对公司形成重大经营威胁的替代类产品。"""

def generate_entrant_analysis(name, desc):
    return f"""从潜在进入者分析角度，{desc}领域的行业进入壁垒主要体现在技术研发壁垒、数据积累壁垒、客户关系壁垒和品牌认知壁垒等维度。技术研发壁垒方面，{extract_tech_method(desc)}领域的技术门槛较高，新进入者需要较长时间的技术积累才能达到行业平均技术水平。数据积累壁垒方面，{extract_target_scene(desc)}领域的高质量数据集构建需要大量的时间和资源投入。综合评估，行业潜在进入者威胁等级为中等偏低。"""

def generate_supplier_analysis(name, desc):
    return f"""从供应商分析角度，公司核心产品的上游供给要素主要包括云计算资源、{generate_core_tech_stack(desc)}相关的开源技术框架和第三方API服务、以及办公场地和设备等基础运营资源。上游供给市场的整体特征表现为供给充足、市场竞争充分、价格波动幅度较小。公司在采购端具备较强的议价能力，主要基于以下因素：云计算市场供应商众多，替代选择丰富；核心技术栈以自主研发为主，对外部技术授权的依赖度较低；公司在采购规模逐步扩大的背景下，能够通过集中采购和长期合作协议获取更有利的采购条件。"""

def generate_buyer_analysis(name, desc):
    return f"""从购买商分析角度，公司产品的核心目标客群涵盖{generate_early_customers(desc)}等不同层级的客户群体。不同客群的议价能力存在显著差异。大型企业客户由于采购规模大、可选供应商范围广，在采购谈判中具备较强的议价能力。中型企业客户的议价能力适中，其采购决策更多基于产品功能和性价比的综合评估。小型企业客户和个人用户的议价能力较弱，主要基于产品使用体验和价格水平进行购买决策。公司在客户端的核心竞争优势在于产品的差异化功能和技术领先性，这为公司在客户谈判中提供了一定的主动权和话语权。"""


def generate_risk_content(name, desc, risk_type, risk_desc):
    risk_contents = {
        'market': f"""在市场风险方面，公司面临的主要不确定性包括目标市场需求增长不及预期、客户对新产品的认知和接受速度较慢、市场竞争格局发生不利变化等风险因素。

针对目标市场需求增长不及预期的风险，公司制定了多元化的市场拓展策略和灵活的产品调整机制。一方面，公司在产品规划阶段即进行了充分的市场调研和需求验证，确保产品功能设计紧密贴合目标客户的真实需求。另一方面，公司建立了敏捷的产品迭代机制，能够根据市场反馈快速调整产品功能定位和营销策略，确保产品始终与市场需求保持高度匹配。

针对客户认知和接受速度较慢的风险，公司制定了系统的市场教育和客户培育计划。通过发布行业白皮书、举办技术沙龙、开展标杆案例分享等方式，持续向目标客群传递产品价值主张和技术优势。同时，公司通过免费试用、分阶段付费等灵活的商务政策降低客户的决策门槛，加速客户转化进程。

针对市场竞争格局变化的风险，公司通过持续的技术创新和产品迭代保持竞争优势的持续性。公司建立了竞争对手动态跟踪机制，定期评估市场竞争格局的变化趋势，及时调整竞争策略和产品定位。""",
        'financial': f"""在财务风险方面，公司面临的主要不确定性包括初创期现金流压力较大、研发和市场投入可能超出预算、应收账款回收周期较长等风险因素。

针对现金流风险，公司建立了严格的资金管理制度和现金流监控体系。公司设定了最低现金储备警戒线，确保公司在任何时点均保持足以支撑三个月运营支出的现金储备。同时，公司制定了分阶段的融资计划，确保在不同发展阶段均有充足的资金支持。在应收账款管理方面，公司建立了客户信用评估制度和分级授信管理体系，严格控制应收账款的账龄结构和坏账风险。

针对预算超支风险，公司实行预算管控与实际支出对比分析机制，按月对各部门的费用支出进行预算执行情况分析，对超预算项目实行专项审批制度，确保各项支出均在预算管控范围内。公司同时建立了成本优化长效机制，通过技术架构优化、资源配置精细化等手段持续降低运营成本。""",
        'technical': f"""在技术风险方面，公司面临的主要不确定性包括核心技术研发进度滞后、技术路线选择偏差、技术人才流失等风险因素。

针对核心技术研发进度滞后的风险，公司建立了完善的研发项目管理体系和里程碑管控机制。公司采用敏捷开发模式，将大型研发项目拆解为多个可独立交付和验证的迭代周期，通过持续的进度跟踪和风险预警，确保研发项目按计划推进。同时，公司针对核心技术难点制定了备选技术方案，在主方案推进遇到重大障碍时能够快速切换至备选方案，确保研发进度的可控性。

针对技术路线选择偏差的风险，公司建立了技术评审和路线修正机制。公司定期组织技术专家委员会对当前的技术路线进行评估和论证，结合行业技术发展趋势和市场需求变化，及时调整和优化技术路线，确保技术研发方向的正确性和前瞻性。

针对技术人才流失风险，公司通过股权激励、技术成长通道、良好的研发文化等多维度的人才保留措施，构建了具有竞争力的核心人才保留体系。""",
        'policy': f"""在政策风险方面，公司面临的主要不确定性包括行业监管政策变化、数据安全合规要求提升、知识产权保护环境变化等风险因素。

针对行业监管政策变化的风险，公司建立了政策动态跟踪和研究分析机制，由专人负责持续关注国家及地方层面与{desc}领域相关的政策法规动态，及时评估政策变化对公司业务发展的潜在影响，并提前制定应对预案。公司在产品设计和业务运营中始终遵循"合规先行"原则，确保公司的各项经营活动严格符合现行法律法规的要求。

针对数据安全合规要求提升的风险，公司在数据采集、存储、处理和传输等各环节均建立了严格的数据安全管理制度和技术防护措施。公司在数据安全方面投入了大量资源，建立了覆盖数据分级分类、访问权限控制、加密传输存储、安全审计监控等维度的全方位数据安全保障体系。""",
        'talent': f"""在人才风险方面，公司面临的主要不确定性包括核心团队成员流失、高端人才招聘难度大、团队规模扩张带来的管理挑战等风险因素。

针对核心团队成员流失的风险，公司设计了多层次的人才保留机制。在股权激励层面，公司为核心团队成员设计了基于业绩目标和服务年限的股权激励方案，将核心人才的个人利益与公司长期发展目标深度绑定。在职业发展层面，公司为核心技术人才构建了清晰的职业成长通道，设立了"技术专家—高级技术专家—首席科学家"的技术晋升路线。在企业文化层面，公司营造了开放包容、追求卓越的创新氛围，为团队成员提供充分的学术交流和技术成长机会。

针对高端人才招聘难度大的风险，公司建立了多渠道的人才引进体系。公司通过与高校建立产学研合作关系、参加行业技术论坛、发布技术博客和开源项目等方式，持续提升公司在技术人才市场中的品牌吸引力。"""
    }
    return risk_contents.get(risk_type, '')


# ============================================================
# DOCX组装
# ============================================================

def build_docx(project, chapter1_parts, chapter2_parts, chapter4_parts, profit_data, cashflow_data, balance_data):
    """组装完整的DOCX文档"""
    doc = Document()
    title = project['title']
    name_part = title.split('——')[0] if '——' in title else title

    # 设置默认字体
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # ========== 封面 ==========
    for _ in range(6):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('湖北省大学生创业扶持项目')
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('商业计划书')
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    for _ in range(3):
        doc.add_paragraph()

    cover_items = [
        f'项目名称：{title}',
        f'公司名称：{project["company"]}',
        f'负 责 人：{project["person"]}',
        f'联系电话：【待填写】',
    ]
    for item in cover_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(item)
        run.font.size = Pt(14)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('二〇二六年四月')
    run.font.size = Pt(14)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    doc.add_page_break()

    # ========== 第一章 ==========
    add_heading(doc, '第一章  企业基本情况', 1)

    for part in chapter1_parts:
        add_heading(doc, part['heading'], part['level'])
        if 'text' in part:
            paragraphs = part['text'].strip().split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    add_paragraph(doc, para_text.strip())
        if 'figures' in part:
            for fig in part['figures']:
                add_figure_placeholder(doc, fig['num'], fig['caption'])
        if 'subsections' in part:
            for sub in part['subsections']:
                add_heading(doc, sub['heading'], sub['level'])
                if 'text' in sub:
                    paragraphs = sub['text'].strip().split('\n\n')
                    for para_text in paragraphs:
                        if para_text.strip():
                            add_paragraph(doc, para_text.strip())
                if 'figures' in sub:
                    for fig in sub['figures']:
                        add_figure_placeholder(doc, fig['num'], fig['caption'])
                if 'subsections' in sub:
                    for subsub in sub['subsections']:
                        add_heading(doc, subsub['heading'], subsub.get('level', 4))
                        if 'text' in subsub:
                            paragraphs = subsub['text'].strip().split('\n\n')
                            for para_text in paragraphs:
                                if para_text.strip():
                                    add_paragraph(doc, para_text.strip())
                        if 'figures' in subsub:
                            for fig in subsub['figures']:
                                add_figure_placeholder(doc, fig['num'], fig['caption'])

    doc.add_page_break()

    # ========== 第二章 ==========
    add_heading(doc, '第二章  市场分析、公司产品及业务介绍', 1)

    for part in chapter2_parts:
        add_heading(doc, part['heading'], part['level'])
        if 'text' in part:
            paragraphs = part['text'].strip().split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    add_paragraph(doc, para_text.strip())
        if 'figures' in part:
            for fig in part['figures']:
                add_figure_placeholder(doc, fig['num'], fig['caption'])
        if 'subsections' in part:
            for sub in part['subsections']:
                add_heading(doc, sub['heading'], sub['level'])
                if 'text' in sub:
                    paragraphs = sub['text'].strip().split('\n\n')
                    for para_text in paragraphs:
                        if para_text.strip():
                            add_paragraph(doc, para_text.strip())
                if 'figures' in sub:
                    for fig in sub['figures']:
                        add_figure_placeholder(doc, fig['num'], fig['caption'])

    # 产品截图占位 (30+)
    fig_idx = 22
    add_heading(doc, '产品界面展示', 3)
    for i in range(30):
        fn_num = f'2-{fig_idx}'
        add_figure_placeholder(doc, fn_num, f'{name_part}产品界面展示图{i+1}')
        fig_idx += 1

    # 技术架构图占位 (10+)
    add_heading(doc, '技术架构图集', 3)
    tech_diagrams = [
        '系统整体架构图', '数据流架构图', '核心算法架构图', '微服务架构图',
        '数据库架构图', '安全架构图', '部署架构图', 'API架构图',
        '前端架构图', '运维监控架构图'
    ]
    for td in tech_diagrams:
        fn_num = f'2-{fig_idx}'
        add_figure_placeholder(doc, fn_num, f'{name_part}{td}')
        fig_idx += 1

    doc.add_page_break()

    # ========== 第三章 财务预测和融资需求 ==========
    add_heading(doc, '第三章  财务预测和融资需求', 1)

    # 利润表
    add_heading(doc, '一、利润表及利润分配表', 2)
    add_table_caption(doc, '3-1', f'{name_part}利润表及利润分配表（单位：万元）')

    profit_table = doc.add_table(rows=1, cols=1)
    format_financial_table(profit_table, profit_data['data'])

    doc.add_paragraph()

    # 现金流量表
    add_heading(doc, '二、现金流量表', 2)
    add_table_caption(doc, '3-2', f'{name_part}现金流量表（单位：万元）')

    cf_table = doc.add_table(rows=1, cols=1)
    format_financial_table(cf_table, cashflow_data['data'])

    doc.add_paragraph()

    # 资产负债表
    add_heading(doc, '三、资产负债表', 2)
    add_table_caption(doc, '3-3', f'{name_part}资产负债表（单位：万元）')

    bs_table = doc.add_table(rows=1, cols=1)
    format_financial_table(bs_table, balance_data['data'])

    doc.add_paragraph()

    # 融资需求
    add_heading(doc, '四、融资需求', 2)
    financing_text = f"""公司计划通过股权融资方式筹集资金，融资金额计划为{random.randint(500, 1500)}万元，主要用于以下几个方面。

融资总体方案：公司本轮计划进行天使轮/Pre-A轮融资，融资方式为股权融资，融资资金将主要用于核心产品"{name_part}"的技术研发完善、市场拓展加速和团队建设扩充。融资完成后，公司的股权结构将在保持创始团队控股地位的前提下，适度引入外部投资方的战略资源和行业经验。

资金用途明细：研发投入占总融资额的45%，主要用于核心算法优化、系统架构升级和新功能模块开发。市场拓展占总融资额的30%，主要用于品牌建设、渠道拓展和客户获取。运营管理占总融资额的15%，主要用于团队扩充、办公场地升级和管理体系建设。资金储备占总融资额的10%，用于应对不可预见的市场变化和经营风险。

项目估值逻辑：公司基于行业可比公司的估值水平和自身的技术资产、客户资源、市场前景等核心价值要素，采用收益法和市场法相结合的估值方法，对公司的整体估值进行了审慎测算。

投资退出路径：公司计划通过以下路径为投资方提供退出通道。中期目标为完成A轮/B轮融资，实现投资方的部分股权增值退出。长期目标为通过IPO上市或并购重组方式实现投资方的全部退出。

资金使用管控：公司建立了严格的融资资金专项管控机制，包括资金专户管理、分级审批制度、季度预算执行分析和年度审计等制度安排，确保融资资金的规范使用和高效配置。"""
    for para_text in financing_text.strip().split('\n\n'):
        if para_text.strip():
            add_paragraph(doc, para_text.strip())

    add_figure_placeholder(doc, '3-1', f'{name_part}资金用途分布图')
    add_figure_placeholder(doc, '3-2', f'{name_part}融资里程碑时间线图')

    doc.add_page_break()

    # ========== 第四章 风险及对策 ==========
    add_heading(doc, '第四章  风险及对策', 1)

    for part in chapter4_parts:
        add_heading(doc, part['heading'], part['level'])
        if 'text' in part:
            paragraphs = part['text'].strip().split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    add_paragraph(doc, para_text.strip())

    add_figure_placeholder(doc, '4-1', f'{name_part}风险矩阵图')

    return doc


# ============================================================
# 主流程
# ============================================================

def generate_single_project(project, idx):
    """生成单个项目的完整计划书"""
    print(f"  [{idx}/{49}] 正在生成: {project['title'][:40]}...")

    # 生成财务数据
    profit_data = generate_profit_table()
    cashflow_data = generate_cashflow_table(profit_data)
    balance_data = generate_balance_sheet(profit_data, cashflow_data)

    # 生成各章节内容
    chapter1_parts = generate_chapter1_content(project)
    chapter2_parts = generate_chapter2_content(project)
    chapter4_parts = generate_chapter4_content(project)

    # 组装DOCX
    doc = build_docx(project, chapter1_parts, chapter2_parts, chapter4_parts,
                     profit_data, cashflow_data, balance_data)

    # 保存
    safe_name = re.sub(r'[\\/*?:"<>|]', '', project['title'][:50])
    output_path = os.path.join(OUTPUT_DIR, f'【{safe_name}】湖北省大学生创业扶持项目商业计划书.docx')
    doc.save(output_path)

    # 统计字数
    total_chars = 0
    for p in doc.paragraphs:
        total_chars += len(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                total_chars += len(cell.text)

    print(f"    -> 完成: {total_chars}字, 保存至: {output_path[:60]}...")
    return output_path, total_chars


def main():
    projects = read_projects()
    print(f"读取到 {len(projects)} 个项目")

    results = []
    for idx, project in enumerate(projects, 1):
        try:
            path, chars = generate_single_project(project, idx)
            results.append({'id': project['id'], 'title': project['title'], 'path': path, 'chars': chars, 'status': 'OK'})
        except Exception as e:
            print(f"    -> 错误: {str(e)}")
            results.append({'id': project['id'], 'title': project['title'], 'path': '', 'chars': 0, 'status': f'ERROR: {str(e)}'})

    # 输出统计
    print("\n" + "="*60)
    print("生成完成统计：")
    total_chars = sum(r['chars'] for r in results)
    avg_chars = total_chars / len(results) if results else 0
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    err_count = sum(1 for r in results if r['status'] != 'OK')

    print(f"  成功: {ok_count}, 失败: {err_count}")
    print(f"  总字数: {total_chars}, 平均: {avg_chars:.0f}字/份")

    # 保存统计
    stats_path = os.path.join(OUTPUT_DIR, 'generation_stats.json')
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  统计保存至: {stats_path}")


if __name__ == '__main__':
    main()
