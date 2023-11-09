import logging
import pandas as pd


class DataPreprocessor:
    def __init__(self, path_to_data):
        self._path_to_data = path_to_data

    def make_docs(self, mode='csv'):
        data = self.load_data(mode)
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"],  # Split character (default \n\n)
            chunk_size=2000,
            chunk_overlap=0,
            length_function=len,
            keep_separator=False
        )
        splits = splitter.split_text(data)
        return splits

    def load_data(self, mode='csv'):
        try:
            logging.info("Читаем файл")
            data = list()
            if mode == 'csv':
                df = pd.read_csv(str(self._path_to_data), delimiter=';')
            elif mode == 'excel':
                df = pd.read_excel(str(self._path_to_data))
            for ind, row in df.iterrows():
                tmp = list()
                for col in df.columns[0:]:
                    tmp.append(f"{col}  :  {row[col]} ")
                data.append(tmp)
            data = [x for x in data if len(x) > 2]
            header = list()
            chunks = list()
            for chunk in data:
                for elem in chunk:
                    header.append(elem.split('  :  ')[0])
            for elem in data:
                length = len(' '.join(elem))
                if length > 2000:
                    tmp = elem[2].split('  :  ')[1]
                    splitted = [tmp[start:min(len(tmp) - 1, start + 2000)] for start in
                                range(0, len(tmp), 2000)]
                    for ch in splitted:
                        chunk = elem
                        chunk[2] = header[2] + '  :  ' + ch
                        chunks.append('\n'.join(chunk))
                else:
                    chunks.append('\n'.join(elem))
            csv_data = '\n\n'.join(chunks)
        except Exception as e:
            logging.error("Ошибка при чтении файла")
            csv_data = []
        finally:
            return csv_data
