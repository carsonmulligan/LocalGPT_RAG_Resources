"""
download_survival_refs.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Grab every PDF referenced in *survival_agent_system_prompts.json* and
store them in a local `pdfs/` folder.

Usage
-----
$ python download_survival_refs.py         # downloads everything
$ python download_survival_refs.py --dir /path/to/save/pdfs
"""

import os
import argparse
import pathlib
import urllib.parse
import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# 1)  All the PDF links (duplicates removed, “#page” anchors stripped).
#     If you add more refs later, just extend this list.
# ---------------------------------------------------------------------------
PDF_URLS = [
    # Wilderness / fire / shelter / hygiene
    "https://archive.org/download/Fm21-76SurvivalManual/FM21-76_SurvivalManual.pdf",
    "https://irp.fas.org/doddir/army/fm3-05-70.pdf",

    # Hunting / game handling
    "https://www.bits.de/NRANEU/others/amd-us-archive/Fm21-75_15%2884%29.pdf",

    # Fishing
    "https://www.dnr.sc.gov/fish/pdf/fishingguide1.pdf",
    "https://www.nj.gov/dep/fgw/pdf/basicfishingbook.pdf",

    # Knots
    "https://sossepic.weebly.com/uploads/1/3/2/1/13211340/six_boy_scout_knots.pdf",
    "https://cubsource.org/Step_By_Step_Basic_Knots.pdf",

    # First-Aid
    "https://safetytrainingpros.com/wp-content/uploads/2015/10/American-Red-Cross-First-Aid-CPR-AED-Participants-Manual.pdf",

    # Go-bag
    "https://www.ready.gov/sites/default/files/2021-02/ready_checklist.pdf",
    "https://www.redcross.org/content/dam/redcross/atg/Chapters/Division_1_-_Media/Denver/Denver_-_PDFs/EmergencyPreparednessChecklist.pdf",

    # Trapping appendix (same FM 3-05.70 already in list)

    # Plant ID & Foraging
    "https://truthbrary.mpaq.org/BOOKS/Homesteading%20-%20Survival%20-%20Self-Sufficiency%20%28Books%29/Edible%20Wild%20Plants/The_Complete_Guide_to_Edible_Wild_Plants_-_Department_of_the_Army.pdf",

    # Dog training
    "https://cinotecniamilitar.files.wordpress.com/2015/02/fm20_20_1960.pdf",
    "https://irp.fas.org/doddir/army/fm3-19-17.pdf",

    # Old-car maintenance
    "https://transportation.wv.gov/highways/training/TrainingDocuments/Crawfords_Auto_Repair_Guide.pdf",
    "https://www.cartalk.com/sites/default/files/features/jumpstart/images/jumpstart.pdf",

    # Battery re-use
    "https://www.odysseybattery.com/wp-content/uploads/2020/05/ODYSSEY_Battery_Reconditioning_Charge_Procedure.pdf",
    "https://www.qsl.net/y/yo4tnv/docs/BatteryReconditioning.pdf",

    # Solar basics
    "https://www.lg.com/us/solar/solar/files/resources/Beginner-s-Guide_Ver20_01082020.pdf",
    "https://web.pdx.edu/~rueterj/courses/ESM342-solar/WK3-GE-MC3-PVintro.pdf",

    # Forest art
    "https://www.forestryengland.uk/sites/default/files/documents/Forestry%20England_Arts%20Material_Lesson%20Plan.pdf",
    "https://www.countrysideclassroom.org.uk/storage/resource/downloads/e8137741-d25a-442e-a658-8149993cf1aa/original/outdoor-art-natural-connections.pdf",
]

# ---------------------------------------------------------------------------
# 2)  Helpers
# ---------------------------------------------------------------------------

def nice_filename(url: str) -> str:
    """
    Turn a URL into a sane local filename.
    Keeps the original basename but strips query-strings / fragments.
    """
    parsed = urllib.parse.urlparse(url)
    base = os.path.basename(parsed.path)
    return base or "download.pdf"

def download(url: str, dest_folder: pathlib.Path, chunk_size: int = 8192) -> None:
    """
    Stream-download the file at *url* into *dest_folder* with a progress bar.
    Skips download if file already exists.
    """
    filename = nice_filename(url)
    dest = dest_folder / filename
    if dest.exists():
        print(f"✔ Already downloaded: {filename}")
        return

    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            with open(dest, "wb") as f, tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=filename,
            ) as bar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive packets
                        f.write(chunk)
                        bar.update(len(chunk))
        print(f"✔ Saved to {dest}")
    except Exception as e:
        print(f"✖ Failed to download {url}\n  ↳ {e}")

# ---------------------------------------------------------------------------
# 3)  CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Download survival reference PDFs.")
    parser.add_argument(
        "--dir",
        "-d",
        default="pdfs",
        help="Directory where PDFs will be saved (default: ./pdfs)",
    )
    args = parser.parse_args()

    dest_folder = pathlib.Path(args.dir).expanduser()
    dest_folder.mkdir(parents=True, exist_ok=True)

    print(f"Saving PDFs to: {dest_folder.resolve()}\n")

    for url in PDF_URLS:
        # Strip off any “#page=…” anchors in case they exist
        clean_url = url.split("#")[0]
        download(clean_url, dest_folder)

    print("\nAll done! 🎉")


if __name__ == "__main__":
    main()
