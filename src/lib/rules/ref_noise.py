"""Parser noise in openspec_code_refs.code_path: "paths" that are not files.

PROVISIONAL. October's rules (direction1/prepare_refs.py) were not available
when Phase 1 was written. Phase 2's port should replace or reconcile these.

Each rule is a regular expression. A ref is noise if any rule matches its
code_path. The rules are kept narrow so real files survive: `.env` is a real
file but `.ts` is not; `app/[...slug]/page.tsx` is a real Next.js route.
"""
import re

CODE_EXTENSIONS = (
    "ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|kts|swift|c|h|cc|cpp|hpp|cs|rb|php|html|css|"
    "scss|sass|less|sql|sh|bash|zsh|ps1|vue|svelte|astro|md|mdx|json|yaml|yml|toml|xml|"
    "dart|lua|ex|exs|erl|scala|clj|r|jl|m|mm|proto|graphql|gql|tf|hcl|ipynb|txt|csv|wasm|"
    "zig|nim|ml|hs|elm|fs|vb|pl|pm"
)

# Library and framework names written like files ("Next.js", "Node.js").
TECH_NAMES = (
    "next|node|vue|nuxt|react|express|nest|three|chart|d3|socket|alpine|ember|angular|"
    "backbone|p5|solid|svelte|deno|bun|electron|meteor|knockout|anime|moment|day|lodash|"
    "underscore|jquery|handlebars|mustache|pixi|babylon|leaflet|cytoscape|tone|matter|"
    "cannon|phaser|vis|sigma|chartjs|preact|mithril|riot|aurelia|polymer|ext|dojo|"
    "mootools|prototype|hapi|koa|fastify|sails|adonis|feathers|strapi|gatsby|remix|"
    "qwik|htmx|lit|stimulus|turbo|hotwire|crypto|zod|tensorflow|ml5|brain|natural|"
    "pdf|fabric|paper|konva|two|zdog|popper|tippy|swiper|glide|splide|flickity|"
    "sortable|dragula|interact|hammer|velocity|gsap|popmotion|framer|mo|scroll|"
    "lenis|locomotive|barba|swup|vanta|particles|tsparticles|typed|countup|odometer|"
    "ag-grid|handsontable|tabulator|datatables|grid|x6|g6|g2|echarts|highcharts|"
    "plotly|apexcharts|frappe|uplot|dygraphs|recharts|nivo|victory|visx|reaviz"
)

RULES = {
    # ".ts", ".py": a bare extension
    "bare_extension": re.compile(rf"^\.({CODE_EXTENSIONS})$"),
    # "Next.js", "Node.js": a technology name with no folder
    "tech_name": re.compile(rf"^({TECH_NAMES})\.js$", re.IGNORECASE),
    # "src/**/*.ts", "{a,b}.ts": a glob pattern
    "glob": re.compile(r"[*?{}]"),
    # "<name>.ts", "dist/<app>/index.html": a placeholder.
    # Elided paths like "domain/.../Screen.kt" are kept: the suffix match usually finds the file.
    "placeholder": re.compile(r"[<>]"),
    # "7.6.F1.c", "1.1.c": a task number read as a file name
    "task_number": re.compile(r"^\d+\.\d+(\.[A-Za-z0-9]+)*\.[A-Za-z]$|^\d+(\.\d+)+$"),
    # "https://...": a URL
    "url": re.compile(r"://|^www\."),
}


def noise_rule(code_path):
    """Name of the first rule the path matches, or None if it looks like a real file."""
    if code_path is None:
        return None
    for name, pattern in RULES.items():
        if pattern.search(code_path):
            return name
    return None
