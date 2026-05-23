/**
 * generate_all.js
 * 为49个项目生成商业计划书图表PPT
 * 每个项目一个PPT，包含38页幻灯片（每张图一页）
 * 使用PptxGenJS + 莫兰迪配色 + 项目专属数据
 */
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const OUT = path.join("D:", "计划书AI", "output_v2", "charts_pptx");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const DATA_DIR = path.join("D:", "计划书AI", "pptx_charts", "project_data");

// ============= 莫兰迪色板集合 =============
const COLOR_SCHEMES = [
  // 0: 经典蓝灰
  { bg: "F5F0EB", bgGroup: "EDE8E2", bgGroup2: "E8E3DD", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D8D2CC",
    s: ["A8B5C4","C4B7A6","B5C4B1","D4B5B5","B0A8C4","A6C4C4","C4C4A6","C4B8A6","B8B8C4","C4A6A6"],
    d: ["6B7B8C","8C7B6B","7B8C76","947676","7B6B8C","6B8C8C","8C8C6B","8C7B6B","76768C","8C6B6B"] },
  // 1: 暖橙大地
  { bg: "F5F0EB", bgGroup: "EDE8E2", bgGroup2: "E8E3DD", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D8D2CC",
    s: ["C4A882","B8A890","C4B896","A8B094","C4A8A0","A0A8B0","B0B4A0","C4B0A0","A8B8B0","B0A8B8"],
    d: ["8C6B4A","7B6B5A","8C7B5A","5A6B4A","8C5A50","4A5A6B","5A5A4A","8C5A4A","4A6B6B","5A4A6B"] },
  // 2: 清新绿调
  { bg: "F0F2EB", bgGroup: "E5E8DD", bgGroup2: "DDE3D5", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D0D5C8",
    s: ["A3B899","B8C4A8","A8C4B0","C4B8A3","A8B8C4","B0C4C4","C4C4A8","C4B0A8","B0B8C4","C4A8B0"],
    d: ["5A6B4A","6B7B5A","5A7B6B","7B6B4A","4A5A6B","5A6B6B","6B6B4A","6B5A4A","4A4A6B","6B4A5A"] },
  // 3: 紫罗兰调
  { bg: "F2EFF5", bgGroup: "E8E3ED", bgGroup2: "E0DBE5", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D5D0DD",
    s: ["B0A8C4","C4A8C4","A8B4C4","C4B8B8","B8B8C4","A8C4C4","C4C4A8","C4B0A8","B0C4B8","C4A8B0"],
    d: ["6B5A7B","7B5A7B","4A5A6B","7B5A5A","5A5A7B","4A6B6B","6B6B4A","6B4A4A","5A6B4A","6B4A5A"] },
  // 4: 暖粉棕调
  { bg: "F5EFEF", bgGroup: "EDE3E3", bgGroup2: "E5D8D8", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D8C8C8",
    s: ["C4A8A8","C4B0A0","B8A8B0","C4B8A8","A8B8B8","B0B0C4","C4C4B0","B0C4B0","C4A8B8","B8C4B8"],
    d: ["7B4A4A","7B5A40","5A4050","7B5A4A","4A5A5A","4A4A6B","6B6B40","4A6B4A","6B4A5A","4A6B4A"] },
  // 5: 深海蓝调
  { bg: "EBEFF5", bgGroup: "DDE5ED", bgGroup2: "D5DDE5", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "C8D0D8",
    s: ["8CA8C4","A8B8C4","94A8B8","B0A8B8","A8C4C4","B8B8A8","C4B8A8","B0C4B0","A8B0C4","C4A8A8"],
    d: ["3A5A6B","4A5A6B","3A4A5A","5A4A5A","4A6B6B","5A5A4A","6B4A4A","4A6B4A","4A4A6B","6B4A4A"] },
  // 6: 土黄自然
  { bg: "F5F2EB", bgGroup: "EDE8DD", bgGroup2: "E5E0D5", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D8D0C0",
    s: ["C4B896","B8A880","A8B090","C4A890","B0A8A0","A0B0B0","C4B0A0","A8B8A8","B8B0A8","B0B0A8"],
    d: ["6B5A30","5A4A20","4A5A30","6B4A30","504040","405050","6B4A30","4A5A4A","5A4A30","404030"] },
  // 7: 薄荷清新
  { bg: "EFF5F2", bgGroup: "E3EDE8", bgGroup2: "D8E5E0", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "C8D8D0",
    s: ["94C4B0","A8C4B8","B0C4A8","A8B8C4","B8C4C4","C4B8A8","C4A8B0","B0B0C4","B8B8A8","C4C4B0"],
    d: ["2A6B50","3A6B50","4A6B3A","3A4A6B","4A6B6B","6B5A3A","6B3A4A","4A4A6B","4A4A3A","6B6B3A"] },
  // 8: 玫瑰豆沙
  { bg: "F5EFF0", bgGroup: "EDE3E5", bgGroup2: "E5D8DA", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "D8C8CC",
    s: ["C4A8B0","C4B0B8","B8A8B0","C4B8B0","B0B0C4","A8C4C4","C4C4B0","B0C4B0","C4A8A8","B8C4B8"],
    d: ["6B3A4A","6B4A5A","5A4A40","6B5A40","4A4A6B","3A6B6B","6B6B40","3A6B3A","6B3A3A","3A6B3A"] },
  // 9: 青石灰调
  { bg: "EFF2F5", bgGroup: "E3E8ED", bgGroup2: "D8DDE0", title: "3D3D3D", sub: "5A5A6A", body: "4A4A5A", white: "FFFFFF", light: "FAF8F5", border: "C8D0D5",
    s: ["A0A8B0","B0B0B8","A8B0B8","B8B0A8","B0B8A8","A8B8B0","B0A8B0","A8B0C4","C4B8A0","B0A8C4"],
    d: ["3A4048","484850","404848","484840","404840","404840","483848","404058","584830","403858"] }
];

// 幻灯片尺寸 16:9
const SW = 10, SH = 5.625;

// ============= 工具函数 =============

/** 标题栏 */
function titleBar(slide, pres, text, C) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: SW, h: 0.6,
    fill: { color: C.title }
  });
  slide.addText(text, {
    x: 0.35, y: 0, w: SW - 0.7, h: 0.6,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: C.white, bold: true, valign: "middle"
  });
}

/** 副标题标签 */
function subLabel(slide, pres, text, x, y, w, h, color, C) {
  slide.addText(text, {
    x, y, w: w || 2, h: h || 0.35,
    shape: pres.shapes.RECTANGLE,
    fill: { color: color || C.d[0] },
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: C.white, bold: true, align: "center", valign: "middle"
  });
}

/** 圆角卡片(文字在形状内部) */
function card(slide, pres, text, x, y, w, h, fillColor, C, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h,
    shape: pres.shapes.ROUNDED_RECTANGLE,
    fill: { color: fillColor || C.s[0] },
    fontSize: o.fontSize || 14,
    fontFace: "Microsoft YaHei",
    color: o.color || C.white,
    align: o.align || "center",
    valign: o.valign || "middle",
    bold: o.bold || false,
    rectRadius: 0.08,
    margin: [2, 4, 2, 4]
  });
}

/** 矩形卡片 */
function rectCard(slide, pres, text, x, y, w, h, fillColor, C, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h,
    shape: pres.shapes.RECTANGLE,
    fill: { color: fillColor || C.s[0] },
    fontSize: o.fontSize || 14,
    fontFace: "Microsoft YaHei",
    color: o.color || C.white,
    align: o.align || "center",
    valign: o.valign || "middle",
    bold: o.bold || false,
    margin: [2, 4, 2, 4]
  });
}

/** 分组背景 */
function groupBg(slide, pres, x, y, w, h, color, C) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: color || C.bgGroup },
    rectRadius: 0.1,
    line: { color: C.border, width: 0.5 }
  });
}

/** 六边形卡片 */
function hexCard(slide, pres, text, x, y, w, h, fillColor, C, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h,
    shape: pres.shapes.HEXAGON,
    fill: { color: fillColor || C.s[0] },
    fontSize: o.fontSize || 14,
    fontFace: "Microsoft YaHei",
    color: o.color || C.white,
    align: "center", valign: "middle",
    bold: o.bold || false,
    margin: [2, 4, 2, 4]
  });
}

/** 菱形卡片 */
function diamondCard(slide, pres, text, x, y, w, h, fillColor, C, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h,
    shape: pres.shapes.DIAMOND,
    fill: { color: fillColor || C.s[5] },
    fontSize: o.fontSize || 14,
    fontFace: "Microsoft YaHei",
    color: o.color || C.white,
    align: "center", valign: "middle",
    bold: o.bold || false,
    margin: [2, 4, 2, 4]
  });
}

/** 椭圆标签 */
function ovalLabel(slide, pres, text, x, y, w, h, fillColor, C, opts) {
  const o = opts || {};
  slide.addText(text, {
    x, y, w, h,
    shape: pres.shapes.OVAL,
    fill: { color: fillColor || C.s[2] },
    fontSize: o.fontSize || 14,
    fontFace: "Microsoft YaHei",
    color: o.color || C.white,
    align: "center", valign: "middle",
    bold: o.bold || false
  });
}

// ============= 图表模板 =============

/** 图1-1 公司组织架构 - 层次树形卡片 */
function chart_org_chart(pres, projectName, data, C) {
  const d = data.org_chart;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 公司组织架构", C);

  const l2 = d.l2;
  const l2x = [0.8, 4.1, 7.4];
  const cx = SW / 2 - 0.9;
  rectCard(slide, pres, "总经理", cx, 0.75, 1.8, 0.4, C.d[0], C, { bold: true });

  l2.forEach((t, i) => {
    rectCard(slide, pres, t, l2x[i], 1.35, 1.8, 0.4, C.d[i + 1], C, { bold: true });
  });

  d.l3.forEach((group, gi) => {
    const baseX = l2x[gi];
    group.forEach((t, ti) => {
      const ox = baseX + ti * 1.5 - 0.3;
      card(slide, pres, t, ox, 2.0, 1.3, 0.35, C.s[gi * 2 + ti], C);
    });
  });

  d.l4.forEach((group, gi) => {
    const row = Math.floor(gi / 2);
    const col = gi % 2;
    const baseX = col === 0 ? 0.3 : 5.1;
    const baseY = 2.65 + row * 0.95;
    groupBg(slide, pres, baseX - 0.05, baseY - 0.05, 4.7, 0.85, C.bgGroup, C);
    group.forEach((t, ti) => {
      card(slide, pres, t, baseX + ti * 1.15, baseY + 0.08, 1.05, 0.35, C.s[(gi * 2 + ti) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图1-2 发展战略路线 - 分阶段时间线 */
function chart_strategy_roadmap(pres, projectName, data, C) {
  const d = data.strategy_roadmap;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 发展战略路线", C);

  const phases = d.phases;
  const phaseW = 2.2, gap = 0.2;
  const startX = (SW - (phaseW * 4 + gap * 3)) / 2;

  phases.forEach((p, i) => {
    const x = startX + i * (phaseW + gap);
    rectCard(slide, pres, p.name, x, 0.75, phaseW, 0.4, C.d[i], C, { bold: true });
    card(slide, pres, p.period, x, 1.2, phaseW, 0.3, C.s[i], C, { fontSize: 14 });
    groupBg(slide, pres, x, 1.65, phaseW, 3.5, C.bgGroup, C);
    p.items.forEach((item, j) => {
      card(slide, pres, item, x + 0.1, 1.75 + j * 0.82, phaseW - 0.2, 0.7, C.s[(i + j) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图1-3 SWOT分析 - 2x2象限 */
function chart_swot(pres, projectName, data, C) {
  const d = data.swot;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · SWOT分析", C);

  const quads = d.quads;
  const positions = [[0.3, 0.75], [5.15, 0.75], [0.3, 3.05], [5.15, 3.05]];
  const qw = 4.55, qh = 2.15;

  quads.forEach((q, i) => {
    const [qx, qy] = positions[i];
    groupBg(slide, pres, qx, qy, qw, qh, C.bgGroup, C);
    rectCard(slide, pres, q.title, qx + 0.1, qy + 0.1, qw - 0.2, 0.35, C.d[i], C, { bold: true, fontSize: 14 });
    q.items.forEach((item, j) => {
      const col = j % 2;
      const row = Math.floor(j / 2);
      const cx = qx + 0.15 + col * 2.2;
      const cy = qy + 0.55 + row * 0.75;
      card(slide, pres, item, cx, cy, 2.05, 0.65, C.s[i], C, { fontSize: 14 });
    });
  });

  ovalLabel(slide, pres, "SWOT\n战略分析", 4.2, 2.55, 1.6, 0.8, C.d[5], C, { bold: true, fontSize: 14 });
  return slide;
}

/** 图1-4 波特六力分析 - 六角布局 */
function chart_porter_six(pres, projectName, data, C) {
  const d = data.porter_six;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 波特六力分析", C);

  const items = d.items;
  items.forEach((item, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.3 + col * 3.2;
    const y = 0.75 + row * 2.45;
    groupBg(slide, pres, x, y, 3.0, 2.25, C.bgGroup, C);
    rectCard(slide, pres, item.title, x + 0.1, y + 0.1, 2.8, 0.35, C.d[i], C, { bold: true });
    card(slide, pres, item.desc, x + 0.1, y + 0.55, 2.8, 0.4, C.s[i], C, { fontSize: 14 });
    card(slide, pres, item.detail, x + 0.1, y + 1.05, 2.8, 0.95, C.s[i], C, { fontSize: 14 });
  });

  return slide;
}

/** 图1-5 研发路线 - 阶段时间线 */
function chart_rd_roadmap(pres, projectName, data, C) {
  const d = data.rd_roadmap;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 研发路线", C);

  const phases = d.phases;
  const pw = 1.8, gap = 0.12;
  const sx = (SW - (pw * 5 + gap * 4)) / 2;

  phases.forEach((p, i) => {
    const x = sx + i * (pw + gap);
    rectCard(slide, pres, p.name, x, 0.75, pw, 0.38, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, p.period, x, 1.2, pw, 0.3, C.s[i], C, { fontSize: 14 });
    groupBg(slide, pres, x, 1.6, pw, 3.6, C.bgGroup, C);
    p.items.forEach((item, j) => {
      card(slide, pres, item, x + 0.05, 1.7 + j * 0.85, pw - 0.1, 0.7, C.s[(i + j) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图1-6 产品矩阵 - 网格表格 */
function chart_product_matrix(pres, projectName, data, C) {
  const d = data.product_matrix;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 产品矩阵", C);

  const rows = d.rows;
  const cols = d.cols;
  const matrixData = d.data;

  const ox = 0.3, oy = 0.8;
  const cw = 1.7, rh = 0.6;
  const headerW = 1.2;

  cols.forEach((c, i) => {
    rectCard(slide, pres, c, ox + headerW + i * cw, oy, cw - 0.05, rh, C.d[i % 5], C, { bold: true, fontSize: 14 });
  });
  rectCard(slide, pres, "版本", ox, oy, headerW, rh, C.title, C, { bold: true, color: C.white });

  rows.forEach((r, ri) => {
    const y = oy + (ri + 1) * (rh + 0.05);
    rectCard(slide, pres, r, ox, y, headerW, rh, C.d[ri + 5], C, { bold: true, fontSize: 14 });
    matrixData[ri].forEach((cell, ci) => {
      card(slide, pres, cell, ox + headerW + ci * cw, y, cw - 0.05, rh, C.s[(ri * 3 + ci) % 10], C, { fontSize: 14 });
    });
  });

  const bottomY = oy + 4 * (rh + 0.05);
  groupBg(slide, pres, 0.3, bottomY, 9.4, 0.6, C.bgGroup, C);
  card(slide, pres, d.bottomDesc, 0.4, bottomY + 0.05, 9.2, 0.5, C.s[7], C, { fontSize: 14 });

  return slide;
}

/** 通用分层架构图 */
function chart_layered_arch(pres, projectName, chartTitle, layers, C) {
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · " + chartTitle, C);

  const layerCount = layers.length;
  const margin = 0.3;
  const layerGap = 0.1;
  const topY = 0.75;
  const totalH = SH - topY - 0.2;
  const layerH = (totalH - layerGap * (layerCount - 1)) / layerCount;

  layers.forEach((layer, li) => {
    const y = topY + li * (layerH + layerGap);
    const colorIdx = li % 10;
    groupBg(slide, pres, margin, y, SW - margin * 2, layerH, C.bgGroup, C);
    rectCard(slide, pres, layer.name, margin + 0.05, y + 0.05, 1.5, layerH - 0.1, C.d[colorIdx], C, { bold: true, fontSize: 14 });

    const items = layer.items;
    const cardAreaW = SW - margin * 2 - 1.7;
    const cardGap = 0.08;
    const cardW = Math.min(2.0, (cardAreaW - cardGap * (items.length - 1)) / items.length);
    const cardStartX = margin + 1.65;

    items.forEach((item, ii) => {
      card(slide, pres, item, cardStartX + ii * (cardW + cardGap), y + 0.05, cardW, layerH - 0.1, C.s[(colorIdx + ii) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图1-8 营销渠道 - 漏斗 */
function chart_funnel(pres, projectName, data, C) {
  const d = data.funnel;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 营销渠道漏斗", C);

  const stages = d.stages;
  const totalH = 4.4;
  const rowH = totalH / stages.length;
  const maxWidth = 8.0;

  stages.forEach((s, i) => {
    const y = 0.8 + i * rowH;
    const widthRatio = 1 - i * 0.15;
    const w = maxWidth * widthRatio;
    const x = (SW - w) / 2;
    card(slide, pres, s.name, x, y + 0.05, w, rowH - 0.1, C.s[i], C, { fontSize: 16, bold: true });
    card(slide, pres, s.value, 0.3, y + 0.1, 1.2, rowH - 0.2, C.d[i], C, { fontSize: 14, bold: true });
    if (i % 2 === 0) {
      card(slide, pres, s.desc, SW - 2.3, y + 0.1, 2.0, (rowH - 0.2) / 2, C.s[(i + 3) % 10], C, { fontSize: 14 });
      card(slide, pres, s.count, SW - 2.3, y + (rowH - 0.2) / 2 + 0.1, 2.0, (rowH - 0.2) / 2, C.s[(i + 5) % 10], C, { fontSize: 14 });
    }
  });

  return slide;
}

/** 图1-9 商业画布 - 9宫格 */
function chart_business_canvas(pres, projectName, data, C) {
  const d = data.business_canvas;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 商业模式画布", C);

  const cells = d.cells;
  const gx = 0.25, gy = 0.75;
  const gw = 3.05, gh = 1.55;
  const gg = 0.1;

  cells.forEach((c, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = gx + col * (gw + gg);
    const y = gy + row * (gh + gg);
    groupBg(slide, pres, x, y, gw, gh, C.bgGroup, C);
    rectCard(slide, pres, c.title, x + 0.05, y + 0.05, gw - 0.1, 0.3, C.d[i], C, { bold: true, fontSize: 14 });
    c.items.forEach((item, j) => {
      card(slide, pres, item, x + 0.05, y + 0.4 + j * 0.36, gw - 0.1, 0.32, C.s[i], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 通用流程图 */
function chart_flowchart(pres, projectName, chartTitle, steps, C) {
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · " + chartTitle, C);

  const maxPerRow = 6;
  const rows = [];
  for (let i = 0; i < steps.length; i += maxPerRow) {
    rows.push(steps.slice(i, i + maxPerRow));
  }

  const rowH = 2.0;
  const startY = 0.8 + (rows.length === 1 ? 1.0 : 0);

  rows.forEach((row, ri) => {
    const count = row.length;
    const cardW = Math.min(1.5, (SW - 0.6 - 0.1 * (count - 1)) / count);
    const totalRowW = count * cardW + (count - 1) * 0.1;
    const startX = (SW - totalRowW) / 2;
    const y = startY + ri * (rowH + 0.3);

    row.forEach((step, si) => {
      const x = startX + si * (cardW + 0.1);
      const colorIdx = (ri * maxPerRow + si) % 10;
      groupBg(slide, pres, x, y, cardW, rowH, C.bgGroup, C);
      ovalLabel(slide, pres, String(ri * maxPerRow + si + 1), x + cardW / 2 - 0.2, y + 0.08, 0.4, 0.35, C.d[colorIdx], C, { bold: true, fontSize: 14 });
      card(slide, pres, step, x + 0.05, y + 0.55, cardW - 0.1, rowH - 0.65, C.s[colorIdx], C, { fontSize: 15, bold: true });
    });
  });

  return slide;
}

/** 图2-2 市场规模增长趋势 - 柱状图块 */
function chart_area_growth(pres, projectName, data, C) {
  const d = data.market_growth;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 市场规模增长趋势", C);

  const growthData = d.data;
  const maxVal = Math.max(...growthData.map(x => x.value));
  const barArea = { x: 1.0, y: 0.9, w: 8.0, h: 3.8 };
  const barW = 1.0;
  const barGap = (barArea.w - growthData.length * barW) / (growthData.length + 1);

  growthData.forEach((item, i) => {
    const x = barArea.x + barGap + i * (barW + barGap);
    const barH = (item.value / maxVal) * barArea.h;
    const y = barArea.y + barArea.h - barH;
    rectCard(slide, pres, item.label, x, y, barW, barH, C.s[i % 10], C, { fontSize: 16, bold: true, valign: "top" });
    card(slide, pres, item.year, x - 0.1, barArea.y + barArea.h + 0.1, barW + 0.2, 0.35, C.d[i], C, { fontSize: 14 });
  });

  card(slide, pres, "年复合增长率(CAGR): " + d.cagr, 2.5, SH - 0.5, 5.0, 0.4, C.d[5], C, { fontSize: 14, bold: true });
  return slide;
}

/** 图2-3 政策支持时间线 */
function chart_timeline(pres, projectName, data, C) {
  const d = data.policy_timeline;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 政策支持时间线", C);

  const phases = d.phases;
  const pw = 1.75, gap = 0.15;
  const sx = (SW - (pw * 5 + gap * 4)) / 2;

  phases.forEach((p, i) => {
    const x = sx + i * (pw + gap);
    rectCard(slide, pres, p.name, x, 0.75, pw, 0.38, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, p.dur, x, 1.2, pw, 0.3, C.s[i], C, { fontSize: 14 });
    groupBg(slide, pres, x, 1.6, pw, 3.6, C.bgGroup, C);
    p.items.forEach((item, j) => {
      card(slide, pres, item, x + 0.05, 1.7 + j * 1.15, pw - 0.1, 1.0, C.s[(i + j) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图2-11 目标客户画像 */
function chart_personas(pres, projectName, data, C) {
  const d = data.personas;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 目标客户画像", C);

  const personas = d.personas;
  const pw = 3.0, gap = 0.2;
  const sx = (SW - (pw * 3 + gap * 2)) / 2;

  personas.forEach((p, i) => {
    const x = sx + i * (pw + gap);
    groupBg(slide, pres, x, 0.75, pw, 4.5, C.bgGroup, C);
    ovalLabel(slide, pres, p.name.charAt(0), x + pw / 2 - 0.4, 0.9, 0.8, 0.7, C.d[i], C, { bold: true, fontSize: 24 });
    card(slide, pres, p.name, x + 0.1, 1.7, pw - 0.2, 0.4, C.d[i], C, { bold: true, fontSize: 16 });
    p.attrs.forEach((attr, j) => {
      card(slide, pres, attr, x + 0.15, 2.25 + j * 0.58, pw - 0.3, 0.5, C.s[i], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图2-12 雷达图 → 维度卡片网格 */
function chart_radar(pres, projectName, chartTitle, labels, values, C) {
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · " + chartTitle, C);

  const count = labels.length;
  const cols = 3;
  const rows = Math.ceil(count / cols);
  const cw = 3.0, ch = 1.2, gx = 0.15, gy = 0.1;
  const sx = (SW - (cols * cw + (cols - 1) * gx)) / 2;
  const sy = 0.8;

  labels.forEach((label, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = sx + col * (cw + gx);
    const y = sy + row * (ch + gy);
    rectCard(slide, pres, label, x, y, cw, 0.35, C.d[i % 10], C, { bold: true, fontSize: 14 });

    const val = values[i];
    const barMaxW = cw - 0.2;
    const barW = (val / 100) * barMaxW;
    rectCard(slide, pres, val + "%", x + 0.1, y + 0.45, barW, 0.6, C.s[i % 10], C, { fontSize: 18, bold: true });

    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.1, y: y + 0.45 + 0.6,
      w: barMaxW, h: 0.08,
      fill: { color: C.border }
    });
  });

  return slide;
}

/** 图2-13 对比表格 */
function chart_comparison(pres, projectName, data, C) {
  const d = data.product_comparison;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 产品优势对比", C);

  const headers = d.headers;
  const rows = d.rows;

  const ox = 0.5, oy = 0.85;
  const colW = [1.8, 2.5, 2.5, 2.5];
  const rh = 0.85;

  let cx = ox;
  headers.forEach((h, i) => {
    rectCard(slide, pres, h, cx, oy, colW[i] - 0.05, rh, C.title, C, { bold: true, color: C.white, fontSize: 16 });
    cx += colW[i];
  });

  rows.forEach((row, ri) => {
    const y = oy + (ri + 1) * (rh + 0.08);
    let rx = ox;
    row.forEach((cell, ci) => {
      const bgColor = ci === 0 ? C.d[ri + 3] : (ci === 1 ? "7B8C76" : C.s[(ri * 2 + ci) % 10]);
      const txtColor = ci === 0 ? C.white : C.white;
      card(slide, pres, cell, rx, y, colW[ci] - 0.05, rh, bgColor, C, { fontSize: 15, bold: ci === 1, color: txtColor });
      rx += colW[ci];
    });
  });

  card(slide, pres, d.bottomText, 0.5, SH - 0.55, 9.0, 0.4, C.d[2], C, { fontSize: 14 });
  return slide;
}

/** 图2-15 柱状对比 */
function chart_bar(pres, projectName, data, C) {
  const d = data.effect_bar;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 应用效果数据对比", C);

  const barData = d.data;
  const barArea = { x: 0.5, y: 1.0, w: 9.0, h: 3.5 };
  const barH = 0.6;
  const barGap = (barArea.h - barData.length * barH) / (barData.length + 1);
  const maxBarW = 7.0;

  barData.forEach((item, i) => {
    const y = barArea.y + barGap + i * (barH + barGap);
    const w = (item.value / 100) * maxBarW;
    rectCard(slide, pres, item.label, 0.3, y, 1.5, barH, C.d[i], C, { bold: true, fontSize: 16 });
    rectCard(slide, pres, item.value + "%", 1.9, y, w, barH, C.s[i], C, { fontSize: 18, bold: true });
    card(slide, pres, item.desc, 1.9 + w + 0.1, y, 1.2, barH, C.s[(i + 5) % 10], C, { fontSize: 14 });
  });

  return slide;
}

/** 图2-16 饼图 → 比例方块 */
function chart_pie(pres, projectName, data, C) {
  const d = data.market_share;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 市场占有率分析", C);

  const slices = d.slices;
  const totalW = 4.5;
  let cx = 0.4;
  slices.forEach((s, i) => {
    const w = (s.pct / 100) * totalW;
    rectCard(slide, pres, s.label + "\n" + s.pct + "%", cx, 1.2, w, 3.0, C.s[i], C, { fontSize: 16, bold: true });
    cx += w;
  });

  const rx = 5.2;
  slices.forEach((s, i) => {
    const y = 0.9 + i * 0.9;
    rectCard(slide, pres, s.label, rx, y, 1.8, 0.35, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, s.pct + "%", rx + 1.9, y, 1.0, 0.35, C.s[i], C, { bold: true, fontSize: 16 });
    card(slide, pres, "占比分析", rx + 3.0, y, 1.5, 0.35, C.s[(i + 5) % 10], C, { fontSize: 14 });
  });

  card(slide, pres, d.bottomText, 1.5, SH - 0.55, 7.0, 0.4, C.d[0], C, { fontSize: 14, bold: true });
  return slide;
}

/** 图2-17/2-20 散点 → 象限矩阵 */
function chart_quadrant(pres, projectName, chartTitle, d, C) {
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · " + chartTitle, C);

  const items = d.items;
  const quadLabels = d.quadLabels;
  const quadPos = [[0.5, 0.8], [5.2, 0.8], [0.5, 3.1], [5.2, 3.1]];
  const qw = 4.5, qh = 2.15;

  quadLabels.forEach((ql, qi) => {
    const [qx, qy] = quadPos[qi];
    groupBg(slide, pres, qx, qy, qw, qh, qi === 0 ? "E8EDE8" : C.bgGroup, C);
    subLabel(slide, pres, ql, qx + 0.1, qy + 0.05, 1.5, 0.3, C.d[qi], C);
  });

  items.forEach((item, i) => {
    const qi = (item.y === "高" ? 0 : 2) + (item.x === "高" || item.x === "中" ? 0 : 1);
    const [qx, qy] = quadPos[Math.min(qi, 3)];
    const ox = qx + 0.2 + (i % 2) * 2.2;
    const oy = qy + 0.4 + Math.floor(i / 3) * 1.0;
    card(slide, pres, item.name, ox, oy, 2.0, 0.35, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, item.desc, ox, oy + 0.4, 2.0, 0.7, C.s[i], C, { fontSize: 14 });
  });

  return slide;
}

/** 图2-18 收入构成 - 甜甜圈 → 环形块 */
function chart_donut(pres, projectName, data, C) {
  const d = data.revenue_donut;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 收入构成分析", C);

  const slices = d.slices;
  slices.forEach((s, i) => {
    const y = 0.9 + i * 0.85;
    rectCard(slide, pres, s.label, 0.3, y, 1.5, 0.7, C.d[i], C, { bold: true, fontSize: 14 });
    rectCard(slide, pres, s.pct + "%", 1.9, y, (s.pct / 100) * 5.5, 0.7, C.s[i], C, { bold: true, fontSize: 18 });
  });

  const rx = 6.0;
  slices.forEach((s, i) => {
    const y = 0.9 + i * 0.85;
    card(slide, pres, s.desc, rx, y, 3.5, 0.7, C.s[(i + 3) % 10], C, { fontSize: 14 });
  });

  return slide;
}

/** 图2-19 收入增长趋势 */
function chart_line_growth(pres, projectName, data, C) {
  const d = data.revenue_growth;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 收入增长趋势", C);

  const years = d.years;
  const revenue = d.revenue;
  const profit = d.profit;
  const maxVal = Math.max(...revenue);
  const barArea = { x: 0.8, y: 1.0, w: 8.5, h: 3.2 };
  const groupW = barArea.w / years.length;

  years.forEach((year, i) => {
    const gx = barArea.x + i * groupW;
    const revH = (revenue[i] / maxVal) * barArea.h;
    const revY = barArea.y + barArea.h - revH;
    rectCard(slide, pres, revenue[i] + "万", gx + 0.1, revY, groupW * 0.4, revH, C.s[0], C, { fontSize: 14, bold: true });

    const proH = (profit[i] / maxVal) * barArea.h;
    const proY = barArea.y + barArea.h - proH;
    rectCard(slide, pres, profit[i] + "万", gx + groupW * 0.5, proY, groupW * 0.4, proH, C.s[2], C, { fontSize: 14, bold: true });

    card(slide, pres, year, gx + 0.1, barArea.y + barArea.h + 0.1, groupW - 0.2, 0.35, C.d[i], C, { fontSize: 15 });
  });

  rectCard(slide, pres, "营收", 3.0, SH - 0.5, 1.5, 0.35, C.s[0], C, { fontSize: 14 });
  rectCard(slide, pres, "净利润", 4.7, SH - 0.5, 1.5, 0.35, C.s[2], C, { fontSize: 14 });
  return slide;
}

/** 图3-1 资金用途分布 */
function chart_funding_use(pres, projectName, data, C) {
  const d = data.funding_use;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 资金用途分布", C);

  const items = d.items;
  const barY = 0.9, barH = 1.8;
  let cx = 0.3;
  items.forEach((s, i) => {
    const w = (s.pct / 100) * 9.0;
    rectCard(slide, pres, s.label + "\n" + s.pct + "%", cx, barY, w, barH, C.s[i], C, { fontSize: 16, bold: true });
    cx += w;
  });

  items.forEach((s, i) => {
    const x = 0.3 + i * 1.9;
    const y = 3.0;
    rectCard(slide, pres, s.label, x, y, 1.75, 0.4, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, s.pct + "%", x, y + 0.45, 1.75, 0.5, C.s[i], C, { bold: true, fontSize: 18 });
    card(slide, pres, s.desc, x, y + 1.0, 1.75, 0.7, C.s[(i + 5) % 10], C, { fontSize: 14 });
  });

  return slide;
}

/** 图3-2 融资里程碑 */
function chart_financing_milestone(pres, projectName, data, C) {
  const d = data.financing_milestone;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 融资里程碑", C);

  const phases = d.phases;
  const pw = 1.8, gap = 0.12;
  const sx = (SW - (pw * 5 + gap * 4)) / 2;

  phases.forEach((p, i) => {
    const x = sx + i * (pw + gap);
    rectCard(slide, pres, p.name, x, 0.75, pw, 0.35, C.d[i], C, { bold: true, fontSize: 14 });
    card(slide, pres, p.period, x, 1.15, pw, 0.28, C.s[i], C, { fontSize: 14 });

    if (p.amount !== "—") {
      ovalLabel(slide, pres, p.amount, x + pw / 2 - 0.5, 1.5, 1.0, 0.5, C.d[i], C, { bold: true, fontSize: 16 });
    }

    groupBg(slide, pres, x, 2.15, pw, 3.0, C.bgGroup, C);
    p.items.forEach((item, j) => {
      card(slide, pres, item, x + 0.05, 2.25 + j * 0.95, pw - 0.1, 0.85, C.s[(i + j) % 10], C, { fontSize: 14 });
    });
  });

  return slide;
}

/** 图4-1 风险矩阵 */
function chart_risk_matrix(pres, projectName, data, C) {
  const d = data.risk_matrix;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 风险评估矩阵", C);

  const rows = d.rows;
  const oy = 0.8;
  const nameW = 1.5;
  const cardW = 1.9;
  const rh = 0.75;
  const gap = 0.08;

  const headers = ["风险类型", "发生概率", "影响程度", "综合评级", "应对优先级"];
  let hx = 0.3;
  const hwidths = [nameW, cardW, cardW, cardW, cardW];
  headers.forEach((h, i) => {
    rectCard(slide, pres, h, hx, oy, hwidths[i] - gap, rh, C.title, C, { bold: true, color: C.white, fontSize: 15 });
    hx += hwidths[i];
  });

  rows.forEach((row, ri) => {
    const y = oy + (ri + 1) * (rh + gap);
    let rx = 0.3;
    rectCard(slide, pres, row.name, rx, y, nameW - gap, rh, C.d[ri], C, { bold: true, fontSize: 15 });
    rx += nameW;
    row.items.forEach((item, ci) => {
      card(slide, pres, item, rx, y, cardW - gap, rh, C.s[(ri + ci) % 10], C, { fontSize: 14 });
      rx += cardW;
    });
  });

  card(slide, pres, "风险应对策略：优先关注高概率高影响风险，建立预警机制与应急预案", 0.5, SH - 0.55, 9.0, 0.4, C.d[2], C, { fontSize: 14, bold: true });
  return slide;
}

/** 图2-54 核心算法架构变体 */
function chart_porter_six_variant(pres, projectName, data, C) {
  const d = data.algorithm_arch;
  const slide = pres.addSlide();
  slide.background = { color: C.bg };
  titleBar(slide, pres, projectName + " · 核心算法架构", C);

  const items = d.items;
  items.forEach((item, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.3 + col * 3.2;
    const y = 0.75 + row * 2.45;
    groupBg(slide, pres, x, y, 3.0, 2.25, C.bgGroup, C);
    rectCard(slide, pres, item.title, x + 0.1, y + 0.1, 2.8, 0.35, C.d[i], C, { bold: true, fontSize: 14 });
    item.details.forEach((detail, j) => {
      card(slide, pres, detail, x + 0.1, y + 0.55 + j * 0.55, 2.8, 0.5, C.s[i], C, { fontSize: 14 });
    });
  });

  return slide;
}

// ============= 主生成逻辑 =============

function loadProjectData(projectIdx, projectName) {
  const dataPath = path.join(DATA_DIR, `p${projectIdx}_${projectName}.json`);
  if (!fs.existsSync(dataPath)) {
    throw new Error(`项目数据文件不存在: ${dataPath}`);
  }
  return JSON.parse(fs.readFileSync(dataPath, "utf8"));
}

function generateProjectCharts(projectName, projectIdx) {
  const data = loadProjectData(projectIdx, projectName);
  const C = COLOR_SCHEMES[data.colorScheme % COLOR_SCHEMES.length];

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = projectName + " - 商业计划书图表";

  // 图1-1
  chart_org_chart(pres, projectName, data, C);
  // 图1-2
  chart_strategy_roadmap(pres, projectName, data, C);
  // 图1-3
  chart_swot(pres, projectName, data, C);
  // 图1-4
  chart_porter_six(pres, projectName, data, C);
  // 图1-5
  chart_rd_roadmap(pres, projectName, data, C);
  // 图1-6
  chart_product_matrix(pres, projectName, data, C);
  // 图1-7
  chart_layered_arch(pres, projectName, "服务体系架构", data.service_arch.layers, C);
  // 图1-8
  chart_funnel(pres, projectName, data, C);
  // 图1-9
  chart_business_canvas(pres, projectName, data, C);

  // 图2-1
  chart_flowchart(pres, projectName, "行业产业链", data.industry_chain.steps, C);
  // 图2-2
  chart_area_growth(pres, projectName, data, C);
  // 图2-3
  chart_timeline(pres, projectName, data, C);
  // 图2-4
  chart_layered_arch(pres, projectName, "产品功能架构", data.product_func_arch.layers, C);
  // 图2-5
  chart_layered_arch(pres, projectName, "系统技术架构", data.tech_arch.layers, C);
  // 图2-6
  chart_flowchart(pres, projectName, "核心算法流程", data.algorithm_flow.steps, C);
  // 图2-11
  chart_personas(pres, projectName, data, C);
  // 图2-12
  chart_radar(pres, projectName, "客户需求分析", data.customer_radar.labels, data.customer_radar.values, C);
  // 图2-13
  chart_comparison(pres, projectName, data, C);
  // 图2-15
  chart_bar(pres, projectName, data, C);
  // 图2-16
  chart_pie(pres, projectName, data, C);
  // 图2-17
  chart_quadrant(pres, projectName, "行业竞争格局", data.competition_scatter, C);
  // 图2-18
  chart_donut(pres, projectName, data, C);
  // 图2-19
  chart_line_growth(pres, projectName, data, C);
  // 图2-20
  chart_quadrant(pres, projectName, "竞争格局矩阵", data.competition_matrix, C);
  // 图2-21
  chart_radar(pres, projectName, "竞争对手对标分析", data.competitor_radar.labels, data.competitor_radar.values, C);

  // 图2-52 to 图2-61
  chart_layered_arch(pres, projectName, "系统整体架构", data.overall_arch.layers, C);
  chart_layered_arch(pres, projectName, "微服务架构", data.microservice_arch.layers, C);
  chart_layered_arch(pres, projectName, "数据库架构", data.database_arch.layers, C);
  chart_layered_arch(pres, projectName, "安全架构", data.security_arch.layers, C);
  chart_layered_arch(pres, projectName, "部署架构", data.deploy_arch.layers, C);
  chart_layered_arch(pres, projectName, "前端架构", data.frontend_arch.layers, C);
  chart_layered_arch(pres, projectName, "运维监控架构", data.ops_arch.layers, C);

  chart_flowchart(pres, projectName, "数据流架构", data.dataflow_arch.steps, C);
  chart_flowchart(pres, projectName, "API架构流程", data.api_arch.steps, C);

  // 图2-54 核心算法架构变体
  chart_porter_six_variant(pres, projectName, data, C);

  // 图3-1
  chart_funding_use(pres, projectName, data, C);
  // 图3-2
  chart_financing_milestone(pres, projectName, data, C);
  // 图4-1
  chart_risk_matrix(pres, projectName, data, C);

  const outPath = path.join(OUT, `p${projectIdx}_${projectName}.pptx`);
  pres.writeFile({ fileName: outPath });
  return outPath;
}

// ============= 主入口 =============

async function main() {
  const projectsPath = path.join("D:", "计划书AI", "output_v2", "projects_list.json");
  const projects = JSON.parse(fs.readFileSync(projectsPath, "utf8"));

  console.log(`共 ${projects.length} 个项目需要生成`);
  console.log(`输出目录: ${OUT}`);

  const total = projects.length;
  const startTime = Date.now();

  for (let i = 0; i < total; i++) {
    const p = projects[i];
    try {
      const outPath = generateProjectCharts(p.name, p.idx);
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`[${i + 1}/${total}] ${p.name} -> ${outPath} (${elapsed}s)`);
    } catch (err) {
      console.error(`[${i + 1}/${total}] ERROR ${p.name}: ${err.message}`);
    }
  }

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`\n全部完成! 总耗时: ${totalTime}s`);
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
