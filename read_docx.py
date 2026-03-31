import zipfile
import xml.etree.ElementTree as ET
import sys
import io

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            texts = []
            # Find paragraphs
            for p in tree.findall('.//w:p', namespaces):
                p_text = []
                for t in p.findall('.//w:t', namespaces):
                    if t.text:
                        p_text.append(t.text)
                if p_text:
                    texts.append(''.join(p_text))
            
            # encode safely
            sys.stdout.buffer.write('\n'.join(texts).encode('utf-8'))
    except Exception as e:
        sys.stderr.write(f"Error: {e}")

if __name__ == '__main__':
    read_docx(sys.argv[1])
