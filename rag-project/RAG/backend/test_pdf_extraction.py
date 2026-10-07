from pypdf import PdfReader

pdf_path = r"knowledge/aws-security-incident-response-guide.pdf"
reader = PdfReader(pdf_path)

print("PDF:", pdf_path)
print("Total pages:", len(reader.pages))

text = ""

for page in reader.pages:
    text += page.extract_text() or ""

print("Characters:", len(text))
print("Words:", len(text.split()))

print("\n--- EXTRACTED TEXT ---")
print(text[:2000])