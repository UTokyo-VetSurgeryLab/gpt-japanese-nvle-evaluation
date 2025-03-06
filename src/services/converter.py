import datetime
import re
import os
import pandas as pd
import pdfplumber


# これを使う
def question_pdf_converter_to_excel_test(
    path: str,
    is_test:bool = True,
):
    """
    PDFから問題番号、問題文、選択肢を抽出し、エクセルファイルに保存する関数。
    
    Args:
        path (str): 入力元や出力先となるフォルダ
        is_test (bool): testとしてconverterを使用しているか。その際に同じ出力ファイルとなってしまうと
                        以前の記録が上書きされてしまうため、この引数を設けて防ぐ
    """
    data = []
    common_question_sentences = []
    
    dt_now = datetime.datetime.now()
    now = dt_now.strftime('%Y%m%d_%H%M')
    
    if is_test:
        pdf_path = f'{path}/questions.pdf'
        output_path = f'{path}/questions_{now}.xlsx'
        academic_d_common_question_file_path = f'{path}/questions_common_sentence_{now}.xlsx'
    else:
        pdf_path = f'{path}/questions.pdf'
        output_path = f'{path}/questions.xlsx'
        academic_d_common_question_file_path = f'{path}/questions_common_sentence.xlsx'
    
    alp_options = {'a', 'b', 'c', 'd', 'e'}

    # Re-process the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[1:]:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                question_texts, options, common_question_text =[], [], []
                #in_question = False
                is_option = False

                for line in lines:
                    # Detect question start
                    if line.startswith('問'):
                        # If a question was already being processed, save it before starting a new one
                        if question_texts and options:
                            data.append(r:=(len(data)+1, "".join(question_texts), " ".join(options)))
                            print(f'question_texts:{question_texts}')
                        elif common_question_text:
                            common_question_sentences.append((len(common_question_sentences)+1, "".join(common_question_text[1:])))
                        
                        # Start a new question
                        question_head_text = line.strip().lstrip('問').lstrip()
                        r = re.match(r"^\d+", question_head_text)
                        question_modified_head_text = question_head_text[len(r.group(0)):]
                        question_texts = [question_modified_head_text.strip().replace('\n', '')]
                        options = []
                        #in_question = True
                        is_option = False
                    
                    # Collect options
                    #elif in_question and line.strip() and line[0].isdigit():
                    elif line.strip() and line[0].isdigit():
                        l_striped = line.strip()
                        if len(l_striped) > 4:
                            options.append(l_striped)
                            is_option = True
                        else:
                            for ch in l_striped:
                                if not ch.isdigit():
                                    options.append(l_striped)
                                    break
                                
                    
                    elif line.strip() and line[0] in alp_options:
                        question_texts.append(" ")
                        question_texts.append(line.replace('\n', '').strip())
                    else:
                        print(line)
                        if line[0] == "〰":
                            continue
                        if line[:2] == "別冊":
                            continue
                        if line[0] == '図':
                            continue
                        if line[0] == '表':
                            continue
                        if question_texts and is_option:
                            options.append(line)
                        elif is_option:
                            common_question_text.append(line.replace('\n', '').strip())
                        else:
                            question_texts.append(line.replace('\n', '').strip())
                    
                    # End of question block if no more options and empty lines
                    #elif in_question and not line.strip() and options:
                    #    in_question = False
                        
                # Append last question on the page if any
                if question_texts and options:
                    data.append((len(data)+1, "".join(question_texts), "\n".join(options)))

    df_question = pd.DataFrame(data, columns=["number", "question", "options"])
    df_question.to_excel(output_path, index=False, engine="openpyxl")
    
    if common_question_sentences:
        df_academic_d_common_sentence = pd.DataFrame(common_question_sentences, columns=["number", "question"])
        df_academic_d_common_sentence.to_excel(academic_d_common_question_file_path, index=False, engine="openpyxl")
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
