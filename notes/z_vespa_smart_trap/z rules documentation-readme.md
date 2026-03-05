
**One-line purpose:** cursor rules for documentation
**Short summary:** audience, tone and style, doc types, writing approach, format guidelines
**Agent:** can be used as template for current project

---


### Audience

The README.md is made for the github repository. This user documentation must be written for non-technical users — especially **beekeepers** with no prior knowledge of vespCV, Raspberry Pi, or computer vision. The language must be simple, avoiding assumptions about technical literacy.

### Tone and Style

- Friendly and clear — avoid jargon or acronyms. If a technical term is absolutely necessary, it must be explained immediately in plain, simple language, or defined in the Glossary.
- Use short, concise sentences.
- Employ bullet points, numbered lists, and clear headings to break down information.
- Prefer step-by-step instructions over abstract descriptions, using a "do this, then this" approach.
- Include visual aids like images and diagrams where helpful to illustrate concepts or steps.

### Documentation Types

Cursor should help create and review the following documents. For each, focus on the user's practical needs and common questions:

1.  **Install Instructions**
    * Comprehensive step-by-step guide covering the entire setup process, from installing the OS on a Raspberry Pi to achieving the first successful detection.
    * Explicitly include details on hardware wiring, powering up the device, and how to verify and view results.
    * **Focus on exact commands, specific file paths, and expected outputs at each stage.**

2.  **Usage Guide**
    * **Basic Usage:**
        * Clear instructions on how to start the vespCV application.
        * Guidance on interacting with and understanding the user interface (e.g., "What does this button do?", "Where do I see the detections?").
    * **Using the Raspberry Pi Remotely** with Raspberry Pi Connect:
        * Step-by-step setup and usage for accessing the Pi from another device.
    * **Advanced Configuration:**
        * How to customize the application through the `config.yaml` file (e.g., "how to change detection sensitivity," "how to set up notifications"). Explain each configurable parameter in simple terms.
    * **Troubleshooting (Basic):**
        * Initial steps for common, easy-to-resolve user issues.

3.  **Maintenance and Troubleshooting (Advanced)**
    * Address common problems users might encounter (e.g., "nothing is showing on the screen," "detections are not accurate," "the device is slow").
    * Provide clear instructions on how to check logs, safely restart the application or Raspberry Pi, and manage storage (e.g., "how to delete old detection files to free up space").
    * **Emphasize safety and preventing data loss or system corruption.**

4.  **Glossary**
    * Define all technical terms, acronyms, and project-specific jargon (e.g., YOLO, Raspberry Pi, vespCV, detection, inference, SSH, GPIO, `.yaml` file).
    * Each definition should be concise and in plain language, directly relevant to the beekeeper's understanding of the system.

### Writing Approach

-   Documentation should be written **alongside development**, not after. This ensures accuracy and currency.
-   For each new feature, modification, or observed behavior, include or update a user-facing explanation immediately.
-   When writing user documentation, always ask: *"Would a beekeeper with no tech background understand this? Is it actionable?"*
-   When writing documentation for contributors, always ask: *"Would a contributor to the repository with limited *prior* tech background (but capable of learning) understand this? Is it clear, concise, and accurate?"* (This clarifies "little tech background" to mean less familiar with *this specific project* but generally capable of programming).

### Format Guidelines

-   Use Markdown for all user-facing documentation files.
-   Maintain one main `README.md` for the GitHub repository, providing a high-level overview and clear links to all specific guides (e.g., Installation, Usage, Troubleshooting).
-   Keep all screenshots, diagrams, and visual aids organized in a dedicated `/doc/images/` folder within the repository.
-   **Ensure all file paths and commands provided in the documentation are accurate and copy-paste friendly.**

---