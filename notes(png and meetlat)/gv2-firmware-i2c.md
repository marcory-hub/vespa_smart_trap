**One-line purpose:** script to generate json with information from books
**Short summary:** _has to be updated after metadata is added to the markdown files_
**Agent:** user notes
**Main Index:** [[__cookbookIO]]


---


```sh
./.venv/bin/python scripts/sync_extracted_book_metadata.py
```

```sh
./.venv/bin/python scripts/sync_extracted_book_metadata.py \
  --md-dir data/extracted/markdown-clean2 \
  --output-dir data/extracted/metadata
```
---

to update context from pdf
```sh
.venv/bin/python scripts/generate_book_context.py --combined
```
-- combined make one file with all books
without generated per book a json with the title of the book

---

- [How to prepare data for LLMs](https://youtu.be/eihYrX7F7as)
structured and unstructured data

