"""Download publicly available IRDAI-filed health insurance policy wordings."""

import pathlib
import requests

BASE = "https://irdai.gov.in/documents/37343/931203"

DOCUMENTS = {
    "sbi_superhealth": "/SBIHLIP23050V012223.pdf/de34fc22-e5b0-d313-41b1-9bcd4243d600?version=1.0&t=1669351245742&download=true",
    "hdfcergo_optima_restore": "/APOHLIP20106V051920_2019-2020.pdf/98914a3f-33dc-7b44-b67a-6b65386590b5?version=1.1&t=1668513370722&download=true",
    "futuregenerali_health_suraksha": "/FGIHLIP21156V022021_2020-2021.pdf/9d3df075-c8ee-3981-324e-7ad9fa3aec10?version=1.1&t=1668579067754&download=true",
    "futuregenerali_group_health": "/FGIHLGP21165V022021_2020-2021.pdf/31b9b937-4dbc-ddda-b33d-d0195eafdf4b?version=1.1&t=1668578906592&download=true",
    "unitedindia_group_health": "/UIIHLGP21226V022021_2020-2021.pdf/3761fa7d-ef8c-7d8d-2b7a-2dd44eb41f25?version=1.1&t=1668590224936&download=true",
    "bajaj_health_total": "/Health+Total.pdf/1686e404-21d0-da0a-e815-8d1c2e52bc5c?version=1.1&t=1668923517128&download=true",
    "carehealth_group": "/CHIHMGP22132V012122_HEALTH2083.pdf/b5c15df2-8a5a-5927-10d8-c3d136055139?version=1.1&t=1668769248703&download=true",
    "adityabirla_group_activ": "/ABHI_GroupActivHealth_2016-2017.pdf/71c8aec7-4623-33be-20ed-25749ede61c2?version=1.1&t=1668411840253&download=true",
    "kotak_health_care": "/KMGIC+-+Health+Care_2015-2016.pdf/eff58f68-ccde-7764-1d3a-305beb113442?version=1.1&t=1668408839058&download=true",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def main() -> None:
    raw_dir = pathlib.Path(__file__).parents[1] / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for stem, suffix in DOCUMENTS.items():
        dest = raw_dir / f"{stem}.pdf"
        if dest.exists():
            print(f"skip  {stem}.pdf (already exists)")
            continue

        url = BASE + suffix
        try:
            response = requests.get(url, headers=HEADERS, timeout=90)
            response.raise_for_status()
            body = response.content
            if not body.startswith(b"%PDF"):
                print(f"WARN  {stem}.pdf — response is not a PDF, skipping")
                continue
            dest.write_bytes(body)
            print(f"saved {stem}.pdf ({len(body) // 1024} KB)")
        except Exception as exc:
            print(f"FAIL  {stem}.pdf — {exc}")


if __name__ == "__main__":
    main()
