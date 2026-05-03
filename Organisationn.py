import os
import time
from playwright.sync_api import sync_playwright


def node(title, role, tier, header_color, desc="", compact=False):
    """Helper function to generate the rigid HTML structure for a single node."""
    width = "max-w-[260px]" if compact else "max-w-[280px]"
    title_size = "text-xs" if compact else "text-sm"
    role_size = "text-[10px]" if compact else "text-xs"

    desc_block = ""
    if desc:
        desc_block = (
                '<div class="w-8 border-t border-slate-400 mb-2 flex-shrink-0"></div>'
                '<p class="text-[11px] leading-relaxed text-slate-700 font-serif">' + desc + '</p>'
        )

    return (
            '<div class="relative z-10 w-full ' + width + ' border-2 border-slate-900 bg-white flex flex-col text-center shadow-sm h-full">'
                                                          '<div class="py-3 px-2 border-b-2 border-slate-900 flex-shrink-0 ' + header_color + '">'
                                                                                                                                              '<div class="text-[10px] font-bold uppercase tracking-[0.2em] mb-1 opacity-90">' + tier + '</div>'
                                                                                                                                                                                                                                        '<h3 class="font-serif font-bold leading-snug uppercase tracking-wide ' + title_size + '">' + title + '</h3>'
                                                                                                                                                                                                                                                                                                                                              '</div>'
                                                                                                                                                                                                                                                                                                                                              '<div class="p-4 bg-white text-slate-900 flex-grow flex flex-col justify-center items-center">'
                                                                                                                                                                                                                                                                                                                                              '<div class="font-bold uppercase tracking-wider mb-2 ' + role_size + '">' + role + '</div>'
            + desc_block +
            '</div>'
            '</div>'
    )


def vline(h="h-8", extra_classes=""):
    """Helper function to generate formal vertical/horizontal connector lines."""
    return '<div class="w-[2px] bg-slate-900 mx-auto ' + h + ' ' + extra_classes + '"></div>'


# Assemble the complete HTML document matching the React structure exactly
html_parts = [
    '<!DOCTYPE html>',
    '<html lang="en">',
    '<head>',
    '  <meta charset="UTF-8">',
    '  <script src="https://cdn.tailwindcss.com"></script>',
    '  <style>',
    "    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');",
    "    .font-serif { font-family: 'Merriweather', serif; }",
    '  </style>',
    '</head>',
    '<body class="bg-[#F9F9F8] py-16 px-4 font-sans flex flex-col items-center relative overflow-x-hidden">',

    # HEADER
    '  <div class="text-center mb-12 w-full max-w-5xl border-b-4 border-double border-slate-900 pb-6 px-4 pt-8">',
    '    <h2 class="text-xs font-bold tracking-[0.3em] text-slate-600 uppercase mb-4">Official Organizational Structure</h2>',
    '    <h1 class="text-4xl font-serif font-extrabold text-slate-900 uppercase tracking-widest mb-2 leading-tight">Board of Student Executives</h1>',
    '    <p class="text-xs font-bold tracking-[0.2em] text-slate-800 uppercase mt-4">Institution\'s Innovation Council • NIT Kurukshetra</p>',
    '  </div>',

    '  <div class="w-full max-w-7xl flex flex-col items-center relative pb-32">',

    # TIER 1
    node("Secretary-General", "Student Chief", "Tier 1", "bg-slate-900 text-white",
         "1-2 Holders | Appointed on the Recommendation of the Old Leadership and Other by the Faculty Convener Independently"),

    # CONNECTOR 1
    '  <div class="hidden lg:flex w-full flex-col items-center">',
    vline("h-8"),
    '    <div class="w-[66%] border-t-2 border-slate-900 flex justify-between relative">',
    vline("h-8", "-mt-[2px] mx-0"),
    vline("h-8", "absolute left-1/2 -mt-[2px] -translate-x-1/2"),
    vline("h-8", "-mt-[2px] mx-0"),
    '    </div>',
    '  </div>',

    # TIER 2 ROW & STAFF
    '  <div class="w-full grid grid-cols-3 gap-6 px-4">',
    '    <div class="flex justify-center">',
    node("Associate Secretary", "Strategic Deputies", "Tier 1.5", "bg-slate-200 text-slate-900",
         "Apex-level advisory and domain strategy assistance."),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Executive Secretaries & Joint Secretary-General", "The High Command", "Tier 2", "bg-slate-800 text-white",
         "1-2 Holders | Supreme Enforcers of Deadlines & Ground Execution."),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Chief Coordinator to Secretariat General", "Administrative Aide", "Tier 1.5", "bg-slate-200 text-slate-900",
         "Internal scheduling, documents, and liaison for SG."),
    '    </div>',
    '  </div>',

    # CONNECTOR 2
    '  <div class="hidden xl:flex w-full flex-col items-center mt-2">',
    vline("h-10"),
    '    <div class="w-[75%] border-t-2 border-slate-900 flex justify-between relative">',
    vline("h-8", "-mt-[2px] mx-0"),
    vline("h-8", "absolute left-[33.33%] -mt-[2px] -translate-x-1/2 mx-0"),
    vline("h-8", "absolute left-[66.66%] -mt-[2px] -translate-x-1/2 mx-0"),
    vline("h-8", "-mt-[2px] mx-0"),
    '    </div>',
    '  </div>',

    # TIER 3 (4 DEPARTMENTS)
    '  <div class="w-full grid grid-cols-4 gap-6 px-4">',
    '    <div class="flex justify-center">',
    node("Ground Ops & Logistics", "Exec. & Asst. Coordinators", "Tier 3 (Dept)", "bg-slate-700 text-white",
         "Includes Addl. Exec. Coordinators as needed.", True),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Design & Media Content", "Exec. & Asst. Coordinators", "Tier 3 (Dept)", "bg-slate-700 text-white",
         "Includes Addl. Exec. Coordinators as needed.", True),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Outreach & Publicity", "Exec. & Asst. Coordinators", "Tier 3 (Dept)", "bg-slate-700 text-white",
         "Includes Addl. Exec. Coordinators as needed.", True),
    '    </div>',
    '    <div class="flex justify-center">',
    node("PR & Documentation", "Exec. & Asst. Coordinators", "Tier 3 (Dept)", "bg-slate-700 text-white",
         "Includes Addl. Exec. Coordinators as needed.", True),
    '    </div>',
    '  </div>',

    # CONNECTOR 3
    '  <div class="hidden xl:flex w-full flex-col items-center mt-2">',
    '    <div class="w-[75%] flex justify-between relative">',
    vline("h-8", "mx-0"),
    vline("h-8", "absolute left-[33.33%] -translate-x-1/2 mx-0"),
    vline("h-8", "absolute left-[66.66%] -translate-x-1/2 mx-0"),
    vline("h-8", "mx-0"),
    '    </div>',
    '    <div class="w-[75%] h-[2px] bg-slate-900"></div>',
    '    <div class="w-[66%] flex justify-between relative max-w-5xl">',
    vline("h-8", "mx-0"),
    vline("h-8", "absolute left-1/2 -translate-x-1/2 mx-0"),
    vline("h-8", "mx-0"),
    '    </div>',
    '  </div>',

    # TIER 4
    '  <div class="w-full max-w-5xl grid grid-cols-3 gap-6 px-4">',
    '    <div class="flex justify-center">',
    node("Lead of Design & Logistics Ops", "Sandwich Lead", "Tier 4", "bg-slate-300 text-slate-900",
         "Bridges Ground Operations and Design functions.", True),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Head/Lead of Design", "Domain Lead", "Tier 4", "bg-slate-300 text-slate-900",
         "Directs core visual content and creative media assets.", True),
    '    </div>',
    '    <div class="flex justify-center">',
    node("Lead of Outreach & Doc.", "Sandwich Lead", "Tier 4", "bg-slate-300 text-slate-900",
         "Bridges Publicity/Outreach and PR/Documentation.", True),
    '    </div>',
    '  </div>',

    # CONNECTOR 4
    '  <div class="hidden md:flex w-full flex-col items-center mt-2">',
    '    <div class="w-[66%] max-w-5xl flex justify-between relative">',
    vline("h-8", "mx-0"),
    vline("h-8", "absolute left-1/2 -translate-x-1/2 mx-0"),
    vline("h-8", "mx-0"),
    '    </div>',
    '    <div class="w-[66%] max-w-5xl h-[2px] bg-slate-900"></div>',
    vline("h-10"),
    '  </div>',

    # TIER 5
    node("Assistant Executives I & II", "The Ground Workforce", "Tier 5", "bg-slate-100 text-slate-900",
         "Physical Execution, Portal Data Gathering & Direct Outreach."),

    '  </div>',

    # FOOTER
    '  <div class="mt-8 w-full max-w-5xl border-t-2 border-slate-900 pt-4 flex flex-row justify-between text-[10px] font-bold uppercase tracking-widest text-slate-600 px-4">',
    '    <span>Doc Ref: BSE-IIC-ORG-004</span>',
    '    <span>Classified: Internal Council Hierarchy</span>',
    '  </div>',

    '</body>',
    '</html>'
]

html_content = "\n".join(html_parts)
temp_html_path = os.path.abspath("temp_org_chart.html")
output_image_path = os.path.abspath("Organisation_Structure.png")

# Write temporary HTML file
with open(temp_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Starting headless browser environment...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    # A wide viewport ensures Tailwind activates all desktop grid structures (xl, lg, md)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    print("Loading structure and fetching fonts/styles...")
    page.goto(f"file://{temp_html_path}", wait_until="networkidle")

    # Pause slightly to ensure the Tailwind CSS CDN compiles everything perfectly
    page.wait_for_timeout(3000)

    print("Rendering Image...")
    # Capture a high-resolution full-page screenshot as a PNG
    page.screenshot(
        path=output_image_path,
        full_page=True,
        type="png"
    )
    browser.close()

# Cleanup temp file
os.remove(temp_html_path)

print(f"\n✅ SUCCESS! Image generated successfully.")
print(f"File saved at: {output_image_path}")