#r "nuget: DocumentFormat.OpenXml, 3.2.0"

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

using WpPageSize = DocumentFormat.OpenXml.Wordprocessing.PageSize;

string[] args = Environment.GetCommandLineArgs();
if (args.Length < 4)
{
    Console.WriteLine("Usage: dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli -- run-script generate_business_plan.csx <input.md> <output.docx> <title>");
    return;
}

string inputPath = args[3];
string outputPath = args[4];
string docTitle = args[5];

string content = File.ReadAllText(inputPath, System.Text.Encoding.UTF8);

// Parse markdown: extract chapters (## headers)
var lines = content.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
var chapters = new List<(string title, List<string> paragraphs)>();
string currentTitle = "";
var currentParagraphs = new List<string>();
bool inChapter = false;

foreach (var rawLine in lines)
{
    string line = rawLine.Trim();
    if (string.IsNullOrWhiteSpace(line)) continue;

    if (line.StartsWith("## "))
    {
        if (inChapter && currentParagraphs.Count > 0)
        {
            chapters.Add((currentTitle, new List<string>(currentParagraphs)));
        }
        currentTitle = line.Substring(3).Trim();
        currentParagraphs.Clear();
        inChapter = true;
    }
    else if (line.StartsWith("# "))
    {
        // Main title, skip
        continue;
    }
    else
    {
        if (inChapter)
        {
            currentParagraphs.Add(line);
        }
    }
}

if (inChapter && currentParagraphs.Count > 0)
{
    chapters.Add((currentTitle, new List<string>(currentParagraphs)));
}

using var doc = WordprocessingDocument.Create(outputPath, WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document(new Body());
var body = mainPart.Document.Body!;

// ── Styles ──
var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
stylesPart.Styles = new Styles();
var styles = stylesPart.Styles;

// DocDefaults: SimSun 12pt body, 1.5x line spacing for CJK readability
styles.Append(new DocDefaults(
    new RunPropertiesDefault(
        new RunPropertiesBaseStyle(
            new RunFonts
            {
                Ascii = "Times New Roman",
                HighAnsi = "Times New Roman",
                EastAsia = "SimSun",
                ComplexScript = "Times New Roman"
            },
            new FontSize { Val = "24" },
            new FontSizeComplexScript { Val = "24" },
            new Color { Val = "000000" },
            new Languages { Val = "en-US", EastAsia = "zh-CN" }
        )
    ),
    new ParagraphPropertiesDefault(
        new ParagraphPropertiesBaseStyle(
            new SpacingBetweenLines
            {
                Line = "360",
                LineRule = LineSpacingRuleValues.Auto,
                After = "0"
            },
            new Indentation { FirstLineChars = 200 }
        )
    )
));

// Normal style
styles.Append(new Style(
    new StyleName { Val = "Normal" },
    new UIPriority { Val = 0 },
    new PrimaryStyle()
)
{
    Type = StyleValues.Paragraph,
    StyleId = "Normal",
    Default = true
});

// Title style
styles.Append(new Style(
    new StyleName { Val = "Title" },
    new BasedOn { Val = "Normal" },
    new NextParagraphStyle { Val = "Normal" },
    new UIPriority { Val = 9 },
    new PrimaryStyle(),
    new StyleParagraphProperties(
        new Justification { Val = JustificationValues.Center },
        new SpacingBetweenLines
        {
            Before = "480",
            After = "480",
            Line = "360",
            LineRule = LineSpacingRuleValues.Auto
        },
        new Indentation { FirstLine = "0" }
    ),
    new StyleRunProperties(
        new RunFonts
        {
            Ascii = "SimHei",
            HighAnsi = "SimHei",
            EastAsia = "SimHei",
            ComplexScript = "SimHei"
        },
        new FontSize { Val = "44" },
        new FontSizeComplexScript { Val = "44" },
        new Bold(),
        new Color { Val = "000000" }
    )
)
{
    Type = StyleValues.Paragraph,
    StyleId = "Title",
    Default = false
});

// Heading1 style for chapter titles
styles.Append(new Style(
    new StyleName { Val = "heading 1" },
    new BasedOn { Val = "Normal" },
    new NextParagraphStyle { Val = "Normal" },
    new UIPriority { Val = 9 },
    new PrimaryStyle(),
    new StyleParagraphProperties(
        new KeepNext(),
        new KeepLines(),
        new SpacingBetweenLines
        {
            Before = "360",
            After = "240",
            Line = "360",
            LineRule = LineSpacingRuleValues.Auto
        },
        new Indentation { FirstLine = "0" },
        new OutlineLevel { Val = 0 }
    ),
    new StyleRunProperties(
        new RunFonts
        {
            Ascii = "SimHei",
            HighAnsi = "SimHei",
            EastAsia = "SimHei",
            ComplexScript = "SimHei"
        },
        new FontSize { Val = "32" },
        new FontSizeComplexScript { Val = "32" },
        new Bold(),
        new Color { Val = "000000" }
    )
)
{
    Type = StyleValues.Paragraph,
    StyleId = "Heading1",
    Default = false
});

// Page setup: A4, 1in margins
var sectPr = new SectionProperties(
    new WpPageSize { Width = 11906U, Height = 16838U },
    new PageMargin
    {
        Top = 1440, Bottom = 1440,
        Left = 1440U, Right = 1440U,
        Header = 720U, Footer = 720U, Gutter = 0U
    }
);

// Page numbers in footer
var footerPart = mainPart.AddNewPart<FooterPart>();
footerPart.Footer = new Footer(
    new Paragraph(
        new ParagraphProperties(
            new Justification { Val = JustificationValues.Center }
        ),
        new Run(
            new RunProperties(
                new FontSize { Val = "20" },
                new FontSizeComplexScript { Val = "20" },
                new Color { Val = "666666" }
            ),
            new SimpleField(
                new Run(new Text("1"))
            )
            { Instruction = " PAGE " }
        )
    )
);
footerPart.Footer.Save();
string footerPartId = mainPart.GetIdOfPart(footerPart);
sectPr.Append(new FooterReference
{
    Type = HeaderFooterValues.Default,
    Id = footerPartId
});

// Add document title
body.Append(new Paragraph(
    new ParagraphProperties(
        new ParagraphStyleId { Val = "Title" }
    ),
    new Run(new Text(docTitle))
));

// Add chapters
foreach (var chapter in chapters)
{
    // Chapter heading
    body.Append(new Paragraph(
        new ParagraphProperties(
            new ParagraphStyleId { Val = "Heading1" }
        ),
        new Run(new Text(chapter.title))
    ));

    // Paragraphs
    foreach (var para in chapter.paragraphs)
    {
        body.Append(new Paragraph(
            new ParagraphProperties(
                new ParagraphStyleId { Val = "Normal" }
            ),
            new Run(new Text(para) { Space = SpaceProcessingModeValues.Preserve })
        ));
    }
}

body.Append(sectPr);
mainPart.Document.Save();
Console.WriteLine($"Generated: {outputPath}");
