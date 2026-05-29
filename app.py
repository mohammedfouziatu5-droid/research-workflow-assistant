import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(page_title="Research Workflow Assistant", layout="wide")

st.title("Research Workflow Assistant")
st.write("Upload PDF research papers to extract key study information.")

# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(pdf_file):
text = ""

```
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted

return text
```


# -----------------------------
# SIMPLE INFORMATION EXTRACTORS
# -----------------------------
def extract_title(text):
    lines = text.split("\\n")
    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) > 0:
        return lines[0]

    return "Not Found"


def extract_year(text):
    year_match = re.search(r"(19|20)\\d{2}", text)

    if year_match:
        return year_match.group()

    return "Not Found"


def extract_authors(text):
    lines = text.split("\\n")

    possible_authors = []

    for line in lines[:10]:
        if "," in line or "and" in line:
            possible_authors.append(line)

    if possible_authors:
        return possible_authors[0]

    return "Not Found"


def extract_section(text, keywords):
    text_lower = text.lower()

    for keyword in keywords:
        pattern = rf"{keyword}(.*?)(introduction|methods|methodology|results|discussion|conclusion|references)"
        match = re.search(pattern, text_lower, re.DOTALL)

        if match:
            section_text = match.group(1).strip()

            section_text = re.sub(r"\\s+", " ", section_text)

            return section_text[:1000]

    return "Not Found"


# -----------------------------
# GAP IDENTIFIER LOGIC
# -----------------------------
def identify_gap(text):
    gap_keywords = [
        "limited studies",
        "few studies",
        "research gap",
        "little is known",
        "however",
        "lack of evidence",
        "no study",
        "scarce evidence",
        "future research",
        "this study addresses"
    ]

    sentences = re.split(r'(?<=[.!?]) +', text)

    possible_gaps = []

    for sentence in sentences:
        for keyword in gap_keywords:
            if keyword.lower() in sentence.lower():
                possible_gaps.append(sentence.strip())

    if possible_gaps:
        return " | ".join(possible_gaps[:3])

    return "No clear gap identified"


# -----------------------------
# MAIN PROCESSING
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    extracted_data = []

    with st.spinner("Processing PDFs..."):

        for pdf in uploaded_files:

            try:
                text = extract_text_from_pdf(pdf)

                title = extract_title(text)
                authors = extract_authors(text)
                year = extract_year(text)

                objectives = extract_section(
                    text,
                    ["objective", "objectives", "aim", "aims", "purpose"]
                )

                methods = extract_section(
                    text,
                    ["methods", "methodology"]
                )

                findings = extract_section(
                    text,
                    ["results", "findings"]
                )

                gaps = identify_gap(text)

                extracted_data.append({
                    "File Name": pdf.name,
                    "Title": title,
                    "Authors": authors,
                    "Year": year,
                    "Objectives": objectives,
                    "Methods": methods,
                    "Research Gaps": gaps,
                    "Findings": findings
                })

            except Exception as e:
                st.error(f"Error processing {pdf.name}: {e}")

    df = pd.DataFrame(extracted_data)

    st.subheader("Extracted Research Information")
    st.dataframe(df, use_container_width=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        label="Download Excel File",
        data=output.getvalue(),
        file_name="research_extraction_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload one or more PDF research papers to begin.")
