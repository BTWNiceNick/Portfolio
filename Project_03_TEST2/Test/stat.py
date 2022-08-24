import pandas as pd

df = pd.read_csv(f'LearningInPublic/Python/Project_03_TEST/Test/report.csv')
print(df)

df.to_excel(f'LearningInPublic/Python/Project_03_TEST/Test/stats.xlsx')
