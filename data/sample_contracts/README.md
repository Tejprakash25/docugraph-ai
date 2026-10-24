# Synthetic Contract Dataset

These documents are fictional, non-legal test data for DocuGraph AI. They do
not represent real organizations, people, contracts, legal advice, or usable
commercial terms. Do not send them to customers or use them as legal templates.

Each sample is intentionally detailed enough to exercise PDF parsing, chunking,
entity extraction, relationship extraction, graph indexing, and hybrid search.

Generate PDFs from the Markdown sources with:

```bash
python scripts/generate_sample_pdfs.py
```

The generated PDFs are written beside their source files and are ignored by
Git so that the repository keeps the editable synthetic sources as the source
of truth.
