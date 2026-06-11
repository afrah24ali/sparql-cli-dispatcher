# sparql-cli-dispatcher
# SPARQL CLI Dispatcher

This project is a small command-line tool that maps fixed English intents to SPARQL queries and runs them against a Fuseki knowledge graph.

The tool uses the `publications.ttl` dataset from Module 9 Integration 9A. It supports a fixed vocabulary of English commands, then dispatches each command to the matching SPARQL query.

## Goal

The goal of this project is to demonstrate a simple natural-language-to-formal-query dispatcher.

Example:

```bash
python query.py "top 5 cited"
```

The command above maps the English intent `"top 5 cited"` to a SPARQL query that returns the top 5 most cited papers.

## Supported Intents

| English Intent                  | SPARQL Type | Description                                                |
| ------------------------------- | ----------- | ---------------------------------------------------------- |
| `list authors at NeurIPS`       | SELECT      | Lists authors who have papers published at NeurIPS         |
| `papers per topic`              | SELECT      | Counts papers grouped by topic                             |
| `top 5 cited`                   | SELECT      | Returns the top 5 papers by citation count                 |
| `any NeurIPS papers`            | ASK         | Checks whether the dataset contains any NeurIPS papers     |
| `construct 2023 authored graph` | CONSTRUCT   | Builds RDF triples connecting 2023 papers to their authors |

## How to Install

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Start Fuseki

Start the Fuseki container:

```bash
docker compose up -d
```

Upload the publications dataset:

```bash
curl -i -u admin:admin -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @data/publications.ttl \
  "http://localhost:3030/publications/data?default"
```

Check that the data was loaded:

```bash
curl -G \
  --data-urlencode "query=SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }" \
  http://localhost:3030/publications/query
```

## How to Run

Run an intent:

```bash
python query.py "top 5 cited"
```

Example output:

```text
http://aispire.example.org/publications/paper063    485
http://aispire.example.org/publications/paper043    475
http://aispire.example.org/publications/paper004    473
http://aispire.example.org/publications/paper007    470
http://aispire.example.org/publications/paper048    470
```

Run an ASK query:

```bash
python query.py "any NeurIPS papers"
```

Example output:

```text
True
```

Show the SPARQL query without running it:

```bash
python query.py "top 5 cited" --show-query
```

## How to Run Tests

Run:

```bash
python -m pytest -v
```

The tests verify that:

* at least five intents are supported
* each intent maps to the expected SPARQL structure
* SELECT, ASK, and CONSTRUCT queries are detected correctly
* `--show-query` prints the SPARQL query
* an unknown intent exits with a non-zero error

## Design Notes

This project does not use full natural-language understanding. It uses a fixed vocabulary dispatcher.

That means the user must type one of the supported English intents exactly. The program then looks up the matching SPARQL query and sends it to Fuseki.

This is a simple preview of how natural language can be reduced into a formal query in a knowledge graph system.
