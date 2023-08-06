from datetime import datetime
import intake
from tqdm import tqdm
import json


this_year = datetime.utcnow().year
this_month = datetime.utcnow().month

datetime_count = {}

cat = intake.open_catalog(
    "https://raw.githubusercontent.com/ContinuumIO/anaconda-package-data/master"
    "/catalog/anaconda_package_data.yaml"
)

for year in tqdm(range(2017, this_year+1)):
    for month in tqdm(range(1, 13)):
        try:
            df = cat.anaconda_package_data_by_month(
                year=year, month=month
            ).to_dask()
        except (IndexError, TypeError):
            break

        if len(df) == 0:
            print("year %d is missing!" % year, flush=True)
            continue

        datetime_count[(year, month)] = df.loc[
            (df.data_source == 'conda-forge')
        ]['counts'].sum().compute()

sdata = sorted(datetime_count.items(), key=lambda x: x[0][0]*12 + x[0][1])

data = {
    "month": str(sum(x[1] for x in sdata[-1:])),
    "year": str(sum(x[1] for x in sdata[-12:])),
    "all": str(sum(x[1] for x in sdata)),
}

print(data, flush=True)

with open("data/download_counts.json", "w") as fp:
    json.dump(data, fp, indent=2)
