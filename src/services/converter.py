import re
import os
import pandas as pd
import pdfplumber

from PyPDF2 import PdfReader

# 使ってみたけどうまくいかない
def extract_questions_to_excel(input_path, output_path):
    """
    PDFファイルから問題番号、問題文、選択肢を抽出し、Excelファイルに出力する関数。

    Parameters:
        input_path (str): 入力PDFファイルのパス
        output_path (str): 出力Excelファイルのパス
    """
    # PDFファイルからテキストを読み込む
    reader = PdfReader(input_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # 正規表現で問題番号、問題文、選択肢を抽出する
    question_pattern = re.compile(
        r"問\s*(\d+)\s*(.+?)\n(?:１．(.+?)\s*２．(.+?)\s*３．(.+?)\s*４．(.+?)\s*５．(.+?))\n",
        re.DOTALL
    )
    
    # データを格納するリスト
    data = []
    for match in question_pattern.finditer(text):
        question_number = match.group(1)
        question_text = match.group(2).strip()
        options = [match.group(i).strip() for i in range(3, 8)]
        data.append({
            "問題番号": question_number,
            "問題文": question_text,
            "選択肢1": options[0],
            "選択肢2": options[1],
            "選択肢3": options[2],
            "選択肢4": options[3],
            "選択肢5": options[4]
        })
    
    # データをDataFrameに変換
    df = pd.DataFrame(data)
    
    # Excelファイルに出力
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"データが正常に {output_path} に出力されました。")

# 使用例
# input_path = "academic_a_questions.pdf"
# output_path = "output.xlsx"
# extract_questions_to_excel(input_path, output_path)



def question_pdf_converter_to_excel(pdf_path, output_path):
    """
    PDFから問題番号、問題文、選択肢を抽出し、エクセルファイルに保存する関数。
    
    Args:
        pdf_path (str): PDFファイルのパス。
        output_path (str): 出力エクセルファイルのパス。
    """
    data = []

    # PDFを開く
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                print(f"デバッグ: ページ {page_number + 1} の解析開始")
                lines = text.split("\n")
                current_number = None
                current_question = None
                current_options = []

                for line in lines:
                    # 問題番号を検出
                    match = re.match(r"^問\s*(\d+)", line)
                    if match:
                        # 前の問題を保存
                        if current_number and current_question:
                            data.append({
                                "number": current_number,
                                "question": current_question,
                                "options": "\n".join(current_options)
                            })
                        # 現在の問題を更新
                        current_number = match.group(1)
                        current_question = line.split(" ", 1)[-1].strip()  # 問題文の開始部分
                        current_options = []  # 選択肢をリセット
                        print(f"デバッグ: 問題番号 {current_number} 検出")
                    # 選択肢を検出
                    elif re.match(r"^\s*\d+\.\s", line.strip()):
                        current_options.append(line.strip())
                        print(f"デバッグ: 選択肢検出 - {line.strip()}")

                # 最後の問題を保存
                if current_number and current_question:
                    data.append({
                        "number": current_number,
                        "question": current_question,
                        "options": "\n".join(current_options)
                    })

    # データをデータフレームに変換
    df = pd.DataFrame(data, columns=["number", "question", "options"])

    # エクセルに保存
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"エクセルファイルに変換完了: {output_path}")



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
