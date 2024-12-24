import re
import os
import pandas as pd
import pdfplumber

# これを使う
def question_pdf_converter_to_excel_test(pdf_path, output_path):
    """
    PDFから問題番号、問題文、選択肢を抽出し、エクセルファイルに保存する関数。
    
    Args:
        pdf_path (str): PDFファイルのパス。
        output_path (str): 出力エクセルファイルのパス。
    """
    data = []
    
    alp_options = {'a', 'b', 'c', 'd', 'e'}

    # Re-process the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                question_texts, options = [], []
                #in_question = False

                for line in lines:
                    # Detect question start
                    if line.startswith('問'):
                        # If a question was already being processed, save it before starting a new one
                        if question_texts and options:
                            data.append((len(data)+1, "\n".join(question_texts), "\n".join(options)))
                        
                        # Start a new question
                        question_head_text = line.strip().lstrip('問').lstrip()
                        r = re.match(r"^\d+", question_head_text)
                        question_modified_head_text = question_head_text[len(r.group(0)):]
                        question_texts = [question_modified_head_text.strip()]
                        options = []
                        #in_question = True
                    
                    # Collect options
                    #elif in_question and line.strip() and line[0].isdigit():
                    elif line.strip() and line[0].isdigit():
                        l_striped = line.strip()
                        if len(l_striped) > 4:
                            options.append(l_striped)
                        else:
                            for ch in l_striped:
                                if not ch.isdigit():
                                    options.append(l_striped)
                                    break
                                
                    
                    elif line.strip() and line[0] in alp_options:
                        question_texts.append(line)
                    else:
                        print(line)
                    
                    # End of question block if no more options and empty lines
                    #elif in_question and not line.strip() and options:
                    #    in_question = False
                        
                # Append last question on the page if any
                if question_texts and options:
                    data.append((len(data)+1, "\n".join(question_texts), "\n".join(options)))

    # データをデータフレームに変換
    df = pd.DataFrame(data, columns=["number", "question", "options"])

    # エクセルに保存
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"エクセルファイルに変換完了!: {output_path}")




sections = {
    "必須問題": "essential_answers.xlsx",
    "学説Ａ": "academic_a_answers.xlsx",
    "学説Ｂ": "academic_b_answers.xlsx",
    "実地Ｃ": "practical_c_answers.xlsx",
    "実地Ｄ": "practical_d_answers.xlsx",
}


def answer_pdf_converter_to_excel(pdf_path, output_path, sections=sections):
    # セクションごとのデータを格納する辞書
    section_data = {key: [] for key in sections.keys()}

    # セクション検出用の正規表現パターン
    section_patterns = {
        "必須問題": r"必須問題",
        "学説Ａ": r"学説Ａ|学説A",
        "学説Ｂ": r"学説Ｂ|学説B",
        "実地Ｃ": r"実地Ｃ|実地C",
        "実地Ｄ": r"実地Ｄ|実地D",
    }

    # PDFを読み込み
    with pdfplumber.open(pdf_path) as pdf:
        current_sections = []  # 現在のセクションを複数管理
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                print(f"デバッグ: ページ {page_number + 1} のテキストを解析中")
                lines = text.split("\n")
                for line in lines:
                    # 複数のセクションが記載されている場合を検出
                    detected_sections = [section for section, pattern in section_patterns.items() if re.search(pattern, line)]
                    if detected_sections:
                        current_sections = detected_sections
                        print(f"デバッグ: ページ {page_number + 1} でセクション {current_sections} を検出")
                        continue
                    
                    # 問題番号と正答を抽出
                    if current_sections and re.match(r"問\d+", line):
                        parts = line.split()
                        if len(parts) >= 2:
                            question_number = parts[0].replace("問", "")
                            answer = parts[1]
                            for section in current_sections:
                                section_data[section].append({"number": question_number, "answer": answer})

    # 出力フォルダが存在しない場合は作成
    os.makedirs(output_path, exist_ok=True)

    # 各セクションをExcelファイルに書き出し
    for section, data in section_data.items():
        if data:
            df = pd.DataFrame(data)
            section_file_path = os.path.join(output_path, sections[section])
            df.to_excel(section_file_path, index=False, engine="openpyxl")
            print(f"出力完了: {section_file_path}")
        else:
            print(f"警告: {section} にデータがありませんでした。")
