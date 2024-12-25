from openpyxl import load_workbook

def write_to_excel(
    header: str,
    values: list[str|int],
    excel_path: str,
):
    # 既存のExcelファイルを読み込む
    workbook = load_workbook(excel_path)
    sheet = workbook.active  # 操作対象のシートを指定 (デフォルトでアクティブシート)

    # 次の空列を探す
    next_column = sheet.max_column + 1  # 現在の最大列の次の列を取得

    # 行に沿って書き込み
    sheet.cell(row=1, column=next_column, value=header)
    for row_index, value in enumerate(values, start=2):  # 行番号は2から始まる
        sheet.cell(row=row_index, column=next_column, value=value)

    # ファイルを保存
    workbook.save(excel_path)
    print(f"データを列 {next_column} に書き込みました。")
