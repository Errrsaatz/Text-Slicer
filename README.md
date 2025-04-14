# Text Slicer

**Text Slicer** is a simple and powerful tool designed to split large text files into smaller parts based on the number of words.  
This allows you to manage large files efficiently and break them down into chunks that are easier to handle.

## Features

- **File Selection**: Choose the text file you want to split.
- **Output Folder**: Specify the output folder where the sliced files will be saved.
- **⚙Parameters**:
  - Set the **average number of words per file**.
  - Set the **maximum number of words per file**.
  - Define the **filename format** for the output files.
- **Options**:
  - **Preserve newlines**: Keep existing line breaks in the output files.
  - **Cut at next newline**: Split the text at the next newline after reaching the average word count.

## 💾 Installation

Clone the repository and install the required libraries:

```bash
git clone https://github.com/yourusername/text-slicer.git
cd text-slicer
pip install ttkbootstrap
