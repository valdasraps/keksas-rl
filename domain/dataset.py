import pandas as pd


class Dataset:

    def __init__(self, csv_file: str, ema_lengths: list[int]) -> None:
        self._data = Dataset._make_cache(csv_file, ema_lengths)
        self._i = -1

    def reset(self) -> None:
        self._i = -1

    def step(self) -> pd.Series | None:
        self._i += 1
        if self._i >= len(self._data):
            return None
        return self._data.iloc[self._i]

    @staticmethod
    def _make_cache(csv_file: str, ema_lengths: list[int]) -> pd.DataFrame:
        data = pd.read_csv(csv_file)
        data.index = pd.to_datetime(data.timestamp).rename('index')
        data.drop(columns=['timestamp'], inplace=True)

        column_names = ['close']
        for ema_length in ema_lengths:
            column_name = f'ema_{ema_length}'
            column_names.append(column_name)
            data[column_name] = data.close.ewm(span=ema_length).mean()
        first_start = max(ema_lengths) * 5
        return data[column_names].iloc[first_start:].copy()
