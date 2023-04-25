import numpy as np
import pandas as pd

path_csv = 'tabels/'

years = ['2023', '2022', '2022 (вне конкурса)', '2021', '2020', '2019'][::-1]

map_clusters = {
    ('Выезд', 'Экскурс'): 'Выезды',
    ('Другое',): 'Другое',
    ('Театр', 'Музыка', 'ЧГК', 'Танец', 'Вожатые', 'Огонь', 'Дебаты', 'Танцы'): 'Коллективы',
    ('Строй', 'Культура', 'Межкультурное'): 'Культура',
    ('Псих',): 'Психология',
    ('Спорт',): 'Спорт',
    ('ДФ', 'Бренд', 'Праздник'): 'Физтех'}


def statistics_by_big_clusters():
    """Создаёт таблицу вида (годы)x(большие кластеры)=сумма, потраченная на текущий год на данный большой кластер"""
    result_df = pd.DataFrame()
    for i, year in enumerate(years):
        result_df[year] = {big_cluster: 0 for big_cluster in map_clusters.values()}

    for year in years:
        # Поменяйте путь, если хотите использовать программу
        df = pd.read_csv(f"{path_csv + year}.csv")
        for i in range(len(df)):
            row = df.iloc[i]
            # Проверка на валидность строчки (иногда почему-то появляются строки полностью из nan-ов
            if np.isnan(row['Сумма']):
                continue
            # Ищем, к какому из больших кластеров на самом деле относится текущая студинициатива (ряд)
            this_big_cluster = None
            for clusters in map_clusters:
                if row['Кластер'] in clusters:
                    this_big_cluster = map_clusters[clusters]
                    break
            # Это проверка на то, что map_clusters учитывает все возможные кластеры
            if this_big_cluster is None:
                raise KeyError(f'Unknown cluster: {row}')
            result_df[year][this_big_cluster] += row['Сумма']
        # print(year, np.sum(result_df[year]))
    return result_df


def merge_2022(result_df):
    """костыль для объединения внеконкурсных с конкурсными"""
    result_df['2022'] += result_df['2022 (вне конкурса)']
    result_df.pop('2022 (вне конкурса)')
    years.remove('2022 (вне конкурса)')
    return result_df


def sort_by_cost_of_big_clusters(result_df):
    """сортировка по дороговизне кластеров"""
    result_df['total'] = 0
    for i, year in enumerate(years):
        result_df['total'] += result_df[year]
    result_df = result_df.sort_values('total', ascending=False)
    result_df.pop('total')
    return result_df

def make_ratios(result_df):
    """нормируем значения для указания долей"""
    for year in years:
        result_df[year] *= 100 / np.sum(result_df[year].values)
    return result_df

if __name__ == '__main__':
    result_df = statistics_by_big_clusters()
    result_df = merge_2022(result_df)
    result_df = sort_by_cost_of_big_clusters(result_df)

    result_df.to_excel('Big_clusters_merged_ratio.xlsx')
