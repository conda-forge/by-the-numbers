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
        except IndexError:
            break

        datetime_count[(year, month)] = df.loc[
            (df.data_source == 'conda-forge')
        ]['counts'].sum().compute()

data = {
    "month": 0,
    "year": 0,
    "all": 0,
}

for k, v in datetime_count.items():
    data["all"] += v
    if k[0] == this_year:
        data["year"] += v

    if k[0] == this_year and k[1] == this_month:
        data["month"] += v


print(data, flush=True)

with open("data/download_counts.json", "w") as fp:
    json.dump(data, fp, indent=2)
