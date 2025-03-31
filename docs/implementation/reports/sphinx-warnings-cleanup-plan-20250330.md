# Sphinx Build Warnings Cleanup Plan - 2025-03-30

**Status:** The Sphinx build (`make -C config/sphinx html`) currently succeeds locally, but generates numerous warnings (182 reported in the last log). The critical `autodoc` import errors have been resolved.

**Objective:** Eliminate the remaining warnings to ensure clean documentation generation.

**Analysis of Remaining Warnings (Based on 9:17 PM Log):**

The warnings fall into several categories:

1.  **RST Formatting Errors in `.rst` Files:**

    - **Issue:** `Title underline too short.`
    - **Files:** `index.rst`, `modules/adaptive.rst`, `modules/morphisms.rst`, `modules/scheduler.rst`, `modules/temporal.rst`.
    - **Pattern:** Section titles (e.g., `Core Modules`, `Adaptive Module`) have underlines (`---`, `===`) that are shorter than the text length.
    - **Fix:** Manually extend the underline characters to be at least as long as the title text above them.

2.  **RST Formatting Errors in Docstrings (Primarily `src/python/agent_temporal.py`):**

    - **Issue:** `Title underline too short.`
    - **Pattern:** Same as above, but for section titles _within_ docstrings (e.g., `Parameters:`, `Returns:`, `Examples:`).
    - **Fix:** Manually extend underlines within the docstrings in the Python source file.
    - **Issue:** `ERROR: Unexpected indentation.`
    - **Pattern:** Lists, code blocks, or paragraphs within docstrings are not indented correctly relative to the surrounding docstring text or RST directives. RST requires strict and consistent indentation (usually multiples of standard spaces).
    - **Fix:** Manually review and correct indentation within the affected docstrings in the Python source file. Ensure blank lines correctly separate blocks where needed.
    - **Issue:** `WARNING: Block quote ends without a blank line; unexpected unindent.`
    - **Pattern:** RST requires blank lines around certain blocks (like lists, code examples, block quotes). This warning indicates a missing blank line is causing parsing ambiguity.
    - **Fix:** Add necessary blank lines within the affected docstrings.
    - **Issue:** `WARNING: Inline substitution_reference start-string without end-string.` / `ERROR: Undefined substitution referenced: "..."`
    - **Pattern:** Using RST substitutions (`|name|`) without defining them (`.. |name| replace:: ...`) or having malformed substitution syntax. Could also be misinterpreted LaTeX math.
    - **Fix:** Review the indicated lines in the docstrings. If substitutions are intended, define them. If it's math, ensure it's correctly formatted (e.g., using `\:math:\`role\` or math blocks). The specific error `Undefined substitution referenced: "tau_2|_{U_n}"` needs fixing in the `time_difference` docstring.
    - **Issue:** `WARNING: Inline strong start-string without end-string.`
    - **Pattern:** Malformed bold text syntax, likely a missing closing `**`.
    - **Fix:** Find the incomplete bold markup and add the closing `**`.

3.  **Duplicate Object/Target Warnings:**

    - **Issue:** `WARNING: duplicate object description of python.agent_temporal... other instance in modules/morphisms...`
    - **Pattern:** The same Python object (module, class, method) is being documented by `automodule` or similar directives in multiple `.rst` files, leading to duplicate entries in the documentation index.
    - **Fix:** Add the `:no-index:` option to the `automodule` directive in the `.rst` file where the documentation is considered secondary (we already did this for `morphisms.rst` regarding `agent_temporal`, but other duplicates might exist).
    - **Issue:** `WARNING: Duplicate explicit target name: "temporal universe"` (and others)
    - **Pattern:** An explicit hyperlink target (e.g., `.. _temporal universe:`) is defined with the same name in multiple places within the processed documentation (could be in different docstrings or `.rst` files). Target names must be unique across the entire project.
    - **Fix:** Review the docstrings in `agent_temporal.py` and potentially other files. Rename duplicate targets to make them unique (e.g., `_temporal universe_def:`, `_temporal universe_ref1:`).

4.  **Broken Links/References:**
    - **Issue:** `WARNING: unknown document: '../../docs/theory/index'` in `index.rst`.
    - **Pattern:** The path used in a `:doc:` role or `toctree` directive points to a file that doesn't exist relative to the current file or isn't included in the Sphinx source directory structure.
    - **Fix:** Correct the path in `config/sphinx/index.rst` to accurately point to the intended theory index document relative to the `config/sphinx/` directory. It might need to be `../theory/index` if `docs/theory/index.md` (or `.rst`) exists and is meant to be included. Alternatively, remove the link if it's incorrect.
    - **Issue:** `WARNING: failed to reach any of the inventories... FileNotFoundError: .../_build/theory/objects.inv`
    - **Pattern:** `intersphinx` is configured in `conf.py` to link to another Sphinx project ('theory'), but the specified inventory file path is incorrect or the 'theory' project hasn't been built yet.
    - **Fix:** Either ensure the 'theory' documentation is built first and the path in `conf.py`'s `intersphinx_mapping` is correct, or remove the 'theory' mapping from `intersphinx_mapping` if cross-linking isn't required currently.

**Proposed Cleanup Strategy:**

1.  **Fix `.rst` Structural Errors:**
    - Correct remaining `Title underline too short` warnings in `index.rst` and `modules/*.rst`.
    - Correct the `unknown document` path in `index.rst`.
    - Address any remaining `Unexpected indentation` errors in the `.rst` files (check commented-out sections).
2.  **Fix Duplicate Object Warnings:**
    - Identify any remaining `duplicate object description` warnings in the build log.
    - Add the `:no-index:` option to the less important `automodule` directive causing the duplicate.
3.  **Manual Docstring Cleanup (User Task):**
    - **Focus File:** `src/python/agent_temporal.py`.
    - **Actions:** Systematically go through the docstrings in this file, fixing all reported RST formatting warnings (`Title underline too short`, `Unexpected indentation`, `Block quote ends...`, `Inline substitution...`, `Inline strong...`, `Duplicate explicit target name`, `Undefined substitution...`). Use a local editor with RST linting/preview if possible.
4.  **Final Build & Review:**
    - Run `make -C config/sphinx html` locally again after the manual cleanup.
    - Address any minor remaining warnings.
    - Ignore or configure the `intersphinx` warning as desired.

This approach prioritizes structural fixes and then allows for focused manual cleanup of the detailed docstring formatting issues.
