from __future__ import annotations

import argparse
from typing import Dict, Optional

import requests


FUSEKI_QUERY_URL = "http://localhost:3030/publications/query"

PREFIXES = """
PREFIX : <http://aispire.example.org/publications/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


INTENT_TO_QUERY: Dict[str, str] = {
    "list authors at NeurIPS": PREFIXES + """
SELECT DISTINCT ?author
WHERE {
  ?paper a :Paper ;
         :publishedIn :NeurIPS ;
         :authoredBy ?author .
}
ORDER BY ?author
""",

    "papers per topic": PREFIXES + """
SELECT ?topic (COUNT(?paper) AS ?count)
WHERE {
  ?paper a :Paper ;
         :hasTopic ?topic .
}
GROUP BY ?topic
ORDER BY DESC(?count)
""",

    "top 5 cited": PREFIXES + """
SELECT ?paper ?cc
WHERE {
  ?paper a :Paper ;
         :citationCount ?cc .
}
ORDER BY DESC(?cc)
LIMIT 5
""",

    "any NeurIPS papers": PREFIXES + """
ASK
WHERE {
  ?paper a :Paper ;
         :publishedIn :NeurIPS .
}
""",

    "construct 2023 authored graph": PREFIXES + """
CONSTRUCT {
  ?paper :authoredBy ?author .
}
WHERE {
  ?paper a :Paper ;
         :year 2023 ;
         :authoredBy ?author .
}
""",
}


def supported_intents() -> list[str]:
    """Return all supported English intents."""
    return sorted(INTENT_TO_QUERY.keys())


def get_query(intent: str) -> str:
    """Return the SPARQL query for a fixed English intent."""
    if intent not in INTENT_TO_QUERY:
        supported = "\n".join(f"- {item}" for item in supported_intents())
        raise ValueError(
            f"Unknown intent: {intent}\n\nSupported intents:\n{supported}"
        )

    return INTENT_TO_QUERY[intent]


def query_type(sparql: str) -> str:
    """Detect SELECT, ASK, or CONSTRUCT after PREFIX declarations."""
    body_lines = []
    for line in sparql.splitlines():
        stripped = line.strip()
        if not stripped.upper().startswith("PREFIX") and stripped:
            body_lines.append(stripped)

    body = "\n".join(body_lines).upper()

    if body.startswith("ASK"):
        return "ASK"
    if body.startswith("CONSTRUCT"):
        return "CONSTRUCT"
    return "SELECT"


def run_sparql(sparql: str) -> str:
    """Run SPARQL against Fuseki and return printable output."""
    qtype = query_type(sparql)

    accept = "text/turtle" if qtype == "CONSTRUCT" else "application/sparql-results+json"

    response = requests.post(
        FUSEKI_QUERY_URL,
        data={"query": sparql},
        headers={"Accept": accept},
        timeout=15,
    )
    response.raise_for_status()

    if qtype == "CONSTRUCT":
        return response.text.strip()

    data = response.json()

    if qtype == "ASK":
        return str(data.get("boolean"))

    variables = data["head"]["vars"]
    rows = data["results"]["bindings"]

    output_lines = []
    for row in rows:
        values = []
        for var in variables:
            if var in row:
                values.append(row[var]["value"])
            else:
                values.append("")
        output_lines.append("\t".join(values))

    return "\n".join(output_lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dispatch fixed English intents to SPARQL queries."
    )

    parser.add_argument(
        "intent",
        help="Supported intent, for example: 'top 5 cited'",
    )

    parser.add_argument(
        "--show-query",
        action="store_true",
        help="Print the SPARQL query without running it.",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        sparql = get_query(args.intent)
    except ValueError as error:
        parser.error(str(error))

    if args.show_query:
        print(sparql.strip())
        return 0

    print(run_sparql(sparql))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())